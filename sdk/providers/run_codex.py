"""
Codex adapter (localhost-first).

Bridges user I/O with the membrane inject bus:
- User input -> codex stdin + `membrane.inject(channel=ui.action.user_prompt)`
- Codex stdout/stderr -> console + `membrane.inject(channel=provider.codex.output)`

This is a lightweight wrapper meant for dev runs. For production use, prefer
running through the Sidecar once signature management is centralised.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import datetime as dt
import json
import os
import sys
import uuid
from typing import Iterable, List, Optional

import websockets  # type: ignore[import]


def utc_ts() -> str:
    return dt.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


def build_envelope(
    *,
    org: str,
    channel: str,
    origin: str,
    payload: dict,
    ttl_frames: int = 900,
    dedupe_key: Optional[str] = None,
) -> dict:
    return {
        "v": "1.1",
        "type": "membrane.inject",
        "org": org,
        "id": str(uuid.uuid4()),
        "ts": utc_ts(),
        "scope": "organizational",
        "channel": channel,
        "origin": origin,
        "ttl_frames": ttl_frames,
        "dedupe_key": dedupe_key,
        "payload": payload,
        "sig": {
            "algo": "ed25519",
            "pubkey": os.getenv("MEMBRANE_DEV_PUBKEY", "dev-local"),
            "signature": os.getenv("MEMBRANE_DEV_SIGNATURE", "dev-local"),
        },
    }


async def send_envelope(ws: websockets.WebSocketClientProtocol, envelope: dict) -> None:
    try:
        await ws.send(json.dumps(envelope))
    except Exception as exc:  # pragma: no cover - diagnostic output
        print(f"[CodexAdapter] Failed to send envelope: {exc}", file=sys.stderr)


async def stream_process_output(
    *,
    reader: asyncio.StreamReader,
    ws: websockets.WebSocketClientProtocol,
    org: str,
    stream_name: str,
    session_id: str,
) -> None:
    while True:
        line = await reader.readline()
        if not line:
            break
        decoded = line.decode(errors="replace")
        print(decoded, end="")
        envelope = build_envelope(
            org=org,
            channel="provider.codex.output",
            origin="provider_codex",
            payload={
                "session_id": session_id,
                "stream": stream_name,
                "data": decoded,
            },
            ttl_frames=900,
            dedupe_key=f"{session_id}:{stream_name}:{abs(hash(decoded))}",
        )
        await send_envelope(ws, envelope)


async def forward_user_input(
    *,
    writer: asyncio.StreamWriter,
    ws: websockets.WebSocketClientProtocol,
    org: str,
    session_id: str,
    prompt_channel: str,
) -> None:
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        try:
            writer.write(line.encode())
            await writer.drain()
        except Exception as exc:  # pragma: no cover
            print(f"[CodexAdapter] Failed to write to Codex stdin: {exc}", file=sys.stderr)
            break
        envelope = build_envelope(
            org=org,
            channel=prompt_channel,
            origin="ui",
            payload={
                "session_id": session_id,
                "content": line,
            },
            ttl_frames=600,
            dedupe_key=f"{session_id}:user:{uuid.uuid4()}",
        )
        await send_envelope(ws, envelope)


async def send_prompts(
    *,
    writer: asyncio.StreamWriter,
    ws: websockets.WebSocketClientProtocol,
    org: str,
    session_id: str,
    prompt_channel: str,
    prompts: Iterable[str],
    close_stdin: bool,
) -> None:
    for prompt in prompts:
        payload = prompt if prompt.endswith("\n") else f"{prompt}\n"
        try:
            writer.write(payload.encode())
            await writer.drain()
        except Exception as exc:  # pragma: no cover
            print(f"[CodexAdapter] Failed to write scripted prompt: {exc}", file=sys.stderr)
            break

        envelope = build_envelope(
            org=org,
            channel=prompt_channel,
            origin="ui",
            payload={"session_id": session_id, "content": payload},
            ttl_frames=600,
            dedupe_key=f"{session_id}:user:{uuid.uuid4()}",
        )
        await send_envelope(ws, envelope)

    if close_stdin:
        with contextlib.suppress(Exception):
            writer.write_eof()  # type: ignore[attr-defined]


async def run(
    cmd: List[str],
    *,
    org: str,
    prompt_channel: str,
    session_id: Optional[str],
    scripted_prompts: Optional[List[str]],
    close_after_prompts: bool,
) -> int:
    inject_uri = os.getenv("MEMBRANE_WS_INJECT", "ws://localhost:8765/inject")
    session_id = session_id or f"codex-{uuid.uuid4()}"

    async with websockets.connect(inject_uri) as ws:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert process.stdin and process.stdout and process.stderr

        tasks: List[asyncio.Task] = [
            asyncio.create_task(
                stream_process_output(
                    reader=process.stdout,
                    ws=ws,
                    org=org,
                    stream_name="stdout",
                    session_id=session_id,
                )
            ),
            asyncio.create_task(
                stream_process_output(
                    reader=process.stderr,
                    ws=ws,
                    org=org,
                    stream_name="stderr",
                    session_id=session_id,
                )
            ),
        ]

        if scripted_prompts:
            tasks.append(
                asyncio.create_task(
                    send_prompts(
                        writer=process.stdin,
                        ws=ws,
                        org=org,
                        session_id=session_id,
                        prompt_channel=prompt_channel,
                        prompts=scripted_prompts,
                        close_stdin=close_after_prompts,
                    )
                )
            )
        else:
            tasks.append(
                asyncio.create_task(
                    forward_user_input(
                        writer=process.stdin,
                        ws=ws,
                        org=org,
                        session_id=session_id,
                        prompt_channel=prompt_channel,
                    )
                )
            )

        await process.wait()

        for task in tasks:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        return process.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex → Membrane adapter (localhost).")
    parser.add_argument(
        "--org",
        default=os.getenv("MEMBRANE_ORG", "dev-org"),
        help="Organization identifier embedded in envelopes.",
    )
    parser.add_argument(
        "--channel",
        default="ui.action.user_prompt",
        help="Stimulus channel used for user prompts.",
    )
    parser.add_argument(
        "--session-id",
        help="Reuse a specific session identifier (default: generated).",
    )
    parser.add_argument(
        "--prompt",
        action="append",
        help="Non-interactive prompt to send (can be repeated).",
    )
    parser.add_argument(
        "--prompt-file",
        help="File containing scripted prompts (one per line).",
    )
    parser.add_argument(
        "--close-after-prompts",
        action="store_true",
        help="Close Codex stdin after scripted prompts (one-shot mode).",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Codex command to execute (default: codex).",
    )
    return parser.parse_args()


def load_prompts(args: argparse.Namespace) -> List[str]:
    prompts: List[str] = []
    if args.prompt_file:
        try:
            with open(args.prompt_file, "r", encoding="utf-8") as fh:
                prompts.extend([line.rstrip("\n") for line in fh if line.strip()])
        except OSError as exc:  # pragma: no cover
            print(f"[CodexAdapter] failed to read prompt file: {exc}", file=sys.stderr)
            sys.exit(1)
    if args.prompt:
        prompts.extend(args.prompt)
    return prompts


def main() -> None:
    args = parse_args()
    cmd = args.command or ["codex"]
    scripted_prompts = load_prompts(args)

    try:
        exit_code = asyncio.run(
            run(
                cmd,
                org=args.org,
                prompt_channel=args.channel,
                session_id=args.session_id,
                scripted_prompts=scripted_prompts or None,
                close_after_prompts=args.close_after_prompts,
            )
        )
    except KeyboardInterrupt:
        exit_code = 130
    except Exception as exc:  # pragma: no cover
        print(f"[CodexAdapter] fatal error: {exc}", file=sys.stderr)
        exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
