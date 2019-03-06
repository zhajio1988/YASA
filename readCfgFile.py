from buildCfg import *
from groupCfg import *

class readCfgFileBase(baseCfg):
    def __init__(self, name, file):
        self._section = ConfigObj(infile=file, stringify=True)
        super(readCfgFileBase, self).__init__(name, self._section, None)
        self._subSectionType = {}
        self._validSection = ['build', 'testgroup']

    def _readSubSection(self):
        for k, v in getSections(self._section).items():
            if self._checkSubSection(k) and k in self._subSectionType:
                self._subSection[k] = self._subSectionType[k](k, v, self)
                self._subSection[k].parse()

    def _checkSubSection(self, key):
        if key not in self._validSection:
            raise ParseError('[%s] is unknown section' % key)
        return True
    
    
class readBuildCfgFile(readCfgFileBase):
    def __init__(self, file):
        super(readBuildCfgFile, self).__init__('readBuildCfgFile', file)
        self._subSectionType = {'build': buildCfg}
        self.parse()

    @property
    def build(self):
        if 'build' in self.subSection:
            return self.subSection['build']

    def compileOption(self, buildName):
            return self.build.getBuild(buildName).compileOption + self.build.compileOption if self.build.compileOption else self.build.getBuild(buildName).compileOption

    def simOption(self, buildName):
        return self.build.getBuild(buildName).simOption + self.build.simOption if self.build.simOption else self.build.getBuild(buildName).simOption

    def preCompileOption(self, buildName):
        return self._toList(self.build.getBuild(buildName).preCompileOption) + self._toList(self.build.preCompileOption)

    def preSimOption(self, buildName):
        return self._toList(self.build.getBuild(buildName).preSimOption) + self._toList(self.build.preSimOption)

    def postCompileOption(self, buildName):
        return self._toList(self.build.getBuild(buildName).postCompileOption) + self._toList(self.build.postCompileOption)

    def postSimOption(self, buildName):
        return self._toList(self.build.getBuild(buildName).postSimOption) + self._toList(self.build.postSimOption)

    def _toList(self, preOptions):
        if isinstance(preOptions, str):
            return [preOptions]
        elif isinstance(preOptions, list):
            return preOptions


class readGroupCfgFile(readCfgFileBase):
    def __init__(self, file):
        super(readGroupCfgFile, self).__init__('readGroupCfgFile', file)
        self._subSectionType = {'testgroup': groupCfg}
        self.parse()
        self._validBuild = []
        self._tests = {}

    @property
    def testGroup(self):
        if 'testgroup' in self.subSection:
            return self.subSection['testgroup']

    @property
    def validBuild(self):
        return self._validBuild[0]

    def getTests(self, groupName):
        groupSection = self.testGroup.getGroup(groupName)
        globalBuild = groupSection.buildOption
        globalTests = groupSection.testsOption
        if globalBuild:
            self._validBuild.append(globalBuild)
        if globalTests:
            self._tests[groupName] = globalTests
        if groupSection.include:
            for incGroup in groupSection.incGroups:
                if incGroup.testsOption:
                    self._tests[incGroup.name] = incGroup.testsOption
                self.setValidBuild(globalBuild, incGroup.buildOption)

        self.checkBuild(self._validBuild, groupName)
        print(self._tests)
        return self._tests

    def setValidBuild(self, globalBuild, subBuild):
        if globalBuild and subBuild and globalBuild != subBuild:
            self._validBuild.append(globalBuild)
        elif subBuild and not globalBuild:
            self._validBuild.append(subBuild)
        elif globalBuild and not subBuild:
            self._validBuild.append(globalBuild)

    def checkBuild(self, buildList, groupName):
        buildSet = set(buildList)
        if len(buildSet) != 1:
            raise ValueError(('group %s has included subgroup is must be in same build' % groupName))

if __name__ == '__main__':
    config = readBuildCfgFile(defaultBuildFile())
    print(config.build.simOption)
    print(config.build.compileOption)
    print(config.build.getBuild('dla_fpga').name)
    print(config.build.getBuild('dla_fpga').compileOption)
    print(config.simOption('dla_fpga'))
    print(config.preCompileOption('dla_fpga'))
    print(config.postCompileOption('dla_fpga'))
    print(config.preSimOption('dla_fpga'))
    print(config.postSimOption('dla_fpga'))


    #config = readGroupCfgFile(defaultGroupFile())
    #config.getTests('v1_regr')
    #config.getTests('top_regr')

    #for v in config.testgroup.subSection.values():
    #    print(v.include)
    #    print(v.name)
        #print(v.buildOption)
        #print(v.argsOption)
        #print(v.testsOption)
        #print('haha', v.include)
        #for include in v.include:
        #   print(config.getGroup(include).testsOption)
