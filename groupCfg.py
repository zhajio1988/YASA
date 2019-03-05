from baseCfg import *
import shlex
from copy import *

class groupCfg(includableTopCfg):
    def __init__(self, name, section, parent=None):
        super(groupCfg, self).__init__(name, section, parent)
        self._subSectionType = groupSubCfg

    def getGroup(self, group=''):
        if group:
            if not group in self.subSection:
                raise ValueError('group : %s is unknown' % group)
            groupSection = self.subSection[group]
        return groupSection


class groupSubCfg(includableCfg):
    def __init__(self, name, section, parent=None):
        super(groupSubCfg, self).__init__(name, section, parent)
        self._addOption('build')
        self._addOption('args')
        self._addOption('tests')
        self._tests = []

    @property
    def incGroups(self):
        for inc in self._include:
            for incGroup in inc.incGroups:
                yield incGroup
        yield deepcopy(self)

    def _readBuildInOption(self):
        super(groupSubCfg, self)._readBuildInOption()
        self._parseBuild()
        self._parseArgs()
        self._parseTests()

    def _parseBuild(self):
        return self._buildInOpts['build']

    def _parseArgs(self):
        return  self._buildInOpts['args']

    def _parseTests(self):
        for test in self._buildInOpts['tests']:
            print("debug point test", test)
            testList = test.split("-")
            print(testList)
            if testList[1:]:
                self._getTestArgs(testList[1:])
                #for i in testList[1:]:
                #    print(i.strip().split(" ")[0])
            else:
                testList.append(self.argsOption)
                index = self._buildInOpts['tests'].index(test)
                self._buildInOpts['tests'].pop(index)
                self._buildInOpts['tests'].insert(index, " ".join(testList))
                print(self._buildInOpts['tests'])

    def _getTestArgs(self, testArgs):
        append = False
        #print("debug point j", self.argsOption)
        argsList = [i for i in self.argsOptionList if i != '']
        #print("debug point j", argsList)
        for j in argsList:
            j = j.strip().split(" ")
            print("debug point j", j)

            for i in testArgs:
                i = i.strip().split(" ")
                print("debug point i", i)
                if len(j) == len(i):
                    if len(j) != 1:
                        if j[0] == i[0]:
                            append = False
                            break
                    else:
                        if j != i[0]:
                            print("debug point j[1]", j)


    @property
    def buildOption(self):
        return self._buildInOpts['build']

    @property
    def argsOption(self):
        return self._buildInOpts['args']

    @property
    def argsOptionList(self):
        return self.argsOption.strip().split("-")

    @property
    def testsOption(self):
        return self._buildInOpts['tests']

#if __name__ == '__main__':
#    config = ConfigObj(infile=defaultGroupFile(), stringify=True)
#    group = groupCfg('test', config['testgroup'])
#    group.parse()
#    for v in group.subSection.values():
#        print(v.name)
#        print(v.buildOption)
#        print(v.argsOption)
#        print(v.testsOption)
#        print('haha', v.include)
#        for include in v.include:
#            print(group.getGroup(include).testsOption)
