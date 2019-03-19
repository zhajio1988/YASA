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
import argparse
import sys
from os.path import join, abspath
from Simulator.simulatorFactory import SIMULATOR_FACTORY
from about import version, doc
from globals import *
from utils import *
from userCli import userCli
from lsfCli import lsfCli

class yasaCli(object):
    """
    Yasa command line interface
    """

    def __init__(self, description=None):
        """
        :param description: A custom short description of the command line tool
        add userCli object and lsfCli object for argparser
        add _check function
        """
        self.parsedArgs = None
        self.parser = _create_argument_parser(description)
        self.subParsers = self.parser.add_subparsers(dest='subparsers')        
        self.userCli = userCli(self.parser)
        self.userCli.addArguments()
        self.lsfCli =lsfCli(self.subParsers)        
        self.lsfCli.addArguments()

    def parseArgs(self, argv=None):
        """
        Parse command line arguments

        :param argv: Use explicit argv instead of actual command line argument
        """
        self.parsedArgs = self.parser.parse_args(args=argv)
        self._check()
        self.userCli.setParsedArgs(self.parsedArgs)
        self.lsfCli.setParsedArgs(self.parsedArgs)

    def _check(self):
        pass

    def getParsedArgs(self):
        return self.parsedArgs

    def userCliCompileOption(self):
        """
        return compilation option extract from userCli command
        """
        return self.userCli.compileOption()

    def userCliSimOption(self):
        """
        return simulation option extract from userCli command
        """        
        return self.userCli.simOption()

def _create_argument_parser(description=None, for_documentation=False):
    """
    Create the argument parser

    :param description: A custom short description of the command line tool
    :param for_documentation: When used for user guide documentation
    :returns: The created :mod:`argparse` parser object
    """
    if description is None:
        description = 'Yet another simulation architecture, version %s' % version()

    if for_documentation:
        default_output_path = "./yasa_out"
    else:
        default_output_path = join(abspath(os.getcwd()), "yasa_out")

    argParser = argparse.ArgumentParser(description=description)
    group = argParser.add_mutually_exclusive_group()
    group.add_argument('-g', '-group', 
                        dest='group', 
                        action='store', 
                        help='assign test group name')

    group.add_argument('-show', 
                        dest='show', 
                        choices=['test', 'group', 'build'], 
                        help='show test list, group list or build list')

    argParser.add_argument('-so', '-simonly', 
                        dest='simOnly', 
                        action='store_true', 
                        help='Only run simulation without compile step')

    argParser.add_argument('-co', '-componly', 
                        dest='compOnly', 
                        action='store_true', 
                        help='Only compile without running tests')

    argParser.add_argument('-b', '-build', 
                        dest='build', 
                        action='store', 
                        help='assign a specific build')

    argParser.add_argument('-test_prefix', 
                        dest='testPrefix', 
                        default='', 
                        action='store', 
                        help='add testcase prefix')

    argParser.add_argument('-r', '-repeat', 
                        type=positive_int, 
                        dest='repeat', 
                        default=1, 
                        action='store', 
                        help='testcase will random run in given repeat round')

    argParser.add_argument('-c', '-clean', 
                        dest='clean', 
                        action='store_true', 
                        help='Remove output build dir')

    argParser.add_argument('-fail-fast', action='store_true',
                        default=False,
                        dest = 'fail_fast',
                        help='Stop immediately on first failing test')

    argParser.add_argument('-o', '-output-path',
                        default=default_output_path,
                        dest = 'output_path',
                        action='store',
                        help='Output path for compilation and simulation artifacts')

    argParser.add_argument('-x', '-xunit-xml',
                        nargs='?', 
                        const='yasa.xml',
                        dest='xunit_xml',
                        action='store',
                        help='Xunit test report .xml file')

    argParser.add_argument('-xunit-xml-format',
                        choices=['jenkins', 'bamboo'],
                        default='jenkins',
                        help=('Only valid with --xunit-xml argument. '
                              'Defines where in the XML file the simulator output is stored on a failure. '
                              '"jenkins" = Output stored in <system-out>, '
                              '"bamboo" = Output stored in <failure>.'))

    argParser.add_argument('-exit-0',
                        default=False,
                        action="store_true",
                        dest = 'exit_0',
                        help=('Exit with code 0 even if a test failed. '
                              'Still exits with code 1 on fatal errors such as compilation failure'))

    argParser.add_argument('-dont-catch-exceptions',
                        default=False,
                        action="store_true",
                        dest = 'dont_catch_exceptions',
                        help=('Let exceptions bubble up all the way. '
                              'Useful when running with "python -m pdb".'))

    argParser.add_argument('-v', '-verbose', action="store_true",
                        default=False,
                        dest = 'verbose',
                        help='Print test output immediately and not only when failure')

    argParser.add_argument('-q', '--quiet', action="store_true",
                        default=False,
                        help='Do not print test output even in the case of failure')

    argParser.add_argument('-no-color', action='store_true',
                        default=False,
                        dest='no_color',                        
                        help='Do not color output')

    argParser.add_argument('-log-level',
                           default="warning",
                           choices=["info", "error", "warning", "debug"],
                           help=("Log level of Yasa internal python logging. "
                              "Used for debugging"))

    argParser.add_argument('-p', '-num-threads', type=positive_int,
                           default=1,
                           dest ='num_threads',
                           action = 'store',
                           help=('Number of tests to run in parallel. '
                              'Test output is not continuously written in verbose mode with p > 1'))

    argParser.add_argument("-u", "-unique_sim",
                        action="store_true",
                        dest='unique_sim',
                        help="Do not re-use the same simulator process for running different test cases (slower)")

    #argParser.add_argument("-export-json",
    #                    default=None,
    #                    help="Export project information to a JSON file.")

    argParser.add_argument('-version', action='version', version=version())
    argParser.add_argument('-doc', dest='docFile', action="store_true", help="print doc file")
    
    SIMULATOR_FACTORY.add_arguments(argParser, group)

    return argParser

def _argParser_for_documentation():
    """
    Returns an argparse object used by sphinx for documentation in user_guide.rst
    """
    return _create_argument_parser(for_documentation=True)

#if __name__ == '__main__':
#    import sys
#
#    cli = yasaCli("Yet another simulation architecture top scripts")
#    #print(cli.parseArgs(sys.argv[1:]))
#    #print(vars(cli.parseArgs(sys.argv[1:])))
#    #print(cli.parseArgs(['-h']))
#    cli.parseArgs(sys.argv[1:])
#    args = cli.getParsedArgs()
#    print(args.sim_option)
#    print(args.wave_name)
#    print(args.prof)
#    print(args.seed)
#    print(args.compOnly)
#    print('11', args.build)
#
#    #print(args.simOption)
#    #print(args.compileOption)
#    print(cli.userCli.compileOption())
#    print(cli.userCli.simOption())
#    print(cli.userCliCompileOption())
#    print(cli.userCliSimOption())
#    print(args.lsfOptions)
#    print(args.subparsers)
#    print("end")
