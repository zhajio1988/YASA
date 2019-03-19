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
"""
Functionality to handle lists of test suites and filtering of them
"""

from test_report import (PASSED, WARNED, FAILED)


class TestList(object):
    """
    A list of test suites
    """
    def __init__(self):
        self._test_suites = []

    def add_suite(self, test_suite):
        self._test_suites.append(test_suite)

    def add_test(self, test_case):
        """
        Add a single test that is automatically wrapped into a test suite
        """
        test_suite = TestSuiteWrapper(test_case)
        self._test_suites.append(test_suite)

    def keep_matches(self, test_filter):
        """
        Keep only testcases matching any pattern
        """
        self._test_suites = [test for test in self._test_suites
                             if test.keep_matches(test_filter)]

    @property
    def num_tests(self):
        """
        Return the number of tests within
        """
        num_tests = 0
        for test_suite in self:
            num_tests += len(test_suite.test_names)
        return num_tests

    @property
    def test_names(self):
        """
        Return the names of all tests
        """
        names = []
        for test_suite in self:
            names += test_suite.test_names
        return names

    def __iter__(self):
        return iter(self._test_suites)

    def __len__(self):
        return len(self._test_suites)

    def __getitem__(self, idx):
        return self._test_suites[idx]


class TestSuiteWrapper(object):
    """
    Wrapper which creates a test suite from a single test case
    """
    def __init__(self, test_case):
        self._test_case = test_case

    @property
    def test_names(self):
        return [self._test_case.name]

    @property
    def name(self):
        return self._test_case.name

    @property
    def test_result_file(self):
        return self._test_case.test_result_file

    @property
    def test_information(self):
        return {self.name: self._test_case.test_information}

    def keep_matches(self, test_filter):
        return test_filter(name=self._test_case.name,
                           attribute_names=self._test_case.attribute_names)

    def run(self, *args, **kwargs):
        """
        Run the test suite and return the test results for all test cases
        """
        test_ok = self._test_case.run()
        return  test_ok

        #return {self._test_case.name: PASSED if test_ok else FAILED}
