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
from globals import *
from exceptions import buildUnknown

class buildCfg(buildBaseCfg):
    def __init__(self, name, section, parent=None):
        super(buildCfg, self).__init__(name, section, parent)
        self._subSectionType=buildSubCfg
        self._addOption('default_build')

    @property
    def defaultBuild(self):
        try:
            default_build = self._buildInOpts['default_build']
        except ValueError:
            raise ValueError('default_build keyword is used but not defined')
        if not default_build in self.subSection:
            raise ValueError('value of default_build : %s is unknown' % default_build)
        return default_build

    def getBuild(self, build=''):
        if build:
            if not build in self.subSection:
                raise buildUnknown(build)
            buildSection = self.subSection[build]
        else:
            buildSection = self.subSection[self.defaultBuild]
        return buildSection

class buildSubCfg(buildBaseCfg):
    def __init__(self, name, section, parent=None):
        super(buildSubCfg, self).__init__(name, section, parent)
        self._addOption('testdir')
        self._addOption('twostep')

    @property
    def testDir(self):
        try:
            testdir = self._buildInOpts['testdir']
        except ValueError:
            return None
        else:
            return testdir

    @property
    def twoStep(self):
        try:
            twostep = self._buildInOpts['twostep']
        except ValueError:
            return None
        else:
            return True

#if __name__ == '__main__':
#    config = ConfigObj(infile=defaultBuildFile(), stringify=True)
#    build = buildCfg('test', config['build'])
#    build.parse()
#    print(build.simOption)
#    print(build.compileOption)
#    print(build.getBuild('dla').name)
#    for v in build.subSection.values():
#        print(v.name)
#        print(v.simOption)
#        print(v.compileOption)
