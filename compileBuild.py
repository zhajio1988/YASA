import os
import sys
from globals import *
from readCfgFile import *
from utils import *
import tbInfo
from yasaCli import yasaCli
from random import randint

class compileBuildBase(object):
    def __init__(self, cli=None, ini_file=None, simulator_if=None):
        """
        Argument object and input build file control

        :param args: The parsed argument namespace object
        :param ini_file: user input build file instead of defaultBuildFile
        :returns: None
        """
        self._cli = cli
        self._simulator_if = simulator_if
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
        if not self._args.compOnly:
            self.createCaseDir()
            self.genTestscaseSimCsh()

    def createRootWorkDir(self):
        createDir(defaultWorkDir())

    def createBuildDir(self):
        createDir(self._buildDir, self._args.clean)

    def createCaseDir(self):
        if self._args.unique_sim:
            createDir(self._testcaseRootDir, self._args.clean)

    @property
    def _buildDir(self):
        pass

    @property
    def _testcaseRootDir(self):
        pass

    def _check(self):
        pass

    def createCompileCsh(self):
        raise NotImplementedError

    def createSimCsh(self, testcaseDir=None):
        raise NotImplementedError

class singleTestCompile(compileBuildBase):
    def __init__(self, cli=None, ini_file='', simulator_if=None):
        super(singleTestCompile, self).__init__(cli, ini_file, simulator_if)
        self._build =  self.buildCfg.getBuild(self._args.build)
        self._testList = tbInfo.testList()
        self.setTestlist()
        self._check()
        self._seeds = []
        self._testcasesDir = []
        self.generateSeed()

    @property
    def _buildDir(self):
        if self._args.unique_sim:
            return os.path.join(defaultWorkDir(), self._build.name)
        elif self._args.test:
            return os.path.join(defaultWorkDir(), self._testcaseRootDir, self._build.name)

    @property
    def _testcaseRootDir(self):
        return os.path.join(defaultWorkDir(), self._args.testPrefix + '__' + self._args.test if self._args.testPrefix else self._args.test)

    @property
    def testList(self):
        return self._testList

    def setTestlist(self):
        if self._build.testDir is not None:
            self._testList.testDir = self._build.testDir
        else:
            self._testList.testDir = defaultTestDir()
        tbInfo.testlist.setTestLists(self._build.name, self._testList)

    def _check(self):
        if not self.testList.check(self._args.test) and self._args.test:
            print('test: %s is unknown' % self._args.test)
            tbInfo.show('test')
            raise ValueError('test: %s is unknown' % self._args.test)
        elif self._args.show:
            tbInfo.show(self._args.show)
            sys.exit(0)

    def createCompileCsh(self):
        self._testList.genTestFileList(self._buildDir)
        with open(os.path.join(self._buildDir, 'pre_compile.csh'), 'w') as f:
            for item in self.buildCfg.preCompileOption(self._args.build):
                f.write(item + '\n')
        with open(os.path.join(self._buildDir, 'compile.csh'), 'w') as f:
            f.write('#!/bin/csh -fe\n')
            f.write(self._simulator_if.compileExe() + ' \\' + '\n')
            for index, item in enumerate(self.compileCshContent()):
                if index == len(self.compileCshContent())-1:
                    f.write('\t' + item + '\n')
                else:
                    f.write('\t' + item + ' \\' + '\n')
        with open(os.path.join(self._buildDir, 'post_compile.csh'), 'w') as f:
            for item in self.buildCfg.postCompileOption(self._args.build):
                f.write(item + '\n')

    def compileCshContent(self):
        cshContent = self.buildCfg.compileOption(self._args.build)
        if self._cli.userCliCompileOption():
            cshContent = cshContent + self._cli.userCliCompileOption()
        if hasattr(self._args, 'compileOption') and self._args.compileOption:
            cshContent  = cshContent + self._args.compileOption
        return cshContent + ['-f %s' % defaultTestListFile()] + ['-l compile.log']

    def compileCmd(self):
        return 'set -e; cd; cd -; chmod a+x pre_compile.csh compile.csh post_compile.csh; ./pre_compile.csh; ./compile.csh; ./post_compile.csh;'

    def generateSeed(self):
        for i in range(self._args.repeat):
            if self._args.seed == 0:
                seed = '%d' % (randint(1, 0xffffffff))
            else:
                seed = self._args.seed
            self._seeds.append(seed)

    def genTestscaseSimCsh(self):
        dir = ''
        for i in self._seeds:
            dir = os.path.join(self._testcaseRootDir, self._args.test + '__' + str(i))
            self._testcasesDir.append(dir)
            createDir(dir)
            self.createSimCsh(dir, i)

    @property
    def _testCaseWordDir(self):
        return self._testcasesDir

    def createSimCsh(self, testcaseDir, seed):
        with open(os.path.join(testcaseDir, 'pre_sim.csh'), 'w') as f:
            for item in self.buildCfg.preSimOption(self._args.build):
                f.write(item + '\n')
        with open(os.path.join(testcaseDir, 'sim.csh'), 'w') as f:
            #FIXME: if add shebang line, will cause */simv: No match. shell error
            #f.write('#!/bin/csh -fe\n')  
            f.write('#!/bin/sh -fe\n')  
            f.write(os.path.join(self._buildDir, self._simulator_if.simExe()) + ' \\' + '\n')
            for index, item in enumerate(self.simCshContent()):
                if index == len(self.simCshContent())-1:
                    #TODO: move this line to vcsInterface, because ntb_random_seed is vcs keyword 
                    if self._args.seed == 0: 
                        f.write('\t' + '+ntb_random_seed=%s' % seed + ' \\' + '\n')
                    f.write('\t' + item + '\n')
                else:
                    f.write('\t' + item + ' \\' + '\n')
        with open(os.path.join(testcaseDir, 'post_sim.csh'), 'w') as f:
            for item in self.buildCfg.postSimOption(self._args.build):
                f.write(item + '\n')

    def simCshContent(self):
        simContent = []
        simContent = self.buildCfg.simOption(self._args.build)
        if self._cli.userCliSimOption():
            simContent = simContent + self._cli.userCliSimOption()
        if hasattr(self._args, 'simOption') and self._args.simOption:
            simContent = simContent+ self._args.simOption
        return simContent + ['-l sim.log']

    def simCmd(self):
        return 'set -e; cd; cd -; chmod a+x pre_sim.csh sim.csh post_sim.csh; ./pre_sim.csh; ./sim.csh; ./post_sim.csh;'

class groupTestCompile(compileBuildBase):
    def __init__(self, cli=None, ini_file=None):
        super(groupTestCompile, self).__init__(cli, ini_file, simulator_if)
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
            f.write('#!/bin/sh -fe\n')
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
    compile.generateSeed()
    compile.genTestscaseSimCsh()
    #gpCompile = groupTestCompile(args)
    #gpCompile.prepareEnv()
