#******************************************************************************
# * Copyright (c) 2019, XtremeDV. All rights reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
# * Author: Jude Zhang, Email: zhajio.1988@gmail.com
# *******************************************************************************
from baseCfg import *
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
            appendArgs = []
            #print("debug point test", test)
            testList = test.split("-")
            testArgs = test.split(" ")[1:]
            #print('22', testArgs)
            if testList[1:] and self.argsOption:
                self._getTestArgs(testList[1:], appendArgs)
                #print("debug point appendArgs1", appendArgs)
                testArgs.append(" ".join(['-'+ x for x in appendArgs]))
                #print("debug point testArgs1", testArgs)
                index = self._buildInOpts['tests'].index(test)
                self._buildInOpts['tests'].pop(index)
                self._buildInOpts['tests'].insert(index, testList[0] + " ".join(testArgs))
            elif self.argsOption:
                testList.append(self.argsOption)
                index = self._buildInOpts['tests'].index(test)
                self._buildInOpts['tests'].pop(index)
                self._buildInOpts['tests'].insert(index, " ".join(testList))
            #print(self._buildInOpts['tests'])

    def _getTestArgs(self, testArgs, appendArgs):
        append = True
        argsList = [i.strip() for i in self.argsOptionList if i != '']
        #print("debug point j", argsList)
        for j in argsList:
            j = j.strip().split(" ")
            #print("debug point j", j)
            for i in testArgs:
                i = i.strip().split(" ")
                if len(i) > 1:
                    if len(j) >1:
                        if j[0] == i[0]:
                            append = False
                            break
                    elif len(j) == 1:
                        append = True
                elif len(i) == 1:
                    if len(i) == 1:
                        if j == i:
                            append = False
                            break
                    elif len(j) > 1:
                        append = True
            if append:
                appendArgs.append(" ".join(j))
                #print("debug point appendArgs", appendArgs)

    @property
    def buildOption(self):
        return self._buildInOpts['build']

    @property
    def argsOption(self):
        return self._buildInOpts['args']

    @property
    def argsOptionList(self):
        if self.argsOption:
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
