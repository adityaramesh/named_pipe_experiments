"""
Tests to check that `PipeReader` and `PipeWriter` work as intended.
"""

import os, sys
sys.path.insert(0, os.getcwd())

import asyncio
import fire
import time

from utils import PipeReader, PipeWriter

def test_1(task: str) -> None:
    """
    Tests simple write.

    Note: the reader must be run before the writer.
    """

    loop = asyncio.get_event_loop()

    if task == 'read':
        r = PipeReader('test')
        print(loop.run_until_complete(r.read(loop)))
    elif task == 'write':
        w = PipeWriter('test')
        loop.run_until_complete(w.write(2, loop))

def test_2(task: str) -> None:
    """
    Tests simple write.

    Note: the reader must be run before the writer.
    """

    loop = asyncio.get_event_loop()

    if task == 'read':
        r = PipeReader('test')
        print(loop.run_until_complete(r.read(loop)))
    elif task == 'write':
        w = PipeWriter('test')
        loop.run_until_complete(w.write({'foo': ['bar_1', 'bar_2'], 'bar': 0}, loop))

def test_3(task: str) -> None:
    """
    Tests buffering logic.
    """

    loop = asyncio.get_event_loop()

    if task == 'read':
        r = PipeReader('test')
        print(loop.run_until_complete(r.read(loop)))
    elif task == 'write':
        w = PipeWriter('test')
        x = (16384 * 'a').encode('utf-8')
        loop.run_until_complete(w.write(x, loop))

def test_4(task: str) -> None:
    """
    Tests sending a large amount of data.
    """

    loop = asyncio.get_event_loop()

    if task == 'read':
        r = PipeReader('test')
        t0 = time.time()
        loop.run_until_complete(r.read(loop))
        dt = time.time() - t0
        print(f"Reading took {dt} seconds.")
    elif task == 'write':
        w = PipeWriter('test')
        x = ((2 ** 30) * '0').encode('utf-8')
        t0 = time.time()
        loop.run_until_complete(w.write(x, loop))
        dt = time.time() - t0
        print(f"Writing took {dt} seconds.")

if __name__ == '__main__':
    #fire.Fire(test_1)
    #fire.Fire(test_2)
    #fire.Fire(test_3)
    fire.Fire(test_4)
