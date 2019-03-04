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

class readGroupCfgFile(readCfgFileBase):
    def __init__(self, file):
        super(readGroupCfgFile, self).__init__('readGroupCfgFile', file)
        self._subSectionType = {'testgroup': groupCfg}
        self.parse()

    @property
    def testgroup(self):
        if 'testgroup' in self.subSection:
            return self.subSection['testgroup']
        else:
            print("none exists")

if __name__ == '__main__':
    #config = readBuildCfgFile(defaultBuildFile())
    #print(config.build.simOption)
    #print(config.build.compileOption)
    #print(config.build.getBuild('').name)
    #print(config.build.getBuild('dla_fpga').name)

    config = readGroupCfgFile(defaultGroupFile())
    for v in config.testgroup.subSection.values():
        print(v.include)
        print(v.name)
        #print(v.buildOption)
        #print(v.argsOption)
        #print(v.testsOption)
        #print('haha', v.include)
        #for include in v.include:
        #   print(config.getGroup(include).testsOption)
