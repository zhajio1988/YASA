#******************************************************************************
# * Copyright (c) 2019, XtremeDV. All rights reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
# * Author: Jude Zhang, Email: zhajio.1988@gmail.com
# *******************************************************************************
# Copyright (c) 2014-2018, Lars Asplund lars.anders.asplund@gmail.com

"""
Provided functionality to run a suite of test in a robust way
"""

from __future__ import print_function

import os
from os.path import join, exists, abspath, basename, relpath
import traceback
import threading
import sys
import time
import logging
import string
from contextlib import contextmanager
import ostools
from test_report import PASSED, FAILED, WARNED
from hashing import hash_string

LOGGER = logging.getLogger(__name__)

class TestRunner(object):
    """
    Administer the execution of a list of test suites
    """
    VERBOSITY_QUIET = 0
    VERBOSITY_NORMAL = 1
    VERBOSITY_VERBOSE = 2

    def __init__(self,
                 report,
                 verbosity=VERBOSITY_NORMAL,
                 num_threads=1,
                 fail_fast=False,
                 dont_catch_exceptions=False,
                 no_color=False):
        self._lock = threading.Lock()
        self._fail_fast = fail_fast
        self._abort = False
        self._local = threading.local()
        self._report = report
        assert verbosity in (self.VERBOSITY_QUIET,
                             self.VERBOSITY_NORMAL,
                             self.VERBOSITY_VERBOSE)
        self._verbosity = verbosity
        self._num_threads = num_threads
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        self._dont_catch_exceptions = dont_catch_exceptions
        self._no_color = no_color

        ostools.PROGRAM_STATUS.reset()

    @property
    def _is_verbose(self):
        return self._verbosity == self.VERBOSITY_VERBOSE

    @property
    def _is_quiet(self):
        return self._verbosity == self.VERBOSITY_QUIET

    def run(self, test_suites):
        """
        Run a list of test suites
        """

        num_tests = 0
        for test_suite in test_suites:
            for test_name in test_suite.test_names:
                num_tests += 1
                if self._is_verbose:
                    print("Running test: " + test_name)

        if self._is_verbose:
            print("Running %i tests" % num_tests)
            print()

        self._report.set_expected_num_tests(num_tests)

        scheduler = TestScheduler(test_suites)

        threads = []

        # Disable continuous output in parallel mode
        write_stdout = self._is_verbose and self._num_threads == 1

        try:
            sys.stdout = ThreadLocalOutput(self._local, self._stdout)
            sys.stderr = ThreadLocalOutput(self._local, self._stdout)

            # Start P-1 worker threads
            for _ in range(self._num_threads - 1):
                new_thread = threading.Thread(target=self._run_thread,
                                              args=(write_stdout, scheduler, num_tests, False))
                threads.append(new_thread)
                new_thread.start()

            # Run one worker in main thread such that P=1 is not multithreaded
            self._run_thread(write_stdout, scheduler, num_tests, True)

            scheduler.wait_for_finish()

        except KeyboardInterrupt:
            LOGGER.debug("TestRunner: Caught Ctrl-C shutting down")
            ostools.PROGRAM_STATUS.shutdown()
            raise

        finally:
            for thread in threads:
                thread.join()

            sys.stdout = self._stdout
            sys.stderr = self._stderr
            LOGGER.debug("TestRunner: Leaving")

    def _run_thread(self, write_stdout, scheduler, num_tests, is_main):
        """
        Run worker thread
        """
        self._local.output = self._stdout

        while True:
            test_suite = None
            try:
                test_suite = scheduler.next()

                with self._stdout_lock():
                    for test_name in test_suite.test_names:
                        print("Starting %s" % test_name)
                    #print("Output file: %s" % test_suite.test_result_file)

                self._run_test_suite(test_suite,
                                     write_stdout,
                                     num_tests)

            except StopIteration:
                return

            except KeyboardInterrupt:
                # Only main thread should handle KeyboardInterrupt
                if is_main:
                    LOGGER.debug("MainWorkerThread: Caught Ctrl-C shutting down")
                    raise

                return

            finally:
                if test_suite is not None:
                    scheduler.test_done()

    def _add_skipped_tests(self, test_suite, results, start_time, num_tests, output_file_name):
        for name in test_suite.test_names:
            #TODO: set case not run as failed case
            results[name] = FAILED
        self._add_results(test_suite, results, start_time, num_tests, output_file_name)

    def _run_test_suite(self,
                        test_suite,
                        write_stdout,
                        num_tests):
        """
        Run the actual test suite
        """
        #output_file = None

        start_time = ostools.get_time()
        results = self._fail_suite(test_suite)

        try:
            if write_stdout:
                """
                If write_stdout enable, use stdout, showing log in terminal
                """
                #self._local.output = Tee([self._stdout])
                self._local.output = self._stdout
            else:
                """
                Open a dummy file os.devnull for writing log file to it, 
                not showing log in terminal
                If you want to save log in a file, use code below:
                >>> output_file = open("xxx.log", "w")
                >>> self._local.output = Tee([output_file])
                """
                devNull = open(os.devnull, "w")
                self._local.output = devNull
                #self._local.output = Tee([devNull])

            results = test_suite.run()

        except KeyboardInterrupt:
            self._add_skipped_tests(test_suite, results, start_time, num_tests, test_suite.test_result_file)
            raise KeyboardInterrupt
        except:
            if self._dont_catch_exceptions:
                raise

            with self._stdout_lock():
                traceback.print_exc()
        finally:
            self._local.output = self._stdout

            #for fptr in [output_file]:
            #    if fptr is None:
            #        continue

            #    fptr.flush()
            #    fptr.close()

        any_not_passed = any(value != PASSED for value in results.values())

        with self._stdout_lock():
            if (any_not_passed or self._is_verbose) and not self._is_quiet and not write_stdout:
                #use stdout, print log file contents in terminal.
                self._print_output(test_suite.test_result_file)

            self._add_results(test_suite, results, start_time, num_tests, test_suite.test_result_file)

            if self._fail_fast and any_not_passed:
                self._abort = True

    def _print_output(self, output_file_name):
        """
        Print contents of output file if it exists
        """
        with open(output_file_name, "r") as fh:
            for line in fh.readlines():
                self._stdout.write(line)

    def _add_results(self, test_suite, results, start_time, num_tests, output_file_name):
        """
        Add results to test report
        """
        runtime = ostools.get_time() - start_time
        time_per_test = runtime / len(results)

        for test_name in test_suite.test_names:
            status = results[test_name]
            self._report.add_result(test_name,
                                    status,
                                    time_per_test,
                                    output_file_name)
            self._report.print_latest_status(total_tests=num_tests)
        print()

    @staticmethod
    def _fail_suite(test_suite):
        """ Return failure for all tests in suite """
        results = {}
        for test_name in test_suite.test_names:
            results[test_name] = FAILED
        return results

    @contextmanager
    def _stdout_lock(self):
        """
        Enter this lock when printing to stdout
        Ensures no additional output is printed during abort
        """
        with self._lock:  # pylint: disable=not-context-manager
            if self._abort:
                raise KeyboardInterrupt
            yield


