import os
import sys
import ostools
from test_report import (PASSED, WARNED, FAILED)
from globals import *

class testcaseSuite(object):
    """
    A test case to be run in an independent simulation
    """
    def __init__(self, testsWordDir, simCmd, simulator_if):
        self._dir = testsWordDir
        self._simCmd = simCmd
        self._test = os.path.basename(testsWordDir)
        self.name = os.path.basename(testsWordDir)
        self._run = TestRun(simulator_if=simulator_if,
                            testWordDir=self._dir,
                            simCmd = self._simCmd,
                            test_cases=[self._test])

    @property
    def test_result_file(self):
        return self._run.get_test_result()

    @property
    def test_information(self):
        """
        Returns the test information
        """
        return self._test

    def run(self, *args, **kwargs):
        """
        Run the test case using the output_path
        """
        results = self._run.run(*args, **kwargs)
        return results

class TestRun(object):
    """
    A single simulation run yielding the results for one or several test cases
    """

    def __init__(self, simulator_if, testWordDir, simCmd, test_cases):
        self._simulator_if = simulator_if
        self._testWordDir = testWordDir
        self._simCmd = simCmd
        self._test_cases = test_cases

    def set_test_cases(self, test_cases):
        self._test_cases = test_cases

    def get_test_result(self):
        return get_result_file_name(self._testWordDir)

    def run(self):
        """
        Run selected test cases within the test suite

        Returns a dictionary of test results
        """
        results = {}
        for name in self._test_cases:
            results[name] = FAILED

        # Ensure result file exists
        ostools.write_file(get_result_file_name(self._testWordDir), "")

        sim_ok = self._simulate()

        results = self._read_test_results(file_name=get_result_file_name(self._testWordDir))

        # Do not run post check unless all passed
        for status in results.values():
            if status != PASSED:
                return results

        #if not self._config.call_post_check(output_path, read_output):
        #    for name in self._test_cases:
        #        results[name] = FAILED

        return results

    def _simulate(self):
        """
        Run simulation
        """

        return self._simulator_if.simulate(
            testWordDir=self._testWordDir,
            simCmd = self._simCmd)

    def _read_test_results(self, file_name):
        """
        Read test results from vunit_results file
        """

        results = {}
        for name in self._test_cases:
            results[name] = FAILED

        if not ostools.file_exists(file_name):
            return results

        test_results = ostools.read_file(file_name)
        test_suite_done = False

        (userSimCheckFunc, userSimCheckFile) = userSimCheck()
        if userSimCheckFile:
            sys.path.append(os.path.dirname(userSimCheckFile))
            from userSimCheck import userSimCheck as simCheck
            checker=simCheck()
        else:
            checker=self._simulator_if.simCheck 

        checker.resetStatus()
        for line in test_results.splitlines():
            line = line.strip()
            checker.check(line)
        status, reasonMsg = checker.status

        for test_name in self._test_cases:
            if status == 'PASS':
                results[test_name] = PASSED
            else:
                if status == 'WARN':
                    results[test_name] = WARNED
                elif status == 'FAIL':
                    results[test_name] = FAILED

        for test_name in results:
            if test_name not in self._test_cases:
                raise RuntimeError("Got unknown test case %s" % test_name)

        return results

def get_result_file_name(output_path):
    return os.path.join(output_path, "sim.log")
