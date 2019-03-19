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
import argparse
from utils import *

class queueArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.lsfQueue = values
        if args.lsfQueue:
            appendAttr(args, 'lsfOptions', '-q %s' % args.lsfQueue)

class rusageArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.lsfRusage = values
        if args.lsfRusage:
            appendAttr(args, 'lsfOptions', '-R %s' % args.lsfRusage)

class jobNameArgsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.lsfJobName = values
        if args.lsfJobName:
            appendAttr(args, 'lsfOptions', '-J %s' % args.lsfJobName)            

class lsfCli(object):
    def __init__(self, parser=None):
        self.subParser = parser
        self.args = None        

    def addArguments(self):
        lsfSubParser = self.subParser.add_parser('lsf')
        lsfSubParser.add_argument('-queue', dest='lsfQueue', action=queueArgsAction,
                            help='Submits job to specified queues.')

        lsfSubParser.add_argument('-rusage', dest='lsfRusage', action=rusageArgsAction,
                            help='Specifies host resource requirements.')

        lsfSubParser.add_argument('-job_name', dest='lsfJobName', action=jobNameArgsAction,
                            help='Assigns the specified name to the job.')        

    def setParsedArgs(self, parsedArgs):
        self.args = parsedArgs
        appendAttr(self.args, 'lsfOptions', '')
