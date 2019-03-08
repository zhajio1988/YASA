from extconfigobj import ConfigObj, ConfigObjError, Section
import copy
from globals import *

class Option(object):
    """Holds a configuration option and the names and locations for it.

    Instantiate options using the same arguments as you would for an
    add_arguments call in argparse. However, you have two additional kwargs
    available:

        env: the name of the environment variable to use for this option
        ini_section: the ini file section to look this value up from
    """

    def __init__(self, *args, **kwargs):
        self.args = args or []
        self.kwargs = kwargs or {}

    def add_argument(self, parser, **override_kwargs):
        """Add an option to a an argparse parser."""
        kwargs = {}
        if self.kwargs:
            kwargs = copy.copy(self.kwargs)
            try:
                del kwargs['env']
            except KeyError:
                pass
            try:
                del kwargs['ini_section']
            except KeyError:
                pass
        kwargs.update(override_kwargs)
        parser.add_argument(*self.args, **kwargs)

    @property
    def type(self):
        """The type of the option.

        Should be a callable to parse options.
        """
        return self.kwargs.get("type", str)

    @property
    def name(self):
        """The name of the option as determined from the args."""
        for arg in self.args:
            if arg.startswith("--"):
                return arg[2:].replace("-", "_")
            elif arg.startswith("-"):
                continue
            else:
                return arg.replace("-", "_")

    @property
    def default(self):
        """The default for the option."""
        return self.kwargs.get("default")


class userCliCfg(object):
    def __init__(self, parser=None, ini_file=None):
        self.parser = parser
        self.kwargs = {}
        self.config = ConfigObj(infile=defaultCliCfgFile(), stringify=True)
        self.section = self.userCliSection

    @property
    def userCliSection(self):
        if 'userCli' in self.config:
            self.section = self.config['userCli']
            return self.section
        else:
            raise AttributeError('userCli section is not defined in %s' % defaultCliCfgFile())

    def compileOption(self, args):
        argsList = []
        keyVar = ''
        for key in self.section:
            keyVar = key.replace('$', '') if not key.find('$') else key
            if hasattr(args, keyVar) and getattr(args, keyVar):
                for k, v in self.section[key].items():
                    if '$' in v:
                        v = v.replace(key, getattr(args, keyVar))
                    if 'compile_option' == k:
                        argsList = argsList + v if isinstance(v, list) else [v]
        return argsList

    def simOption(self, args):
        argsList = []
        keyVar = ''
        for key in self.section:
            keyVar = key.replace('$', '') if not key.find('$') else key
            if hasattr(args, keyVar) and getattr(args, keyVar):
                for k, v in self.section[key].items():
                    if '$' in v:
                        v = v.replace(key, getattr(args, keyVar))
                    if 'sim_option' == k:
                        argsList = argsList + v if isinstance(v, list) else [v]
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

            userCli = Option('-%s' % keyVar)
            userCli.add_argument(self.parser, **self.kwargs)

if __name__ == '__main__':
    import argparse
    import sys

    #print(vars(userCliCfg.userCliSection()))
    #userCliCfg.userCliSection.walk(userCliCfg.add_arguments())
    parser = argparse.ArgumentParser()
    userCliCfg = userCliCfg(parser)
    userCliCfg.addArguments()
    args = parser.parse_args(sys.argv[1:])
    print(args)
    print(args.prof)
    print(args.vh)
    print(args.wave_name)
    print(userCliCfg.compileOption(args))
    print(userCliCfg.simOption(args))
    #print(args.sim_option)
