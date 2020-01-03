"""
Create simulator instances
"""

import os
from .vcsInterface import vcsInterface
from .incisiveInterface import incisiveInterface
from .xceliumInterface import xceliumInterface
#from .simulatorInterface import (BooleanOption, ListOfStringOption)

class simulatorFactory(object):
    """
    Create simulator instances
    """

    @staticmethod
    def supported_simulators():
        """
        Return a list of supported simulator classes
        """
        #TODO: add simulator interface here
        return [vcsInterface,
                incisiveInterface,
                xceliumInterface,
                ]

    def select_simulator(self):
        """
        Select simulator class, either from YASA_SIMULATOR environment variable
        or the first available
        """
        available_simulators = self._detect_available_simulators()
        name_mapping = {simulator_class.name: simulator_class for simulator_class in self.supported_simulators()}
        if not available_simulators:
            raise RuntimeError(
                ("Don't have available simulators. "
                    "Supported simulators are %s")
                % list(name_mapping.keys()))
        environ_name = "YASA_SIMULATOR"
        if environ_name in os.environ:
            simulator_name = os.environ[environ_name]
            if simulator_name not in name_mapping:
                raise RuntimeError(
                    ("Simulator from " + environ_name + " environment variable %r is not supported. "
                     "Supported simulators are %r")
                    % (simulator_name, name_mapping.keys()))
            simulator_class = name_mapping[simulator_name]
        else:
            simulator_class = available_simulators[0]

        return simulator_class

    def add_arguments(self, parser, group):
        """
        Add command line arguments to parser
        """
        #TODO: Can add global simulator arguments here
        #parser.add_argument('-g', '--gui',
        #                    action="store_true",
        #                    default=False,
        #                    help=("Open test case(s) in simulator gui with top level pre loaded"))
        environ_name = "YASA_SIMULATOR"
        if environ_name in os.environ:
            simulator_name = os.environ[environ_name]
        for sim in self.supported_simulators():
            if sim.name == simulator_name:
                sim.add_arguments(parser, group)
        #simulator = self.select_simulator()
        #simulator.add_arguments(parser, group)

    def __init__(self):
        pass
        #self._compile_options = self._extract_compile_options()
        #self._sim_options = self._extract_sim_options()

    def _detect_available_simulators(self):
        """
        Detect available simulators and return a list
        """
        return [simulator_class
                for simulator_class in self.supported_simulators()
                if simulator_class.is_available()]

    @property
    def has_simulator(self):
        return bool(self._detect_available_simulators())


SIMULATOR_FACTORY = simulatorFactory()
