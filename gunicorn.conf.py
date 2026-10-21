
import os
import shutil

from prometheus_client import multiprocess

metrics_dir = os.environ["PROMETHEUS_MULTIPROC_DIR"]


def on_starting(server):
    shutil.rmtree(metrics_dir, ignore_errors=True)
    os.makedirs(metrics_dir, exist_ok=True)


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
