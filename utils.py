import os
import shutil
import time

'''
utils functions
'''

def createDir(path, force = False):
    if force:
        shutil.rmtree(path, True)
    if not os.path.exists(path):
        os.makedirs(path)

def expandDirVar(dir):
    dir = os.path.expanddirs(dir)
    if '$' in dir:
        raise EnvironmentError('Environment Var in %s is unknown' % dir)
    return dir


def parseKwargs(obj, key ,default, **kwargs):
    if key in kwargs and kwargs[key] != 'default':
        setattr(obj, '_' + key, kwargs[key])
    else:
        setattr(obj, '_' + key, default)        
