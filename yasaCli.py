import argparse
from os.path import join, abspath
#from Simulator.simulator_factory import SIMULATOR_FACTORY
from about import version
from globals import *
import userCli

class yasaCli(object):
    """
    Yasa command line interface
    """

    def __init__(self, description=None):
        """
        :param description: A custom short description of the command line tool
        """
        self.parser = _create_argument_parser(description)
        self.userCliCfg = userCli.userCliCfg(self.parser)
        self.userCliCfg.addArguments()
    def parse_args(self, argv=None):
        """
        Parse command line arguments

        :param argv: Use explicit argv instead of actual command line argument
        :returns: The parsed argument namespace object
        """
        return self.parser.parse_args(args=argv)


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
    group.add_argument('-t', '-test', dest='test', action='store',  help='assign test name')
    group.add_argument('-g', '-group', dest='group', action='store', help='assign test group name')
    group.add_argument('-show', dest='show', choices=['test', 'group', 'build'], help='show test list, group list or build list')
    argParser.add_argument('-so', '-simonly', dest='simOnly', action='store_true', help='Only run simulation without compile step')
    argParser.add_argument('-co', '-componly', dest='compOnly', action='store_true', help='Only compile without running tests')
    argParser.add_argument('-b', '-build', dest='build', action='store', help='assign a specific build')
    argParser.add_argument('-w', '-wave', nargs='?', const='fsdb', dest='wave', action='store', choices=['vpd', 'fsdb', 'gui'], help='dump waveform(vpd or fsdb), default fsdb')
    argParser.add_argument('-cov', nargs='?',  const='all', dest='cov', action='store', help='assign a specific build')
    argParser.add_argument('-test_prefix', dest='test_prefix', default='', action='store', help='add testcase prefix')
    argParser.add_argument('-seed', type=positive_int, dest='seed', default=1, action='store', help='set testcase ntb random seed')
    argParser.add_argument('-r', '-repeat', type=positive_int, dest='repeat', default=1, action='store', help='testcase will random run in given repeat round')
    argParser.add_argument('-c', '-clean', dest='clean', action='store_true', help='Remove output build dir')

    argParser.add_argument("-with-attributes",
                        default=None,
                        action="append",
                        help="Only select tests with these attributes set")

    argParser.add_argument("-without-attributes",
                        default=None,
                        action="append",
                        help="Only select tests without these attributes set")

    argParser.add_argument('-fail-fast', action='store_true',
                        default=False,
                        help='Stop immediately on first failing test')

    argParser.add_argument('-o', '-output-path',
                        default=default_output_path,
                        help='Output path for compilation and simulation artifacts')

    argParser.add_argument('-x', '-xunit-xml',
                        default=None,
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
                        help=('Exit with code 0 even if a test failed. '
                              'Still exits with code 1 on fatal errors such as compilation failure'))

    argParser.add_argument('-dont-catch-exceptions',
                        default=False,
                        action="store_true",
                        help=('Let exceptions bubble up all the way. '
                              'Useful when running with "python -m pdb".'))

    argParser.add_argument('-v', '-verbose', action="store_true",
                        default=False,
                        help='Print test output immediately and not only when failure')

    argParser.add_argument('-q', '--quiet', action="store_true",
                        default=False,
                        help='Do not print test output even in the case of failure')

    argParser.add_argument('-no-color', action='store_true',
                        default=False,
                        help='Do not color output')

    argParser.add_argument('-log-level',
                        default="warning",
                        choices=["info", "error", "warning", "debug"],
                        help=("Log level of Yasa internal python logging. "
                              "Used for debugging"))

    argParser.add_argument('-p', '-num-threads', type=positive_int,
                        default=1,
                        help=('Number of tests to run in parallel. '
                              'Test output is not continuously written in verbose mode with p > 1'))

    argParser.add_argument("-u", "-unique-sim",
                        action="store_true",
                        default=False,
                        help="Do not re-use the same simulator process for running different test cases (slower)")

    argParser.add_argument("-export-json",
                        default=None,
                        help="Export project information to a JSON file.")

    argParser.add_argument('-version', action='version', version=version())

    #SIMULATOR_FACTORY.add_arguments(argParser)

    return argParser

def positive_int(val):
    """
    ArgumentParse positive int check
    """
    try:
        ival = int(val)
        assert ival > 0
        return ival
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError("'%s' is not a valid positive int" % val)

def _argParser_for_documentation():
    """
    Returns an argparse object used by sphinx for documentation in user_guide.rst
    """
    return _create_argument_parser(for_documentation=True)

if __name__ == '__main__':
    import sys

    cli = yasaCli("Yet another simulation architecture top scripts")
    #print(cli.parse_args(sys.argv[1:]))
    #print(vars(cli.parse_args(sys.argv[1:])))
    #print(cli.parse_args(['-h']))
    args = cli.parse_args(sys.argv[1:])
    print(args.sim_option)
    print(args.wave_name)
    print(args.prof)
    print(cli.userCliCfg.compileOption(args))
    print(cli.userCliCfg.simOption(args))
    print("end")
