"""Universal Basic Compute distributor."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster
from orchestration.services.wallet_custody.ledger import Ledger, LedgerEntry

from .membrane_store import MembraneStore
from .settings import EconomySettings

logger = logging.getLogger(__name__)


class WalletService:
    """Thin wrapper over custody ledger for transfer attestations."""

    def __init__(self, ledger_path: Path) -> None:
        self._ledger = Ledger(ledger_path)

    async def transfer(self, source: str, destination: str, amount: float, memo: str) -> None:
        entry = LedgerEntry.create(
            entry_type="wallet.transfer",
            wallet_id=source,
            payload={
                "destination": destination,
                "amount_mind": amount,
                "memo": memo,
            },
        )
        await asyncio.to_thread(self._ledger.append, entry)


class UBCDistributor:
    """Schedules daily UBC payouts and telemetry emission."""

    def __init__(
        self,
        settings: EconomySettings,
        store: MembraneStore,
        broadcaster: ConsciousnessStateBroadcaster,
        ledger_path: Path = Path("logs/wallet_transfers.jsonl"),
    ) -> None:
        self._settings = settings
        self._store = store
        self._broadcaster = broadcaster
        self._wallet = WalletService(ledger_path)
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        if self._settings.ubc_daily <= 0:
            logger.info("UBC distribution disabled (UBC_DAILY <= 0)")
            return
        if not self._settings.ubc_treasury_wallet:
            logger.warning("UBC treasury wallet not configured; skipping distribution")
            return
        if not self._settings.ubc_citizen_wallets:
            logger.warning("UBC citizen wallets not configured; skipping distribution")
            return

        if self._task is None:
            self._running = True
            self._task = asyncio.create_task(self._run(), name="ubc-distributor")
            logger.info(
                "UBC distributor scheduled for %d citizens (daily %.2f MIND)",
                len(self._settings.ubc_citizen_wallets),
                self._settings.ubc_daily,
            )

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:  # pragma: no cover - cooperative cancellation
                pass
            self._task = None

    async def _run(self) -> None:
        while self._running:
            delay = self._seconds_until_next_tick()
            await asyncio.sleep(delay)
            await self._distribute()

    def _seconds_until_next_tick(self) -> float:
        now = datetime.utcnow()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        offset = timedelta(seconds=max(0, self._settings.ubc_start_offset_seconds))
        scheduled = next_midnight + offset
        return max(1.0, (scheduled - now).total_seconds())

    async def _distribute(self) -> None:
        amount = self._settings.ubc_daily
        source_wallet = self._settings.ubc_treasury_wallet
        timestamp = datetime.now(timezone.utc).isoformat()

        for citizen, wallet in self._settings.ubc_citizen_wallets.items():
            memo = f"UBC daily transfer {timestamp}"
            try:
                await self._wallet.transfer(source_wallet, wallet, amount, memo=memo)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("Failed UBC transfer to %s: %s", citizen, exc)
                continue

            wallet_node = f"node:citizen:{citizen}"
            await self._store.adjust_wallet_balance(self._settings.org_id, wallet_node, amount)
            await self._store.record_ubc_ledger(
                self._settings.org_id,
                {
                    "citizen_id": citizen,
                    "wallet": wallet,
                    "amount_mind": f"{amount:.6f}",
                    "timestamp": timestamp,
                },
            )
            await self._store.set_wallet_next_ubc(self._settings.org_id, wallet_node, timestamp)

            telemetry = {
                "citizen_id": citizen,
                "amount_mind": amount,
                "wallet": wallet,
                "timestamp": timestamp,
                "org_id": self._settings.org_id,
            }
            await self._broadcaster.broadcast_event("telemetry.economy.ubc_tick", telemetry)
