"""
Demonstrates how to set the pipe size on Linux systems.
"""

import os, sys, fcntl
import fire
import time
import pickle

if not sys.platform.startswith('linux'):
    raise RuntimeError("Only Linux systems supported.")

fifo_name = 'test_fifo'

F_SETPIPE_SZ = 1031 # Linux 2.6.35+
F_GETPIPE_SZ = 1032 # Linux 2.6.35+

def run(pipe_size: int = 2 ** 20) -> None:
    if os.path.exists(fifo_name):
        os.remove(fifo_name)

    try:
        os.mkfifo(fifo_name)
        f = os.open(fifo_name, os.O_RDWR | os.O_NONBLOCK)
        fd = os.fdopen(f, 'wb')

        old_pipe_size = fcntl.fcntl(fd, F_GETPIPE_SZ)
        print(f"Old pipe size: {old_pipe_size}")

        fcntl.fcntl(fd, F_SETPIPE_SZ, pipe_size)
        new_pipe_size = fcntl.fcntl(fd, F_GETPIPE_SZ)

        if new_pipe_size != pipe_size:
            raise RuntimeError("Unable to set pipe to desired size.")
    finally:
        if os.path.exists(fifo_name):
            os.remove(fifo_name)

if __name__ == '__main__':
    fire.Fire(run)
