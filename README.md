# Overview

Experiments exploring named pipes with Python.

Conclusion: named pipes are ok for IPC for messages less than or equal to ~1 MiB in size. They don't seem to be great
for sending large amounts of data (e.g. 1 GiB) quickly: this takes ~1.5 seconds for the producer to write and ~4.5
seconds for the consumer to read (see `tests/pipe_test.py`). This is after tweaking the pipe and buffer sizes, so my
guess is that the bottleneck here is likely not on the Python side.

# Scripts

- `scripts/set_pipe_size.py`: simple test for setting / getting the maximum pipe size.
- `scripts/pipe_test.py`: tests `PipeReader` and `PipeWriter`.
