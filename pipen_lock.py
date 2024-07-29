from __future__ import annotations
from typing import TYPE_CHECKING

from pipen import plugin
from pipen.utils import get_logger
from filelock import FileLock, SoftFileLock, Timeout

if TYPE_CHECKING:  # pragma: no cover
    from pipen import Pipen, Proc

__version__ = "0.8.0"

logger = get_logger("lock", "info")


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
        if proc.plugin_opts.lock_soft:
            self.lock = SoftFileLock(proc.workdir / "proc.lock")
            msg = [
                "Process locked, likely handled by another pipeline instance",
                f"If not, remove the lock file manually: {self.lock.lock_file}",
            ]
        else:
            self.lock = FileLock(proc.workdir / "proc.lock")
            msg = ["Process locked, likely handled by another pipeline instance"]

        try:
            self.lock.acquire(blocking=False)
        except Timeout:
            for m in msg:
                proc.log("warning", m, logger=logger)
        else:
            self.lock.release()

        self.lock.acquire()

    @plugin.impl
    async def on_proc_done(self, proc: Proc, succeeded: bool):
        self.lock.release(True)


pipen_lock_plugin = PipenLockPlugin()
