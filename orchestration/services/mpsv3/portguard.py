# -*- coding: utf-8 -*-
"""
PortGuard — preflight killer for conflicting port holders (Windows & POSIX).

- Frees ports before supervisor starts child services.
- Avoids false kills by allowlisting the current process tree.
- Works without extra dependencies (uses netstat).

Usage:
    from orchestration.services.mpsv3.portguard import PortGuard
    pg = PortGuard()
    ports = pg.ports_from_services_yaml("services.yaml") or [3000, 8000, 8001, 8002, 8010, 6379]
    pg.kill_port_owners(ports, allowlist_pids=pg.supervisor_allowlist())

Author: Nicolas (design) + Atlas (integration)
Date: 2025-10-25
"""

from __future__ import annotations
import os, sys, re, subprocess, time
from typing import List, Set, Dict, Iterable, Optional

try:
    import yaml  # PyYAML
except Exception:
    yaml = None  # optional

class PortGuard:
    NETSTAT = ["netstat", "-ano"] if os.name == "nt" else ["netstat", "-anp"]

    # Simple port detector from service specs:
    PORT_ENV_KEYS = {"PORT", "WS_PORT", "API_PORT", "METRICS_PORT", "UVICORN_PORT"}

    def _run(self, cmd: List[str]) -> str:
        return subprocess.check_output(cmd, text=True, errors="ignore")

    def pids_on_port(self, port: int) -> Set[int]:
        """
        Return PIDs listening on `port`.
        Works on Windows & POSIX via netstat output parsing.
        """
        out = self._run(self.NETSTAT)
        pids: Set[int] = set()

        # Windows: lines end with PID; "LISTENING" state
        # POSIX: may show "LISTEN" and a "pid/program"
        for line in out.splitlines():
            if f":{port}" not in line:
                continue
            if os.name == "nt":
                if "LISTENING" not in line.upper():
                    continue
                parts = line.strip().split()
                if parts:
                    try:
                        pids.add(int(parts[-1]))
                    except ValueError:
                        pass
            else:
                # Try to capture trailing "pid/program"
                m = re.search(r"\s(\d+)/[\w\-.]+$", line.strip())
                if m:
                    try:
                        pids.add(int(m.group(1)))
                    except ValueError:
                        pass
        return pids

    def supervisor_allowlist(self) -> Set[int]:
        """
        Allowlist current process and obvious ancestors to avoid self-kill.
        On Windows the supervisor will be python.exe; children will be killed by ServiceRunner anyway.
        """
        allow: Set[int] = {os.getpid()}
        # Try to include parent (best-effort; not critical)
        try:
            if os.name == "nt":
                # wmic is deprecated but still widely available; keep best-effort.
                out = self._run(["wmic", "process", "where", f"processid={os.getpid()}", "get", "parentprocessid", "/value"])
                m = re.search(r"ParentProcessId=(\d+)", out)
                if m:
                    allow.add(int(m.group(1)))
        except Exception:
            pass
        return allow

    def kill_pid(self, pid: int) -> None:
        if pid == os.getpid():
            return
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            else:
                subprocess.run(["kill", "-9", str(pid)], check=False)
        except Exception as e:
            print(f"[PortGuard] Failed to kill PID {pid}: {e}")

    def kill_port_owners(self, ports: Iterable[int], allowlist_pids: Optional[Set[int]] = None, verify: bool = True) -> Dict[int, Set[int]]:
        """
        Kill all processes holding the given ports (except allowlisted).
        Returns a map of port -> killed PIDs (best-effort).
        """
        allow = allowlist_pids or set()
        killed: Dict[int, Set[int]] = {}

        for port in ports:
            owners = self.pids_on_port(port)
            to_kill = {pid for pid in owners if pid not in allow}
            killed[port] = set()

            for pid in to_kill:
                self.kill_pid(pid)
                killed[port].add(pid)

        if verify:
            # tiny wait for OS to release sockets
            time.sleep(0.5)
            still_in_use = [p for p in ports if self.pids_on_port(p)]
            if still_in_use:
                print(f"[PortGuard] WARNING: Ports still busy after kill attempt: {still_in_use}")
            else:
                print(f"[PortGuard] All target ports are free: {list(ports)}")
        return killed

    # --------- Optional: derive port list from services.yaml ---------

    def _expand_vars(self, value: str, global_env: dict) -> str:
        """Expand ${VAR} references from global env."""
        if not isinstance(value, str):
            return str(value)
        def replacer(match):
            var_name = match.group(1)
            return global_env.get(var_name, match.group(0))
        return re.sub(r'\$\{([^}]+)\}', replacer, value)

    def ports_from_services_yaml(self, path: str) -> List[int]:
        """
        Parse ports from services.yaml:
          - Known env keys (PORT, WS_PORT, ...)
          - Obvious numeric literals in cmd args (uvicorn --port 8000, next --port 3000)
          - Expands ${VAR} references from top-level env block
        """
        if yaml is None:
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        except Exception:
            return []

        ports: Set[int] = set()
        global_env = cfg.get("env", {}) or {}

        for svc in cfg.get("services", []):
            # env-derived (with variable expansion)
            env = (svc.get("env") or {})
            for k, v in env.items():
                if k in self.PORT_ENV_KEYS:
                    try:
                        expanded = self._expand_vars(str(v), global_env)
                        ports.add(int(expanded))
                    except Exception:
                        pass

            # cmd-derived
            cmd = svc.get("cmd") or []
            for token in cmd:
                # explicit flags
                m = re.search(r"(--port|PORT=)(\s*|=)(\d{2,5})", str(token))
                if m:
                    try:
                        ports.add(int(m.group(3)))
                        continue
                    except Exception:
                        pass
                # bare numbers (last resort; keep safe range)
                try:
                    n = int(str(token))
                    if 80 <= n <= 65535:
                        ports.add(n)
                except Exception:
                    pass

        # Include common infra ports if present in top-level env
        top_env = (cfg.get("env") or {})
        for k, v in top_env.items():
            if k in self.PORT_ENV_KEYS:
                try:
                    ports.add(int(str(v)))
                except Exception:
                    pass

        return sorted(ports)

