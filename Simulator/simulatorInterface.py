"""
Generic simulator interface
"""

import sys
import os
import subprocess
from ostools import Process, simplify_path
from exceptions import CompileError
from color_printer import NO_COLOR_PRINTER

class simulatorInterface(object):
    """
    Generic simulator interface
    """
    name = None
    supports_gui_flag = False

    # True if simulator supports ANSI colors in GUI mode
    supports_colors_in_gui = False

    def __init__(self):
        self._output_path = ''

    @property
    def output_path(self):
        return self._output_path

    @staticmethod
    def add_arguments(parser):
        """
        Add command line arguments
        """

    @staticmethod
    def find_executable(executable):
        """
        Return a list of all executables found in PATH
        """
        path = os.environ.get('PATH', None)
        if path is None:
            return []

        paths = path.split(os.pathsep)
        _, ext = os.path.splitext(executable)

        result = []
        if isfile(executable):
            result.append(executable)

        for prefix in paths:
            file_name = os.path.join(prefix, executable)
            if isfile(file_name):
                # the file exists, we have a shot at spawn working
                result.append(file_name)
        return result

    @classmethod
    def find_prefix(cls):
        """
        Find prefix by looking at YASA_<SIMULATOR_NAME>_PATH environment variable
        """
        prefix = os.environ.get("YASA_" + cls.name.upper() + "_PATH", None)
        if prefix is not None:
            return prefix
        return cls.find_prefix_from_path()

    @classmethod
    def find_prefix_from_path(cls):
        """
        Find simulator toolchain prefix from PATH environment variable
        """

    @classmethod
    def is_available(cls):
        """
        Returns True if simulator is available
        """
        return cls.find_prefix() is not None

    @classmethod
    def find_toolchain(cls, executables, constraints=None):
        """
        Find the first path prefix containing all executables
        """
        constraints = [] if constraints is None else constraints

        if not executables:
            return None

        all_paths = [[os.path.abspath(os.path.dirname(executables))
                      for executables in cls.find_executable(name)]
                     for name in executables]

        for path0 in all_paths[0]:
            if all([path0 in paths for paths in all_paths]
                   + [constraint(path0) for constraint in constraints]):
                return path0
        return None

    def merge_coverage(self, file_name, args):  # pylint: disable=unused-argument, no-self-use
        """
        Hook for simulator interface to creating coverage reports
        """
        raise RuntimeError("This simulator does not support merging coverage")

    def add_simulator_specific(self):
        """
        Hook for the simulator interface to add simulator specific things to the project
        """
        pass

    def compile(self, buildDir, cmd, printer=NO_COLOR_PRINTER):
        """
        Compile the project
        """
        self.add_simulator_specific()
        self.executeCompile(buildDir, cmd, printer)

    def simulate(self, testWordDir,  simCmd):
        self.executeSimulataion(testWordDir,  simCmd)

    def executeSimulataion(self, testcaseDir, simCmd):
        """
        Simulate
        """

    def executeCompile(self, buildDir, cmd, printer=NO_COLOR_PRINTER):
        """
        Execute compile step and prints status information and compile log file
        """
        try:
            #output = check_output(cmd, buildDir)
            if run_command(cmd, buildDir):
                #printer.write(output)
                printer.write("Compile passed", fg="gi")
                printer.write("\n")
            #except subprocess.CalledProcessError as err:
            else:
                #printer.write("=== Command output: ===\n%s\n" % err.output)
                printer.write("Compile failed", fg="ri")
                printer.write("\n")
                raise CompileError
        except OSError:
            raise OSError 
        finally:
            print("Log:")
            print(' '*4 + os.path.join(buildDir, 'compile.log\n'))

        return True

    @staticmethod
    def get_env():
        """
        Allows inheriting classes to overload this to modify environment variables. Return None for default environment
        """

def isfile(file_name):
    """
    Case insensitive os.path.isfile
    """
    if not os.path.isfile(file_name):
        return False

    return os.path.basename(file_name) in os.listdir(os.path.dirname(file_name))


def run_command(command, cwd=None):
    """
    Run a command
    """
    try:
        proc = Process(command, cwd=cwd)
        proc.consume_output()
        return True
    except Process.NonZeroExitCode:
        pass
    except KeyboardInterrupt:
        print()
        print("Caught Ctrl-C shutting down")        
        proc.terminate()
    return False


def check_output1(command, cwd=None, env=None):
    """
    Wrapper arround subprocess.check_output
    """
    try:
        output = subprocess.check_output(command,
                                         cwd=cwd,
                                         shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        err.output = err.output.decode("utf-8")
        raise err
    return output.decode("utf-8")

def check_output(command, cwd=None, env=None):
    """
    Wrapper arround subprocess.check_output
    """
    import easyprocess 
    try:
        with easyprocess(command, cwd=cwd, shell=True) as proc:
            print(proc.stdout.read())

    except subprocess.CalledProcessError as err:
        err.output = err.output.decode("utf-8")
        raise err
    #return output.decode("utf-8")
