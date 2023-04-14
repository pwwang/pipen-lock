import sys
import logging
from pipen import Proc, Pipen
from pipen.utils import logger


class PrefixFilter(logging.Filter):
    def __init__(self, prefix):
        self.prefix = prefix

    def filter(self, record):
        record.msg = f"[{self.prefix.upper()}] {record.msg}"
        return True


class ExampleProc(Proc):
    input = "in"
    output = "out:var:{{in.in}}"
    script = "sleep 2"


class ExamplePipeline(Pipen):
    starts = ExampleProc
    cache = False
    data = [["a", "b", "c", "d", "e"]]


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "default"
    logger.logger.addFilter(PrefixFilter(prefix))
    logging.getLogger("pipen.lock").addFilter(PrefixFilter(prefix))
    ExamplePipeline(plugins=["lock"]).run()
