import attr
import asyncio
import struct, pickle
import os, io, fcntl, select

from typing import Any, List, Union

F_SETPIPE_SZ = 1031 # Linux 2.6.35+
F_GETPIPE_SZ = 1032 # Linux 2.6.35+

async def wait_for_reader(fd: Union[int, io.BufferedReader], loop: asyncio.AbstractEventLoop) -> None:
    f: asyncio.Future = asyncio.Future()
    loop.add_reader(fd, f.set_result, None)
    f.add_done_callback(lambda f: loop.remove_reader(fd))
    await f

async def wait_for_writer(fd: Union[int, io.BufferedWriter], loop: asyncio.AbstractEventLoop) -> None:
    f: asyncio.Future = asyncio.Future()
    loop.add_writer(fd, f.set_result, None)
    f.add_done_callback(lambda f: loop.remove_writer(fd))
    await f

@attr.s
class PipeReader:
    """
    For nonblocking IO with named pipes, the reader must be opened before the writer.
    """

    fifo_name: str = attr.ib()

    def __attrs_post_init__(self) -> None:
        if not os.path.exists(self.fifo_name):
            os.mkfifo(self.fifo_name)

        self.f = os.open(self.fifo_name, os.O_RDONLY | os.O_NONBLOCK)

    def __del__(self) -> None:
        os.close(self.f)

    async def read(self, loop: asyncio.AbstractEventLoop) -> Any:
        await wait_for_reader(self.f, loop)
        n_read, n_total = 0, struct.unpack('@Q', os.read(self.f, 8))[0]

        # It's expensive to repeatedly concatenate byte buffers, so we consolidate this to the end.
        chunks: List[bytes] = []

        while True:
            await wait_for_reader(self.f, loop)

            """
            Although 1 MiB is larger than `select.PIPE_BUF`, the reads still seem to be atomic on Linux and the total
            read time for 1 GiB of data is ~3x faster.
            """
            chunk = os.read(self.f, min(2 ** 20, n_total - n_read))
            chunks.append(chunk)
            n_read = n_read + len(chunk)
            assert n_read <= n_total

            if n_read == n_total:
                return pickle.loads(b''.join(chunks))

@attr.s
class PipeWriter:
    fifo_name: str = attr.ib()

    def __attrs_post_init__(self) -> None:
        self.f = os.open(self.fifo_name, os.O_WRONLY | os.O_NONBLOCK)

        # I wasn't able to improve write speed for 1 GiB of data by increasing the pipe size past 1 MiB.
        fcntl.fcntl(self.f, F_SETPIPE_SZ, 2 ** 20)

    def __del__(self) -> None:
        os.close(self.f)

    async def _send(self, buf: bytes, loop: asyncio.AbstractEventLoop) -> None:
        view, n_sent = memoryview(buf), 0

        while True:
            await wait_for_writer(self.f, loop)

            try:
                n = os.write(self.f, view[n_sent:])
            except BlockingIOError:
                continue

            n_sent += n
            assert n_sent <= len(buf)

            if n_sent == len(buf):
                return

    async def write(self, x: Any, loop: asyncio.AbstractEventLoop) -> None:
        """
        This approach is based on the one taken by the multiprocessing package here:
        https://github.com/python/cpython/blob/master/Lib/multiprocessing/connection.py#L395
        """

        buf = pickle.dumps(x)
        length = struct.pack('@Q', len(buf))

        if len(buf) > 16384:
            await self._send(length, loop)
            await self._send(buf, loop)
        else:
            await self._send(length + buf, loop)
