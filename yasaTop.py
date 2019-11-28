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
import sys
import traceback
import logging
import os
from os.path import exists, abspath, join
from database import PickledDataBase, DataBase
import ostools
from yasaCli import yasaCli
from Simulator.simulatorFactory import SIMULATOR_FACTORY
from test_list import TestList
from testCaseSuite import testcaseSuite
from color_printer import (COLOR_PRINTER,
                           NO_COLOR_PRINTER)
from test_runner import TestRunner
from test_report import TestReport
from exceptions import CompileError
from compileBuild import singleTestCompile, groupTestCompile
from about import version, doc

LOGGER = logging.getLogger(__name__)

class yasaTop(object):
    """
    YASA top scripts
    """

    def __init__(self, argv):
        self._cli = yasaCli("Yet another simulation architecture® top scripts")
        self._cli.parseArgs(argv=argv)
        self._args = self._cli.getParsedArgs()
        self._configure_logging(self._args.log_level)
        self._output_path = abspath(self._args.output_path)
        if self._args.no_color:
            self._printer = NO_COLOR_PRINTER
        else:
            self._printer = COLOR_PRINTER

        self._simulator_class = SIMULATOR_FACTORY.select_simulator()

        #TODO: Use default simulator options if no simulator was present
        #if self._simulator_class is None:
        #    self._simulator_class = simulatorInterface()

        #TODO: no usage
        #self._create_output_path(self._args.clean)

        self._checkArgs(self._args)

        #database = self._create_database()

    def _checkArgs(self, args):
        """
        check parsed arguments, in case of input nothing from command line 
        if you type
        >>> YASAsim -doc
        will print doc content, then exit with 0
        """
        if args.docFile:
            print(doc())
            sys.exit(0)
        if not args.compOnly and not args.build:
            if args.show is None:
                if args.group is None and args.test is None:
                    #TODO: this check should be more robust
                    self._printer.write('One of argument" -t/-test and -g/-group"must be supplied, when not use argument -show\n', fg='ri')
                    sys.exit(1)

    def _create_database(self):
        """
        Create a persistent database to store expensive parse results

        Check for Python version used to create the database is the
        same as the running python instance or re-create
        """
        project_database_file_name = join(self._output_path, "project_database")
        create_new = False
        key = b"version"
        version = str((9, sys.version)).encode()
        database = None
        try:
            database = DataBase(project_database_file_name)
            create_new = (key not in database) or (database[key] != version)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:  # pylint: disable=bare-except
            traceback.print_exc()
            create_new = True

        if create_new:
            database = DataBase(project_database_file_name, new=True)
        database[key] = version

        return PickledDataBase(database)

    @staticmethod
    def _configure_logging(log_level):
        """
        Configure logging based on log_level string
        """
        level = getattr(logging, log_level.upper())
        logging.basicConfig(filename=None, format='%(levelname)7s - %(message)s', level=level)

    def main(self, post_run=None):
        """
        Run yasa main function and exit

        :param post_run: A callback function which is called after
          running tests. The function must accept a single `results`
          argument which is an instance of :class:`.Results`
        """
        try:
            all_ok = self._main(post_run)
        except KeyboardInterrupt:
            sys.exit(1)
        except CompileError:
            sys.exit(1)
        except SystemExit as e:
            sys.exit(e.code)
        except: 
            if self._args.dont_catch_exceptions:
                raise
            traceback.print_exc()
            sys.exit(1)

        if (not all_ok) and (not self._args.exit_0):
            sys.exit(1)

        sys.exit(0)

    def _create_tests(self, testWorkDir, simCmd, simulator_if):
        """
        Create all test cases corresponding testsuites
        """

        test_list = TestList()
        for dir in testWorkDir:
            test_list.add_test(testcaseSuite(dir, simCmd, simulator_if=simulator_if))

        return test_list

    def _main(self, post_run):
        """
        Base yasa main function without performing exit
        support compile only and sim only option
        >>> YASAsim -b candy_lover -co -u
        >>> YASAsim -t sanity1 -co
        """

        if self._args.compOnly:
            return self._main_compile_only()

        all_ok = self._main_run(post_run)
        return all_ok

    def _create_simulator_if(self):
        """
        Create new simulator instance
        """

        if self._simulator_class is None:
            LOGGER.error("No available simulator detected.\n"
            "Simulator binary folder must be available in PATH environment variable.\n"
            "Simulator binary folder can also be set the in YASA_<SIMULATOR_NAME>_PATH environment variable.\n")
            exit(1)

        return self._simulator_class()

    def _main_run(self, post_run):
        """
        Main with running tests
        support single testcase running several rounds with specified seed or random seed
        or running a group of testcases(each testcase with specified option) 
        """
        simulator_if = self._create_simulator_if()
        simulator_if.sim_timeout = self._args.sim_timeout;

        if self._args.group:
            compile = groupTestCompile(cli=self._cli, simulator_if=simulator_if)
            compile.prepareEnv()            
        else:
            compile = singleTestCompile(cli=self._cli, simulator_if=simulator_if)
            compile.prepareEnv()   
        test_list = self._create_tests(compile._testCaseWorkDir, compile.simCmd(), simulator_if)
        if not self._args.simOnly:
            self._compile(compile._buildDir, compile.compileCmd(), simulator_if)

        start_time = ostools.get_time()
        report = TestReport(printer=self._printer, filePath=compile._buildDir)

        try:
            self._run_test(test_list, report)
        except KeyboardInterrupt:
            print()
            LOGGER.debug("_main: Caught Ctrl-C shutting down")
        finally:
            del test_list

        report.set_real_total_time(ostools.get_time() - start_time)
        report.print_str()

        if post_run is not None:
            post_run(results=Results(simulator_if))

        del simulator_if

        if self._args.xunit_xml is not None:
            xml = report.to_junit_xml_str(self._args.xunit_xml_format)
            ostools.write_file(self._args.xunit_xml, xml)

        return report.all_ok()

    def _main_compile_only(self):
        """
        Main function when only compiling
        """
        simulator_if = self._create_simulator_if()

        if self._args.group:
            compile = groupTestCompile(cli=self._cli, simulator_if=simulator_if)
            compile.prepareEnv()
        else:
            compile = singleTestCompile(cli=self._cli, simulator_if=simulator_if)
            compile.prepareEnv()     
        test_list = self._create_tests(compile._testCaseWorkDir, compile.simCmd(), simulator_if)

        self._compile(compile._buildDir, compile.compileCmd(), simulator_if)        
        return True

    def _create_output_path(self, clean):
        """
        Create or re-create the output path if necessary
        """
        if clean:
            ostools.renew_path(self._output_path)
        elif not exists(self._output_path):
            os.makedirs(self._output_path)

    def _compile(self, buildDir, cmd, simulator_if):
        """
        Compile entire tb
        """
        simulator_if.compile(buildDir, cmd, self._printer, self._args.comp_timeout)

    def _run_test(self, test_cases, report):
        """
        Run the test suites and return the report
        """

        if self._args.verbose:
            verbosity = TestRunner.VERBOSITY_VERBOSE
        elif self._args.quiet:
            verbosity = TestRunner.VERBOSITY_QUIET
        else:
            verbosity = TestRunner.VERBOSITY_NORMAL

        runner = TestRunner(report,
                            verbosity=verbosity,
                            num_threads=self._args.num_threads,
                            fail_fast=self._args.fail_fast,
                            dont_catch_exceptions=self._args.dont_catch_exceptions,
                            no_color=self._args.no_color)
        runner.run(test_cases)

class Results(object):
    """
    Gives access to results after running tests.
    """

    def __init__(self, simulator_if):
        self._simulator_if = simulator_if

    def merge_coverage(self, file_name, args=None):
        """
        Create a merged coverage report from the individual coverage files

        :param file_name: The resulting coverage file name.
        :param args: The tool arguments for the merge command. Should be a list of strings.
        """

        self._simulator_if.merge_coverage(file_name=file_name, args=args)

if __name__ == '__main__':
    yasa = yasaTop(sys.argv[1:])
    yasa.main()
