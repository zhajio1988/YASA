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
    def __init__(self, options=None, ini_file=None, **kwargs):
        self.kwargs = kwargs or {}
        self.config = ConfigObj(infile=defaultCliCfgFile(), stringify=True)
        self.section = None

    def usrCliSection(self):
        if 'userCli' in self.config:
            self.section = self.config['userCli']
            return self.section
        else:
            raise AttributeError('userCli section is not in %s' % defaultCliCfgFile())

    def add_arguments(self, section, parser):
        for key in section:
            #print('debug point0 %s' % key)
            #print('debug point1 %s' % section.inline_comments[key])
            print('debug point2 %s' % section[key].scalars)
            print('debug point3 %s' % section[key])
            if isinstance(section[key], Section):
                print("debug section")
            self.kwargs = {}
            self.kwargs['dest'] = key
            self.kwargs['action'] = 'store'
            self.kwargs['nargs'] = '?'
            if section.inline_comments[key]:
                self.kwargs['help'] = section.inline_comments[key].lstrip('#')
            else:
                self.kwargs['help'] = 'user defined option'

            if isinstance(section[key], dict) and section[key]:
                #print("%s" % json.dumps(section[key]))
                self.kwargs['const'] = section[key]
                #print('debug point dict')

            #print(self.kwargs)
            val = section[key]
            userCli = Option('-%s' % key)
            userCli.add_argument(parser, **self.kwargs)
            #parseKwargs(self, key, , self.kwargs)

if __name__ == '__main__':
    import argparse
    import sys
    userCliCfg = userCliCfg()

    #print(vars(userCliCfg.usrCliSection()))
    #userCliCfg.usrCliSection.walk(userCliCfg.add_arguments())
    parser = argparse.ArgumentParser()
    userCliCfg.add_arguments(userCliCfg.usrCliSection(), parser)
    args = parser.parse_args(sys.argv[1:])
    print(args)
    print(args.prof)
    print(args.vh)
    #print(args.sim_option)