class Tee(object):
    """
    Provide a write method which writes to multiple files
    like the unix 'tee' command.
    """
    def __init__(self, files):
        self._files = files

    def write(self, txt):
        for ofile in self._files:
            ofile.write(txt)

    def flush(self):
        for ofile in self._files:
            ofile.flush()


class ThreadLocalOutput(object):
    """
    Replacement for stdout/err that separates re-directs
    output to a thread local file interface
    """
    def __init__(self, local, stdout):
        self._local = local
        self._stdout = stdout

    def write(self, txt):
        """
        Write to file object
        """
        if hasattr(self._local, "output"):
            self._local.output.write(txt)
        else:
            self._stdout.write(txt)

    def flush(self):
        """
        Flush file object
        """
        if hasattr(self._local, "output"):
            self._local.output.flush()
        else:
            self._stdout.flush()


class TestScheduler(object):
    """
    Schedule tests to different treads
    """

    def __init__(self, tests):
        self._lock = threading.Lock()
        self._tests = tests
        self._idx = 0
        self._num_done = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Iterator in Python 3
        """
        return self.__next__()

    def next(self):
        """
        Iterator in Python 2
        """
        ostools.PROGRAM_STATUS.check_for_shutdown()
        with self._lock:  # pylint: disable=not-context-manager
            if self._idx < len(self._tests):
                idx = self._idx
                self._idx += 1
                return self._tests[idx]

            raise StopIteration

    def test_done(self):
        """
        Signal that a test has been done
        """
        with self._lock:  # pylint: disable=not-context-manager
            self._num_done += 1

    def is_finished(self):
        with self._lock:  # pylint: disable=not-context-manager
            return self._num_done >= len(self._tests)

    def wait_for_finish(self):
        """
        Block until all tests have been done
        """
        while not self.is_finished():
            time.sleep(0.05)


LEGAL_CHARS = string.printable
ILLEGAL_CHARS = ' <>"|:*%?\\/#&;()'

def _is_legal(char):
    """
    Return true if the character is legal to have in a file name
    """
    return (char in LEGAL_CHARS) and (char not in ILLEGAL_CHARS)


def create_output_path(output_path, test_suite_name):
    """
    Create the full output path of a test case.
    Ensure no bad characters and no long path names.
    """
    output_path = abspath(output_path)
    safe_name = "".join(char if _is_legal(char) else '_' for char in test_suite_name) + "_"
    hash_name = hash_string(test_suite_name)

    if "YASA_SHORT_TEST_OUTPUT_PATHS" in os.environ:
        full_name = hash_name
    else:
        full_name = safe_name + hash_name

    return join(output_path, full_name)

