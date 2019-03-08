import os
import sys
from utils import *
from globals import *
from readCfgFile import  readGroupCfgFile, readBuildCfgFile


class flowList(object):
    def __init__ (self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def list(self):
        pass

    @list.setter
    def list(self,value):
        pass

    def check(self, value):
        return value in self.list

    def show(self):
        print ('Available '+self.name+':\n' + '\n'.join(['\t' + x for x in self.list]))


class testList(flowList):
    def __init__ (self):
        super(testList,self).__init__('Tests')
        self._testDir=defaultTestDir()
        self._testlist = {}

    @property
    def list(self):
        return self._testlist.keys()

    @property
    def testDir(self):
        return self._testDir

    @testDir.setter
    def testDir(self, value):
        if not os.path.isdir(expandDirVar(value)):
            raise SystemError('%s is not exists!' % value)
        self._testDir = expandDirVar(value)
        self._testlist = {}
        self._getTestList()

    def genTestFileList(self, dir):
        with open(os.path.join(dir,defaultTestListFile()), 'w') as file:
            file.write('+incdir+' + self._testDir + '\n')
            for test in self._testlist.values():
                file.write('+incdir+' + test + '\n')
                file.write('+incdir+' + os.path.join(test, '..') + '\n')
                file.write(os.path.join(test, os.path.basename(test) + '.sv') + '\n')

    def getTestList(self):
        for dirpath, dirname, filename in os.walk(self._testDir, topdown=True, followlinks=True):
            if '.svn' in dirname:
                dirname.remove('.svn')
            for file in filename:
                basename, extname = os.path.splitext(file)
                if extname == '.sv' and basename == os.path.basename(dirpath):
                    self._testlist[basename] = dirpath

class allTestList(object):
    def __init__ (self):
        self._testlists={}

    def setTestLists(self, build, testlist):
        self._testlists[build] = testlist

    def show(self):
        if self._testlists:
            print ('Available tests:')
            for key, value in self._testlists.items():
                print('\t'+ key + ':\n' + '\n'.join(['\t\t' + x for x in sorted(value.list)]))
        else:
            testList().show()

class groupList(flowList):
    def __init__(self):
        super(groupList, self).__init__('Groups')
        self._groupFile = defaultGroupFile()
        self._grouplist = readGroupCfgFile(self._groupFile).testGroup.subSection.keys()

    @property
    def list(self):
        return self._grouplist

    @property
    def groupFile(self):
        return self._groupFile

    @groupFile.setter
    def groupFile(self, value):
        if not os.path.isfile(value):
            raise SystemError('%s is not exists!' % value)
        self._groupFile = value
        self._grouplist = readGroupCfgFile(self._groupFile).testGroup.subSection.keys()

class buildList(flowList):
    def __init__ (self):
        super(buildList, self).__init__('Builds')
        self._buildlist= readBuildCfgFile(defaultBuildFile()).build.subSection.keys()

    @property
    def list(self):
        return self._buildlist

testlist = allTestList()
grouplist = groupList()
buildlist = buildList()

def show(name):
    getattr(sys.modules[__name__], name + 'list').show()


if __name__ == '__main__':
    tests = testList()
    tests.getTestList()
    testlist.setTestLists('default_build', tests)
    show('test')
    show('build')
    show('group')