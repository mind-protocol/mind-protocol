#!/usr/bin/env python3
"""
monitor_wallet.py — Monitor deployer wallet for incoming SOL transfers.

Polls the Solana mainnet RPC for the wallet balance every N seconds.
When the balance reaches the target threshold, prints a notification
and exits with code 0.

Usage:
    python3 monitor_wallet.py
    python3 monitor_wallet.py --threshold 2.5
    python3 monitor_wallet.py --threshold 5.0 --interval 5
    python3 monitor_wallet.py --wallet <address> --callback "echo funded"
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


DEFAULT_WALLET = "CCsJLZR8b19iDgS9hXUYs9q2c928ihzZdfSgZLPYffWg"
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
DEFAULT_THRESHOLD = 2.5
DEFAULT_INTERVAL = 10
LAMPORTS_PER_SOL = 1_000_000_000


def get_balance_rpc(wallet: str, rpc_url: str) -> float | None:
    """Fetch SOL balance via JSON-RPC getBalance call."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet]
    }).encode("utf-8")

    req = urllib.request.Request(
        rpc_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"  [RPC error] {exc}", file=sys.stderr)
        return None

    if "error" in data:
        print(f"  [RPC error] {data['error']}", file=sys.stderr)
        return None

    lamports = data.get("result", {}).get("value")
    if lamports is None:
        print("  [RPC error] Unexpected response shape", file=sys.stderr)
        return None

    return lamports / LAMPORTS_PER_SOL


def get_balance_cli(wallet: str) -> float | None:
    """Fallback: fetch balance via `solana balance` CLI."""
    try:
        result = subprocess.run(
            ["solana", "balance", wallet, "--url", "mainnet-beta"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode != 0:
            print(f"  [CLI error] {result.stderr.strip()}", file=sys.stderr)
            return None
        # Output looks like "2.5 SOL"
        parts = result.stdout.strip().split()
        if parts:
            return float(parts[0])
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as exc:
        print(f"  [CLI error] {exc}", file=sys.stderr)
    return None


def get_balance(wallet: str, rpc_url: str) -> float | None:
    """Try RPC first, fall back to CLI."""
    balance = get_balance_rpc(wallet, rpc_url)
    if balance is not None:
        return balance
    print("  Falling back to solana CLI...", file=sys.stderr)
    return get_balance_cli(wallet)


def format_elapsed(seconds: float) -> str:
    """Format seconds into a human-readable duration string."""
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours = int(minutes // 60)
    mins = minutes % 60
    return f"{hours}h {mins}m {secs}s"


def run_callback(callback_cmd: str) -> None:
    """Execute a shell callback command."""
    print(f"\n  Running callback: {callback_cmd}")
    try:
        result = subprocess.run(
            callback_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.stdout.strip():
            print(f"  [callback stdout] {result.stdout.strip()}")
        if result.stderr.strip():
            print(f"  [callback stderr] {result.stderr.strip()}")
        if result.returncode != 0:
            print(f"  [callback] Exited with code {result.returncode}")
    except subprocess.TimeoutExpired:
        print("  [callback] Timed out after 60s")


def monitor(
    wallet: str,
    rpc_url: str,
    threshold: float,
    interval: int,
    callback: str | None = None,
) -> None:
    """Main monitoring loop."""
    print("=" * 60)
    print("  $MIND Token Launch — Wallet Monitor")
    print("=" * 60)
    print(f"  Wallet:    {wallet}")
    print(f"  RPC:       {rpc_url}")
    print(f"  Threshold: {threshold} SOL")
    print(f"  Interval:  {interval}s")
    if callback:
        print(f"  Callback:  {callback}")
    print("=" * 60)
    print()

    start_time = time.monotonic()
    check_count = 0
    last_balance = None

    try:
        while True:
            check_count += 1
            elapsed = time.monotonic() - start_time
            now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

            balance = get_balance(wallet, rpc_url)

            if balance is None:
                print(f"  [{now}] Check #{check_count} — "
                      f"Failed to fetch balance (retrying in {interval}s) — "
                      f"Elapsed: {format_elapsed(elapsed)}")
                time.sleep(interval)
                continue

            # Detect change from previous check
            delta = ""
            if last_balance is not None:
                diff = balance - last_balance
                if abs(diff) > 0.000000001:
                    sign = "+" if diff > 0 else ""
                    delta = f" ({sign}{diff:.9f} SOL)"
            last_balance = balance

            remaining = threshold - balance
            pct = (balance / threshold * 100) if threshold > 0 else 100

            if balance >= threshold:
                print()
                print("*" * 60)
                print(f"  THRESHOLD REACHED!")
                print(f"  Balance:   {balance:.9f} SOL")
                print(f"  Target:    {threshold} SOL")
                print(f"  Surplus:   {balance - threshold:.9f} SOL")
                print(f"  Time:      {format_elapsed(elapsed)}")
                print(f"  Checks:    {check_count}")
                print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
                print("*" * 60)

                if callback:
                    run_callback(callback)

                sys.exit(0)
            else:
                bar_width = 30
                filled = int(bar_width * pct / 100)
                bar = "#" * filled + "-" * (bar_width - filled)

                print(f"  [{now}] #{check_count:>4} | "
                      f"{balance:>12.9f} / {threshold} SOL | "
                      f"[{bar}] {pct:5.1f}% | "
                      f"Need {remaining:.9f} more | "
                      f"{format_elapsed(elapsed)}{delta}")

            time.sleep(interval)

    except KeyboardInterrupt:
        elapsed = time.monotonic() - start_time
        print(f"\n  Stopped after {format_elapsed(elapsed)} "
              f"({check_count} checks). Last balance: "
              f"{last_balance if last_balance is not None else 'unknown'} SOL")
        sys.exit(130)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monitor Solana wallet balance for $MIND token launch",
    )
    parser.add_argument(
        "--wallet",
        default=DEFAULT_WALLET,
        help=f"Wallet address to monitor (default: {DEFAULT_WALLET})",
    )
    parser.add_argument(
        "--rpc",
        default=DEFAULT_RPC,
        help=f"Solana RPC endpoint (default: {DEFAULT_RPC})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"SOL balance threshold to trigger notification (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--callback",
        type=str,
        default=None,
        help="Shell command to execute when threshold is met",
    )
    args = parser.parse_args()

    if args.threshold <= 0:
        print("Error: --threshold must be positive", file=sys.stderr)
        sys.exit(1)
    if args.interval < 1:
        print("Error: --interval must be at least 1 second", file=sys.stderr)
        sys.exit(1)

    monitor(
        wallet=args.wallet,
        rpc_url=args.rpc,
        threshold=args.threshold,
        interval=args.interval,
        callback=args.callback,
    )


if __name__ == "__main__":
    main()
