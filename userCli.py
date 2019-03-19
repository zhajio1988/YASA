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
from extconfigobj import ConfigObj, ConfigObjError, Section
from globals import *

class userCli(object):
    def __init__(self, parser=None, ini_file=None):
        self.parser = parser
        self.kwargs = {}
        self.args = None
        self.config = ConfigObj(infile=defaultCliCfgFile(), stringify=True)
        self.section = self.userCliSection

    @property
    def userCliSection(self):
        if 'userCli' in self.config:
            self.section = self.config['userCli']
            return self.section
        else:
            raise AttributeError('userCli section is not defined in %s' % defaultCliCfgFile())

    def setParsedArgs(self, parsedArgs):
        self.args = parsedArgs

    def compileOption(self):
        args = self.args;
        argsList = []
        keyVar = ''
        for key in self.section:
            keyVar = key.replace('$', '') if not key.find('$') else key
            if hasattr(args, keyVar) and getattr(args, keyVar):
                for k, v in self.section[key].items():
                    if '$' in v:
                        v = v.replace(key, getattr(args, keyVar))
                    if 'compile_option' == k:
                        argsList = argsList + v if isinstance(v, list) else argsList + [v]
        return argsList

    def simOption(self):
        args = self.args;
        argsList = []
        keyVar = ''
        for key in self.section:
            keyVar = key.replace('$', '') if not key.find('$') else key
            if hasattr(args, keyVar) and getattr(args, keyVar):
                for k, v in self.section[key].items():
                    if '$' in v:
                        v = v.replace(key, getattr(args, keyVar))
                    if 'sim_option' == k:
                        argsList = argsList + v if isinstance(v, list) else argsList + [v]
        return argsList

    def addArguments(self):
        keyVar = ''
        action = ''
        for key in self.section:
            if not key.find('$'):
                self.kwargs['default'] = 'rand'
            keyVar = key.replace('$', '') if not key.find('$') else key
            action = 'store' if not key.find('$') else 'store_true'
            self.kwargs = {}
            self.kwargs['dest'] = keyVar
            self.kwargs['action'] = action
            if self.section.inline_comments[key]:
                self.kwargs['help'] = self.section.inline_comments[key].replace('#', '')
            else:
                self.kwargs['help'] = 'user defined option'

            self.parser.add_argument('-%s' % keyVar, **self.kwargs)

if __name__ == '__main__':
    import argparse
    import sys

    #print(vars(userCli.userCliSection()))
    #userCli.userCliSection.walk(userCli.add_arguments())
    parser = argparse.ArgumentParser()
    userCli = userCli(parser)
    userCli.addArguments()
    args = parser.parse_args(sys.argv[1:])
    userCli.setParsedArgs(args)
    print(args)
    print(args.prof)
    print(args.vh)
    print(args.wave_name)
    print(userCli.compileOption())
    print(userCli.simOption())
    #print(args.sim_option)
