"""
Interface for the Cadence Xcelium simulator
"""
import os
import re
from os.path import join, dirname, abspath, relpath
import sys
import argparse
from utils import *
import logging
from .simulatorInterface import (simulatorInterface, run_command)
from .simCheck import *

LOGGER = logging.getLogger(__name__)

class waveArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.wave = values
        if args.wave == 'vpd':
            appendAttr(args, 'compileOption', '-access +r +define+DUMP_VPD')
        elif args.wave == 'fsdb':
            appendAttr(args, 'compileOption', '-access +r +define+DUMP_FSDB')
        elif args.wave == 'gui':
            appendAttr(args, 'compileOption', '-access +rwc +define+DUMP_FSDB')
            appendAttr(args, 'simOption', '-gui')

class covArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.cov = values
        if args.cov == 'all':
            appendAttr(args, 'compileOption', '-coverage all')
            appendAttr(args, 'simOption', '-coverage all')
            appendAttr(args, 'simOption', '+FCOV_EN')
        else:
            appendAttr(args, 'compileOption', '-cm ' + args.cov)
            appendAttr(args, 'simOption', '-cm ' + args.cov)
            appendAttr(args, 'simOption', ' +FCOV_EN')

class indagoArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.indago = values
        appendAttr(args, 'simOption', '-indago')
        if args.indago == 'all':
            appendAttr(args, 'compileOption', '-line -linedebug -classlinedebug -uvmlinedebug')
        else:
            appendAttr(args, 'compileOption', '-line ' + args.indago)

class seedArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.seed = values
        if args.seed == 0:
            appendAttr(args, 'simOption', '-svseed 0')
        else:
            appendAttr(args, 'simOption', '-svseed %d' % args.seed)

class testArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.test = values
        if args.test:
            appendAttr(args, 'simOption', '+UVM_TESTNAME=%s' % args.test)

class xceliumInterface(simulatorInterface):
    """
    Interface for the Cadence Xcelium simulator
    """

    name = "xrun"
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
        parser.add_argument('-indago', nargs='?', const='all', dest='indago', action=indagoArgsAction,
                            help='running Indago in interactive mode(instead of SimVision)')
        parser.add_argument('-cov', nargs='?', const='all', dest='cov', action=covArgsAction,
                            help='collect code coverage, default all kinds collect(line+cond+fsm+tgl+branch+assert')

        parser.add_argument('-seed', type=positive_int, dest='seed', default=0, action=seedArgsAction,
                            help='set testcase ntb random seed')

    @classmethod
    def find_prefix_from_path(cls):
        """
        Find xrun simulator from PATH environment variable
        """
        return cls.find_toolchain(['xrun'])

    def __init__(self):
        simulatorInterface.__init__(self)
        self._simCheck = xrunSimCheck()

    @property
    def simCheck(self):
        return self._simCheck;

    def compileExe(self):
        """
        Returns Xcelium compile executable cmd
        """
        return 'xrun'

    def simExe(self):
        """
        Returns Xcelium simv executable cmd
        """
        return 'xrun'

    #def executeCompile(self, buildDir, cmd, printer, timeout):
    #    """
    #    Xcelium doesn't need compile step, so override this function
    #    in base class, then do nothing 
    #    """
    #    pass

    def executeSimulataion(self, testWordDir, simCmd, timeout):
        if not run_command(simCmd, testWordDir, timeout):
            return False
        else:
            return True

class xrunSimCheck(simCheck):
    """
    xrun specified simulation results checker
    """  
    xrunErrorPattern = r'^Error-\[.*\]'    
    coreDumpPattern = r'Completed context dump phase'
    simEndPattern = r'xcelium> exit'    
    timingViolationPattern = r'.*Timing violation.*'

    def __init__(self):
        super(xrunSimCheck, self).__init__()
        self._simEndPattern = re.compile(xrunSimCheck.simEndPattern)        
        self.setErrPatterns(xrunSimCheck.xrunErrorPattern)    
        self.setErrPatterns(xrunSimCheck.coreDumpPattern)
        self.setWarnPatterns(xrunSimCheck.timingViolationPattern)        
