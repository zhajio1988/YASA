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
