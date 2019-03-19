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
from extconfigobj import ConfigObj, ParseError, Section, getSections, getKeyWords
from globals import *

class baseCfg(object):
    def __init__(self, name, section, parent=None):
        self._name = name
        self._section = section
        self._parent=parent
        self._subSection = {}
        self._buildInOpts = {}
        self._subSectionType=self.__class__

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def subSection(self):
        return self._subSection

    @property
    def buildInOption(self):
        return self._buildInOpts

    def _addOption(self, option):
        self._buildInOpts[option] = []

    def isRoot(self):
        return not self._parent

    def isLeaf(self):
        return not self._subSection

    def parse(self):
        self._readSubSection()
        self._readBuildInOption()

    def dump(self, tab=''):
        result = tab
        result += 'name:' + self.name + '\n'
        result += tab+'\tbuildInOption: '+self.buildInOption.__str__()+'\n'
        for subSection in self.subSection.values():
            result += subSection.dump(tab+'\t')
            return result

    def _readSubSection(self):
        if isinstance(self._section, Section):
            for k, v in getSections(self._section).items():
                self._subSection[k] = self._subSectionType(k,v,self)
                self._subSection[k].parse()

    def _readBuildInOption(self):
        for k,v in getKeyWords(self._section).items():
            if self._checkKeyWord(k) :
                self._buildInOpts[k] = v #" ".join(v) if isinstance(v, list) else v

    def _checkKeyWord(self, k):
        if not k in self._buildInOpts:
            raise ParseError('%s is unknown option' % k)
        return True

class includableTopCfg(baseCfg):
    def __init__(self, name, section, parent=None):
        super(includableTopCfg, self).__init__(name, section, parent)
        self._subSectionType = includableCfg

    def parse(self):
        super(includableTopCfg, self).parse()
        for subSection in self._subSection.values():
            if not isinstance(subSection.include, list):
                for incName in [subSection.include]:
                    subSection.addInclude(self._subSection[incName])
            else:
                for incName in subSection.include:
                    subSection.addInclude(self._subSection[incName])

class includableCfg(baseCfg):
    def __init__(self, name, section, parent=None):
        super(includableCfg, self).__init__(name, section, parent)
        self._include = []
        self._addOption('include')

    @property
    def include(self):
        return self._buildInOpts['include']

    def addInclude(self, inc):
        self._include.append(inc)

class buildBaseCfg(baseCfg):
    def __init__(self, name, section, parent=None):
        super(buildBaseCfg, self).__init__(name, section, parent)
        self._addOption('pre_compile_option')
        self._addOption('compile_option')
        self._addOption('post_compile_option')
        self._addOption('pre_sim_option')
        self._addOption('sim_option')
        self._addOption('post_sim_option')

    @property
    def compileOption(self):
        return self._buildInOpts['compile_option']

    @property
    def simOption(self):
        return self._buildInOpts['sim_option']

    @property
    def preCompileOption(self):
        return self._buildInOpts['pre_compile_option']

    @property
    def preSimOption(self):
        return self._buildInOpts['pre_sim_option']

    @property
    def postCompileOption(self):
        return self._buildInOpts['post_compile_option']

    @property
    def postSimOption(self):
        return self._buildInOpts['post_sim_option']


#if __name__ == '__main__':
#    config = ConfigObj(infile=defaultBuildFile(), stringify=True)
#    baseCfg = flowBaseCfg('test',config)
#    baseCfg.parse()
#    #print(baseCfg.subSection['build'].buildInOption)
#    #print(baseCfg.subSection['build'].subSection['dla'].buildInOption)
#    #print(baseCfg.buildInOption.keys())
#    #baseCfg.dump(tab='debug point')