def kill_port_owners_aggressive(ports, timeout_s=8, sleep_s=0.4, also_node=True):
    """
    Aggressively kill all processes on target ports until they're free.
    Keeps trying for timeout_s seconds, optionally nukes node.exe as fallback.
    
    This is a standalone function (not PortGuard method) for supervisor use.
    """
    import time, subprocess, os
    
    def _pids_on_port_win(port):
        try:
            out = subprocess.check_output(["netstat", "-ano"], text=True, errors="ignore")
            pids = set()
            for line in out.splitlines():
                if f":{port}" in line and "LISTENING" in line.upper():
                    parts = line.strip().split()
                    try:
                        pids.add(int(parts[-1]))
                    except ValueError:
                        pass
            return pids
        except Exception:
            return set()
    
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        still = []
        for port in ports:
            pids = _pids_on_port_win(port)
            for pid in pids:
                if pid == os.getpid():  # safety: never kill self
                    continue
                try:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False, capture_output=True)
                    print(f"[PortGuard] Killed PID {pid} on :{port}")
                except Exception:
                    pass
            # re-check immediately
            if _pids_on_port_win(port):
                still.append(port)
        
        if not still:
            print(f"[PortGuard] All target ports free: {ports}")
            return True
        time.sleep(sleep_s)
    
    # Optional nuclear: if dashboard still blocked, kill node.exe once
    if also_node:
        try:
            subprocess.run(["taskkill", "/F", "/IM", "node.exe"], check=False, capture_output=True)
            print("[PortGuard] Killed node.exe as fallback")
        except Exception:
            pass
        # quick final check
        time.sleep(0.5)
        lingering = [p for p in ports if _pids_on_port_win(p)]
        if not lingering:
            print(f"[PortGuard] Ports free after fallback: {ports}")
            return True
    
    print("[PortGuard] WARNING: Some ports still busy after aggressive attempt")
    return False

