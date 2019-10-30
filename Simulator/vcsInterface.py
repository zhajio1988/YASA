"""
Interface for the Synopsys VCS MX simulator
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
import sys
sys.path.append("../")
from globals import *

class waveArgsAction(argparse.Action):
    """
    '-wave' argument Action callback subclass
    FIXME: because i used VCS version: vcs script version : I-2014.03
    which is not support '-lca' option, and if you want to dump fsdb waveform, 
    you must have -fsdb and -debug_pp option.  but if you new version, 
    -debug_pp is deprecated. so you can set -debug_access+pp
    and $VERDI_HOME env var for fsdb dump
    """
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
    """
    '-cov' argument Action callback subclass
    """    
    def __call__(self, parser, args, values, option = None):
        args.cov = values
        #TODO: Add -cm_dir and -cm_name options
        if args.cov == 'all':
            appendAttr(args, 'compileOption', '-cm_dir %s -cm line+cond+fsm+tgl+branch+assert' %(defaultCovDir()))
            appendAttr(args, 'simOption', '-cm line+cond+fsm+tgl+branch+assert')
            appendAttr(args, 'simOption', '+FCOV_EN')
        else:
            appendAttr(args, 'compileOption', '-cm_dir ' + defaultCovDir() + ' -cm ' + args.cov)
            appendAttr(args, 'simOption', '-cm ' + args.cov)
            appendAttr(args, 'simOption', ' +FCOV_EN')

class seedArgsAction(argparse.Action):
    """
    '-seed' argument Action callback subclass
    """     
    def __call__(self, parser, args, values, option = None):
        args.seed = values
        if args.seed == 0:
            appendAttr(args, 'simOption', '+ntb_random_seed=1')
        else:
            appendAttr(args, 'simOption', '+ntb_random_seed=%d' % args.seed)

class testArgsAction(argparse.Action):
    """
    '-t' argument Action callback subclass
    """      
    def __call__(self, parser, args, values, option = None):
        args.test = values
        if args.test:
            appendAttr(args, 'simOption', '+UVM_TESTNAME=%s' % args.test)

class vcsInterface(simulatorInterface): 
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
        #self._simCheck = vcsSimCheck()

    @property
    def simCheck(self):
        """
        Get the Singleton object of vcs sim check class
        """
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
    """
    VCS specified simulation results checker
    """    
    vcsErrorPattern = r'^Error-\[.*\]'    
    coreDumpPattern = r'Completed context dump phase'
    simEndPattern = r'V C S   S i m u l a t i o n   R e p o r t'
    timingViolationPattern = r'.*Timing violation.*'

    def __init__(self):
        super(vcsSimCheck, self).__init__()
        self._simEndPattern = re.compile(vcsSimCheck.simEndPattern)        
        self.setExcludeWarnPatterns(vcsSimCheck.vcsErrorPattern)
        self.setErrPatterns(vcsSimCheck.coreDumpPattern)
        self.setWarnPatterns(vcsSimCheck.timingViolationPattern)
