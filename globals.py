import os
import grp
import sys
from color_printer import COLOR_PRINTER

def checkEnv():
    if not 'PRJ_HOME' in os.environ:
        raise EnvironmentError('$PRJ_HOME is not defined')

checkEnv()

def defaultCliCfgFile():
    cliFile = os.path.join(os.environ['PRJ_HOME'], 'bin', 'userCli.cfg')
    if os.path.exists(cliFile):
        return cliFile
    else:
        COLOR_PRINTER.write("%s doesn't exist!\n" % cliFile, fg='ri')
        sys.exit(1)

def defaultBuildFile():
    buildFile = os.path.join(os.environ['PRJ_HOME'], 'bin', 'build.cfg')
    if os.path.exists(buildFile):
        return buildFile
    else:
        COLOR_PRINTER.write("%s doesn't exist!\n" % buildFile, fg='ri')
        sys.exit(1)

def defaultGroupFile():
    groupFile = os.path.join(os.environ['PRJ_HOME'], 'bin', 'group.cfg')
    if os.path.exists(groupFile):
        return groupFile 
    else:
        COLOR_PRINTER.write("%s doesn't exist!\n" % groupFile, fg='ri')
        sys.exit(1)

def defaultTestListFile():
    return 'test.f'

def defaultCovDir():
    return 'coverage'

def defaultYasaDir():
    if 'YASA_HOME' in os.environ:
        return os.environ['YASA_HOME']
    else :
        return os.path.join(os.environ['PRJ_HOME'], 'bin', 'Yasa')

def defautlVplanDir():
    return os.path.join(os.environ['PRJ_HOME'], 'etc', 'vplan')


def defaultTestDir():
    if 'TEST_DIR' in os.environ:
        return os.environ['TEST_DIR']
    else:
        return os.path.join(os.environ['PRJ_HOME'], 'testcases')


def defaultWorkDir():
    if 'WORK_DIR' in os.environ:
        return os.environ['WORK_DIR']
    else:
        return os.path.join(defaultWorkPrjDir(), 'work')


def defaultReportDir():
    if 'REPORT_DIR' in os.environ:
        return os.environ['REPORT_DIR']
    else:
        return os.path.join(defaultWorkPrjDir(), 'report')

def userSimCheck():
    userSimCheckFile = os.path.join(os.environ['PRJ_HOME'], 'bin', 'userSimCheck.py')
    if os.path.isfile(userSimCheckFile):
        return ('userSimCheck', userSimCheckFile)
    return (None, None)


def defaultWorkDir():
    # if os.environ['USER'] in grp.getgrnam('sg-ic-ipdv').gr_mem:
    #    return os.path.join('/ic/temp/ipdv', os.environ['USER'], os.path.basename(os.environ['PRJ_HOME']))
    # elif os.environ['USER'] in grp.getgrnam('sg-ic-soc').gr_mem:
    #    return os.path.join('/ic/temp/fe', os.environ['USER'], os.path.basename(os.environ['PRJ_HOME']))
    # else : raise SystemError('You are supposed to be in sg-ic-ipdv, sg-ic-soc, sg-ic-fpga or sg-ic-socdv group, but you are not !')

    return os.path.join(os.environ['PRJ_HOME'], os.path.basename(os.environ['PRJ_HOME']) + '_out')
