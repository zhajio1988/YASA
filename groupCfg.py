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
from exceptions import groupUnknown

class groupCfg(includableTopCfg):
    def __init__(self, name, section, parent=None):
        super(groupCfg, self).__init__(name, section, parent)
        self._subSectionType = groupSubCfg

    def getGroup(self, group=''):
        if group:
            if not group in self.subSection:
                raise groupUnknown(group)
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
        """
        Parse each testcase in group. If group have args field,
        append args with testcase name. if tests field itself has
        args field. Duplicate fields in group args field will be overwritten
        Such as sanity2 will use its seed 56789 and repeat num 2.
        seed 56789 overwrite seed 12345 in args field.
        sanity3 will use its seed 12345 and repeat num 3
        ```
        [[top_smoke]]
        build = candy_lover
        args = -vh  -seed 12345 -r 2
        tests = sanity2 -seed 56789
        tests = sanity3 -r 3 
        ```
        """
        testsOpts = []
        # when only one case in group, _buildInOpts['tests'] is string,
        #should change to list for post processing
        if isinstance(self._buildInOpts['tests'], str):
            testsOpts.append(self._buildInOpts['tests'])
            self._buildInOpts['tests'] = testsOpts
        for test in self._buildInOpts['tests']:
            appendArgs = []
            testList = test.split("-")
            testArgs = test.split(" ")[1:]
            if testList[1:] and self.argsOption:
                self._getTestArgs(testList[1:], appendArgs)
                testArgs.append(" ".join(['-'+ x for x in appendArgs]))
                index = self._buildInOpts['tests'].index(test)
                self._buildInOpts['tests'].pop(index)
                self._buildInOpts['tests'].insert(index, testList[0] + " ".join(testArgs))
            elif self.argsOption:
                testList.append(self.argsOption)
                index = self._buildInOpts['tests'].index(test)
                self._buildInOpts['tests'].pop(index)
                self._buildInOpts['tests'].insert(index, " ".join(testList))

    def _getTestArgs(self, testArgs, appendArgs):
        """
        Get testcase args. Judge if Duplicate fields exist or not.
        then deal with these situation.
        """
        append = True
        argsList = [i.strip() for i in self.argsOptionList if i != '']
        for j in argsList:
            j = j.strip().split(" ")
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
