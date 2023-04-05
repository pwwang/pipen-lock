from __future__ import annotations
from typing import TYPE_CHECKING

from pipen import plugin
from pipen.utils import get_logger
from filelock import FileLock, Timeout

if TYPE_CHECKING:  # pragma: no cover
    from pipen import Proc

__version__ = "0.1.1"

logger = get_logger("lock", "info")


class PipenLockPlugin:
    version = __version__
    name = "lock"

    def __init__(self):
        self.lock = None

    @plugin.impl
    async def on_proc_start(self, proc: Proc):
        self.lock = FileLock(proc.workdir / "proc.lock")
        try:
            self.lock.acquire(blocking=False)
        except Timeout:
            proc.log(
                "warning",
                "Process locked, likely handled by another pipeline instance",
                logger=logger,
            )
        else:
            self.lock.release()

        self.lock.acquire()

    @plugin.impl
    async def on_proc_done(self, proc: Proc, succeeded: bool):
        self.lock.release(True)


pipen_lock_plugin = PipenLockPlugin()
