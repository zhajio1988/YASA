import os
import shutil
import time
import argparse
'''
utils functions
'''

def createDir(path, force = False):
    if force and os.path.exists(path):
        shutil.rmtree(path, True)
    if not os.path.exists(path):
        os.makedirs(path)

def expandDirVar(dir):
    dir = os.path.expandvars(dir)
    if '$' in dir:
        raise EnvironmentError('Environment Var in %s is unknown' % dir)
    return dir

def parseKwargs(obj, key ,default, **kwargs):
    if key in kwargs and kwargs[key] != 'default':
        setattr(obj, '_' + key, kwargs[key])
    else:
        setattr(obj, '_' + key, default)        

def appendAttr(obj, k, v):
    if hasattr(obj, k):
        if isinstance(v, list) and isinstance(getattr(obj, k), list):
            setattr(obj, k, getattr(obj, k)+v)
        elif isinstance(getattr(obj, k), list):
            getattr(obj, k).append(v)
        elif isinstance(v, list):
            setattr(obj, k, v.insert(0, getattr(obj, k)))
        else:
            setattr(obj, k, [getattr(obj, k), v])
    else:
        if isinstance(v, list):
            setattr(obj, k, v)
        else:
            setattr(obj, k, [v])


def positive_int(val):
    """
    ArgumentParse positive int check
    """
    try:
        ival = int(val)
        assert ival > 0
        return ival
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError("'%s' is not a valid positive int" % val)