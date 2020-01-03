import os
import grp

def checkEnv():
    if not 'YASA_SIMULATOR' in os.environ:
        raise EnvironmentError('$YASA_SIMULATOR is not defined')
    elif not os.environ['YASA_SIMULATOR'] in ['vcs','irun','xrun']:
        raise EnvironmentError('$YASA_SIMULATOR=%s is not inside supported tools["vcs", "irun", "xrun"]' % os.environ['YASA_SIMULATOR'])    
    if not 'PRJ_HOME' in os.environ:
        raise EnvironmentError('$PRJ_HOME is not defined')
    if not 'TEMP_ROOT' in os.environ:
        raise EnvironmentError('$TEMP_ROOT is not defined')

checkEnv()

def defaultCliCfgFile():
    defaultCliCfgFile = os.path.join(os.environ['PRJ_HOME'], 'bin', os.environ['YASA_SIMULATOR']+'_cfg', 'userCli.cfg')
    if not os.path.exists(defaultCliCfgFile):
        raise EnvironmentError('%s file not exists' % defaultCliCfgFile)
    else:
        return defaultCliCfgFile

def defaultBuildFile():
    defaultBuildFile = os.path.join(os.environ['PRJ_HOME'], 'bin', os.environ['YASA_SIMULATOR']+'_cfg', 'build.cfg')
    if not os.path.exists(defaultBuildFile):
        raise EnvironmentError('%s file not exists' % defaultBuildFile)
    else:
        return defaultBuildFile

def defaultGroupFile():
    defaultGroupFile = os.path.join(os.environ['PRJ_HOME'], 'bin', os.environ['YASA_SIMULATOR']+'_cfg', 'group.cfg')
    if not os.path.exists(defaultGroupFile):
        raise EnvironmentError('%s file not exists' % defaultGroupFile)
    else:
        return defaultGroupFile

def defaultTestListFile():
    return 'test.f'

def defaultCovDir():
    return 'coverage'

def defaultYasaDir():
    if 'YASA_HOME' in os.environ:
        return os.environ['YASA_HOME']
    else :
        return os.path.join(os.environ['PRJ_HOME'], 'bin', 'YASA')

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
    userSimCheckFile = os.path.join(os.environ['PRJ_HOME'], 'bin', os.environ['YASA_SIMULATOR']+'_cfg', 'userSimCheck.py')
    if os.path.isfile(userSimCheckFile):
        return ('userSimCheck', userSimCheckFile)
    return (None, None)


def defaultWorkDir():
    # if os.environ['USER'] in grp.getgrnam('sg-ic-ipdv').gr_mem:
    #    return os.path.join('/ic/temp/ipdv', os.environ['USER'], os.path.basename(os.environ['PRJ_HOME']))
    # elif os.environ['USER'] in grp.getgrnam('sg-ic-soc').gr_mem:
    #    return os.path.join('/ic/temp/fe', os.environ['USER'], os.path.basename(os.environ['PRJ_HOME']))
    # else : raise SystemError('You are supposed to be in sg-ic-ipdv, sg-ic-soc, sg-ic-fpga or sg-ic-socdv group, but you are not !')

    return os.path.join(os.environ['TEMP_ROOT'], os.path.basename(os.environ['PRJ_HOME']))
