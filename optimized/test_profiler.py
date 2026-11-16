"""Correctness, timing, memory, and main-path coverage checks."""
import time
import sys
import unittest
from unittest.mock import patch
try:
    from memory_profiler import memory_usage
except ImportError:
    # Linux fallback for running tests in an offline environment.
    import os
    def memory_usage(*args, **kwargs):
        with open("/proc/self/statm") as stream:
            resident_pages = int(stream.read().split()[1])
        return [resident_pages * os.sysconf("SC_PAGE_SIZE") / 1024 ** 2]

import profiler


class TestProfiler(unittest.TestCase):
    def test_slow_function(self):
        start = time.perf_counter()
        self.assertEqual(profiler.slow_function(), 333283335000)
        duration = time.perf_counter() - start
        print(f"slow_function: {duration:.6f} s")
        self.assertGreaterEqual(duration, 2)

    def test_fast_function(self):
        start = time.perf_counter()
        self.assertEqual(profiler.optimized_fast_function(), 328350)
        duration = time.perf_counter() - start
        print(f"optimized_fast_function: {duration:.9f} s")
        self.assertLess(duration, 1)

    def test_memory_intensive_function(self):
        before = memory_usage(-1, interval=0.1, timeout=0.1)[0]
        start = time.perf_counter()
        self.assertEqual(profiler.memory_intensive_function(), 333333283333335000000)
        duration = time.perf_counter() - start
        after = memory_usage(-1, interval=0.1, timeout=0.1)[0]
        print(f"memory_intensive_function: {duration:.6f} s; RSS {before:.3f} -> {after:.3f} MiB")
        if sys.gettrace() is None:
            self.assertLess(duration, 5)
        else:
            print("5-second budget not asserted under tracing instrumentation.")
        # The loop keeps only an accumulator; RSS need not increase.
        self.assertLess(abs(after - before), 20)

    def test_main(self):
        with patch.object(profiler, "slow_function") as slow, patch.object(profiler, "optimized_fast_function") as fast, patch.object(profiler, "memory_intensive_function") as memory:
            profiler.main()
        slow.assert_called_once_with()
        fast.assert_called_once_with()
        memory.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
