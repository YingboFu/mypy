"""Test cases that run tests as subprocesses."""

import os
import subprocess
import sys
import unittest
from typing import List

base_dir = os.path.join(os.path.dirname(__file__), "..", "..")


class TestExternal(unittest.TestCase):
    # TODO: Get this to work on Windows.
    # (Or don't. It is probably not a good use of time.)
    @unittest.skipIf(sys.platform.startswith("win"), "rt tests don't work on windows")
    def test_c_unit_test(self) -> None:
        """Run C unit tests in a subprocess."""
        # Build Google Test, the C++ framework we use for testing C code.
        # The source code for Google Test is copied to this repository.
        cppflags: List[str] = []
        env = os.environ.copy()
        if sys.platform == "darwin":
            cppflags += ["-mmacosx-version-min=10.10", "-stdlib=libc++"]
        env["CPPFLAGS"] = " ".join(cppflags)
        subprocess.check_call(
            ["make", "libgtest.a"],
            env=env,
            cwd=os.path.join(base_dir, "mypyc", "external", "googletest", "make"),
        )
        # Build Python wrapper for C unit tests.
        env = os.environ.copy()
        env["CPPFLAGS"] = " ".join(cppflags)
        status = subprocess.check_call(
            [sys.executable, "setup.py", "build_ext", "--inplace"],
            env=env,
            cwd=os.path.join(base_dir, "mypyc", "lib-rt"),
        )
        # Run C unit tests.
        env = os.environ.copy()
        if "GTEST_COLOR" not in os.environ:
            env["GTEST_COLOR"] = "yes"  # Use fancy colors
        status = subprocess.call(
            [sys.executable, "-c", "import sys, test_capi; sys.exit(test_capi.run_tests())"],
            env=env,
            cwd=os.path.join(base_dir, "mypyc", "lib-rt"),
        )
        if status != 0:
            raise AssertionError("make test: C unit test failure")
