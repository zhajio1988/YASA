from globals import *
from readCfgFile import *
from utils import *
from tbInfo import *
import os
from yasaCli import yasaCli

class compileBuildBase(object):
    def __init__(self, cli=None, ini_file=None):
        """
        Argument object and input build file control

        :param args: The parsed argument namespace object
        :param ini_file: user input build file instead of defaultBuildFile
        :returns: None
        """
        self._cli = cli;
        self._args = self._cli.getParsedArgs()
        if  ini_file is not None and os.path.exists(ini_file):
            self.buildCfg = readBuildCfgFile(ini_file)
        else:
            self.buildCfg = readBuildCfgFile(defaultBuildFile())

    def prepareEnv(self):
        """
        Prepare build dir and testcase dirs

        :param description: A custom short description of the command line tool
        :param for_documentation: When used for user guide documentation
        :returns: The created :mod:`argparse` parser object
        """
        self.createRootWorkDir()
        if not self._args.simOnly:
            self.createBuildDir()
            self.createCompileCsh()

    def createRootWorkDir(self):
        createDir(defaultWorkDir())

    def createBuildDir(self):
        createDir(self._buildDir, self._args.clean)

    @property
    def _buildDir(self):
        pass

    def createCompileCsh(self):
        pass

class singleTestCompile(compileBuildBase):
    def __init__(self, cli=None, ini_file=None):
        super(singleTestCompile, self).__init__(cli, ini_file)
        self._build =  self.buildCfg.getBuild(self._args.build)

    @property
    def _buildDir(self):
        if self._args.unique_sim:
            return os.path.join(defaultWorkDir(), self._build.name)
        elif self._args.test:
            return os.path.join(defaultWorkDir(), self._args.test, self._build.name)

    #TODO: should add compile option from userCli and yasaCli
    def createCompileCsh(self):
        with open(os.path.join(self._buildDir, 'pre_compile.csh'), 'w') as f:
            for item in self.buildCfg.preCompileOption(self._args.build):
                f.write(item + '\n')
        with open(os.path.join(self._buildDir, 'compile.csh'), 'w') as f:
            f.write('#!/bin/csh -fe\n')
            for item in self.buildCfg.compileOption(self._args.build) + self._cli.userCliCompileOption():
                f.write(item + ' \\' + '\n' )
        with open(os.path.join(self._buildDir, 'post_compile.csh'), 'w') as f:
            for item in self.buildCfg.postCompileOption(self._args.build):
                f.write(item + '\n')

class groupTestCompile(compileBuildBase):
    def __init__(self, cli=None, ini_file=None):
        super(groupTestCompile, self).__init__(cli, ini_file)
        if  ini_file is not None and os.path.exists(ini_file):
            self.groupCfg = readGroupCfgFile(ini_file)
        else:
            self.groupCfg = readGroupCfgFile(defaultGroupFile())
        print(self._args.group)
        self._group = self.groupCfg.testGroup.getGroup(self._args.group)
        self._build =  self.buildCfg.getBuild(self._group.buildOption)

    @property
    def _buildDir(self):
        if self._args.group:
            return os.path.join(defaultWorkDir(), self._args.group, self._group.buildOption)

    def createCompileCsh(self):
        with open(os.path.join(self._buildDir, 'pre_compile.csh'), 'w') as f:
            for item in self.buildCfg.preCompileOption(self._group.buildOption):
                f.write(item + '\n')
        with open(os.path.join(self._buildDir, 'compile.csh'), 'w') as f:
            f.write('#!/bin/csh -fe\n')
            for item in self.buildCfg.compileOption(self._group.buildOption):
                f.write(item + ' \\' + '\n' )
        with open(os.path.join(self._buildDir, 'post_compile.csh'), 'w') as f:
            for item in self.buildCfg.postCompileOption(self._group.buildOption):
                f.write(item + '\n')

if __name__ == '__main__':
    import sys

    cli = yasaCli("Yet another simulation architecture")
    cli.parseArgs(sys.argv[1:])
    #userCliCfg.compileOption(args)
    compile = singleTestCompile(cli)
    compile.prepareEnv()
    #gpCompile = groupTestCompile(args)
    #gpCompile.prepareEnv()
