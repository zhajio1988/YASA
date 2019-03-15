"""
Interface for the Synopsys VCS MX simulator
"""
import os
import re
from os.path import join, dirname, abspath, relpath
import subprocess
import sys
import argparse
from utils import *
import logging
from ostools import write_file, file_exists
from .simulatorInterface import (simulatorInterface, run_command)
from .simCheck import *

LOGGER = logging.getLogger(__name__)

class waveArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.wave = values
        if args.wave == 'vpd':
            appendAttr(args, 'compileOption', '-lca -kdb -debug_access+pp +define+DUMP_VPD')
        elif args.wave == 'fsdb':
            appendAttr(args, 'compileOption', '-lca -kdb -debug_access+pp +define+DUMP_FSDB')
        elif args.wave == 'gui':
            appendAttr(args, 'compileOption', '-lca -kdb -debug_access+all +define+DUMP_FSDB')
            appendAttr(args, 'simOption', '-lca  -verdi')

class covArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.cov = values
        #TODO: Add -cm_dir and -cm_name options
        if args.cov == 'all':
            appendAttr(args, 'compileOption', '-cm line+cond+fsm+tgl+branch+assert')
            appendAttr(args, 'simOption', '-cm line+cond+fsm+tgl+branch+assert')
            appendAttr(args, 'simOption', '+FCOV_EN')
        else:
            appendAttr(args, 'compileOption', '-cm ' + args.cov)
            appendAttr(args, 'simOption', '-cm ' + args.cov)
            appendAttr(args, 'simOption', ' +FCOV_EN')

class seedArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.seed = values
        if args.seed == 0:
            appendAttr(args, 'simOption', '+ntb_random_seed=1')
        else:
            appendAttr(args, 'simOption', '+ntb_random_seed=%d' % args.seed)

    #def generateSeed(self):
    #    for i in range(self._args.repeat):
    #        if self.args.seed == 0:
    #            seed = '%d' % (randint(1, 0xffffffff))
    #        else:
    #            seed = self._args.seed
    #        self._seeds.append(seed)

#class seedArgsAction(argparse.Action):
#    def __call__(self, parser, args, values, option = None):
#        print("debug point1", args.repeat)        
#        for i in range(args.repeat):
#            if values == 0:
#                seed = '%d' % (randint(1, 0xffffffff))
#            else:
#                seed = values
#            print(seed)
        #if args.seed == 0:
        #    appendAttr(args, 'simOption', ' +ntb_random_seed=1')
        #else:
        #   appendAttr(args, 'simOption', ' +ntb_random_seed=%d' % args.seed)

class testArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.test = values
        if args.test:
            appendAttr(args, 'simOption', '+UVM_TESTNAME=%s' % args.test)

class vcsInterface(simulatorInterface):  # pylint: disable=too-many-instance-attributes
    """
    Interface for the Synopsys VCS MX simulator
    """

    name = "vcs"
    supports_gui_flag = True

    @staticmethod
    def add_arguments(parser, group):
        """
        Add command line arguments
        """
        group.add_argument('-t', '-test', dest='test', action=testArgsAction, help='assign test name')

        parser.add_argument('-w', '-wave', nargs='?', const='fsdb', dest='wave', action=waveArgsAction,
                            choices=['vpd', 'fsdb', 'gui'],
                            help='dump waveform(vpd or fsdb), default fsdb')
        parser.add_argument('-cov', nargs='?', const='all', dest='cov', action=covArgsAction,
                            help='collect code coverage, default all kinds collect(line+cond+fsm+tgl+branch+assert')

        parser.add_argument('-seed', type=positive_int, dest='seed', default=0, action=seedArgsAction,
                            help='set testcase ntb random seed')

    @classmethod
    def find_prefix_from_path(cls):
        """
        Find vcs simulator from PATH environment variable
        """
        return cls.find_toolchain(['vcs'])

    def __init__(self):
        simulatorInterface.__init__(self)
        self._simCheck = vcsSimCheck()

    @property
    def simCheck(self):
        return self._simCheck;

    def compileExe(self):
        """
        Returns vcs compile executable cmd
        """
        return 'vcs'

    def simExe(self):
        """
        Returns vcs simv executable cmd
        """
        return 'simv'


    def executeSimulataion(self, testWordDir, simCmd):
        if not run_command(simCmd, cwd=testWordDir):
            return False
        else:
            return True

class vcsSimCheck(simCheck):
    vcsErrorPattern = r'^Error-\[.*\]'    
    coreDumpPattern = r'Completed context dump phase'
    simEndPattern = r' V C S   S i m u l a t i o n   R e p o r t'    
    timingViolationPattern = r'.*Timing violation.*'

    def __init__(self):
        super(vcsSimCheck, self).__init__()
        self._simEndPattern = re.compile(vcsSimCheck.simEndPattern)        
        self.setExcludeWarnPatterns(vcsSimCheck.vcsErrorPattern)    
        self.setErrPatterns(vcsSimCheck.coreDumpPattern)
        self.setWarnPatterns(vcsSimCheck.timingViolationPattern)        
