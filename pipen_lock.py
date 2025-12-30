from __future__ import annotations
from time import sleep
from typing import TYPE_CHECKING

from panpath import PanPath, CloudPath
from pipen import plugin
from pipen.utils import get_logger
from filelock import FileLock, SoftFileLock, Timeout

if TYPE_CHECKING:  # pragma: no cover
    from pipen import Pipen, Proc

__version__ = "1.1.0"

logger = get_logger("lock", "info")


class CloudFileLock:
    """Support file lock for cloud files, simply rely on file existence."""

    def __init__(self, lockfile: str | CloudPath):
        """Initialize the lock file."""
        if isinstance(lockfile, str):
            self.lockfile = PanPath(lockfile)
        else:
            self.lockfile = lockfile

    async def acquire(self, blocking: bool = True):
        """Acquire the lock."""
        if blocking:
            while await self.lockfile.a_exists():
                sleep(0.1)  # Add sleep to prevent CPU hogging

        # Create lock file when acquired
        if await self.lockfile.a_exists():
            if not blocking:
                raise Timeout("Lock already exists")
        else:
            # Create the lock file
            await self.lockfile.a_touch()

    async def release(self, force: bool = False):
        """Release the lock."""
        if force or await self.lockfile.a_exists():
            await self.lockfile.a_unlink()


class PipenLockPlugin:
    version = __version__
    name = "lock"

    def __init__(self):
        self.lock = None

    @plugin.impl
    async def on_init(self, pipen: Pipen):
        pipen.config.plugin_opts.setdefault("lock_soft", False)

    @plugin.impl
    async def on_proc_start(self, proc: Proc):
        if isinstance(proc.workdir, CloudPath):
            self.lock = CloudFileLock(proc.workdir / "proc.lock")
            msg = [
                "Process locked, likely handled by another pipeline instance",
                "If not, remove the lock file manually: "
                f"{self.lock.lockfile}",
            ]

        elif proc.plugin_opts.lock_soft:
            self.lock = SoftFileLock(proc.workdir / "proc.lock")
            msg = [
                "Process locked, likely handled by another pipeline instance",
                f"If not, remove the lock file manually: {self.lock.lock_file}",
            ]

        else:
            self.lock = FileLock(proc.workdir / "proc.lock")
            msg = ["Process locked, likely handled by another pipeline instance"]

        try:
            await self.lock.acquire(blocking=False)
        except Timeout:
            for m in msg:
                proc.log("warning", m, logger=logger)
        else:
            await self.lock.release()

        await self.lock.acquire()

    @plugin.impl
    async def on_proc_done(self, proc: Proc, succeeded: bool):
        await self.lock.release(True)


pipen_lock_plugin = PipenLockPlugin()
