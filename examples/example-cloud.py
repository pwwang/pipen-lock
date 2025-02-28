import logging
import time
from dotenv import load_dotenv
from pipen import Proc, Pipen
from pipen.utils import logger

load_dotenv()
BUCKET = "gs://handy-buffer-287000.appspot.com"


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


class ExamplePipelineCloudWdir(Pipen):
    starts = ExampleProc
    cache = False
    data = [["a", "b", "c", "d", "e"]]
    workdir = f"{BUCKET}/pipen-lock-example"


class ExamplePipelineCloudWdir2(ExamplePipelineCloudWdir):
    name = "ExamplePipelineCloudWdir"
    starts = ExampleProc
    cache = True
    workdir = f"{BUCKET}/pipen-lock-example"


def run_pipeline_with_prefix(pipeline_class, prefix):
    # Create a new logger filter with the specified prefix
    prefix_filter = PrefixFilter(prefix)

    # Add the filter to both loggers
    logger.logger.addFilter(prefix_filter)
    logging.getLogger("pipen.lock").addFilter(prefix_filter)

    # Run the pipeline
    pipeline_class(plugins=["lock"]).run()


if __name__ == "__main__":
    # if len(sys.argv) > 1:
    #     prefix = sys.argv[1]
    #     logger.logger.addFilter(PrefixFilter(prefix))
    #     logging.getLogger("pipen.lock").addFilter(PrefixFilter(prefix))

    #     ExamplePipeline(plugins=["lock"]).run()
    # else:

    # using multiprocessing to run the pipeline twice at the same time
    from multiprocessing import Process

    p1 = Process(
        target=run_pipeline_with_prefix,
        args=(ExamplePipelineCloudWdir, "P1"),
    )
    p2 = Process(
        target=run_pipeline_with_prefix,
        args=(ExamplePipelineCloudWdir2, "P2"),
    )
    p1.start()
    time.sleep(10)
    p2.start()
    p1.join()
    p2.join()
