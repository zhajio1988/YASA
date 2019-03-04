from extconfigobj import ConfigObj, ParseError, Section, getSections, getKeyWords
from globals import *

class baseCfg(object):
    def __init__(self, name, section, parent=None):
        self._name = name
        self._section = section
        self._parent=parent
        self._subSection = {}
        self._buildInOpts = {}
        self._subSectionType=self.__class__
        #self._buildInOptsType = ['pre_compile_option','compile_option', 'post_compile_option',
        #                    'pre_sim_option', 'sim_option', 'post_sim_option']

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def subSection(self):
        return self._subSection

    @property
    def buildInOption(self):
        return self._buildInOpts

    def _addOption(self, option):
        self._buildInOpts[option] = []

    def isRoot(self):
        return not self._parent

    def isLeaf(self):
        return not self._subSection

    def parse(self):
        self._readSubSection()
        self._readBuildInOption()

    def dump(self, tab=''):
        result = tab
        result += 'name:' + self.name + '\n'
        result += tab+'\tbuildInOption: '+self.buildInOption.__str__()+'\n'
        for subSection in self.subSection.values():
            result += subSection.dump(tab+'\t')
            return result

    def _readSubSection(self):
        if isinstance(self._section, Section):
            #print('debug point1', getSections(self._section).keys())
            for k, v in getSections(self._section).items():
                #print(k ,v)
                self._subSection[k] = self._subSectionType(k,v,self)
                self._subSection[k].parse()

    def _readBuildInOption(self):
        #print("debug point2", self._section)
        for k,v in getKeyWords(self._section).items():
            #print("debug point2", k, v)
            if self._checkKeyWord(k) :
                print("debug point3", k, v)
                self._buildInOpts[k] = v #" ".join(v) if isinstance(v, list) else v
                #print(self.buildInOption.keys())

    def _checkKeyWord(self, k):
        if not k in self._buildInOpts:
            raise ParseError('%s is unknown option' % k)
        return True

class includableTopCfg(baseCfg):
    def __init__(self, name, section, parent=None):
        super(includableTopCfg, self).__init__(name, section, parent)
        self._subSectionType = includableCfg

    def _readBuildInOption(self):
        for k, v in getKeyWords(self._section).items():
            print("debug point2", k, v)
            if self._checkKeyWord(k):
                self._buildInOpts[k] = v
                #handlePlusEq(self._buildInOption[k])

    def parse(self):
        super(includableTopCfg, self).parse()
        for subSection in self._subSection.values():
            #handlePlusEq(subSection.include)
            for incName in subSection.include:
                print("debug point0", incName)
                subSection.addInclude(self._subSection[incName])

class includableCfg(baseCfg):
    def __init__(self, name, section, parent=None):
        super(includableCfg, self).__init__(name, section, parent)
        self._include = []
        self._addOption('include')

    @property
    def include(self):
        return self._buildInOpts['include']

    def addInclude(self, inc):
        self._include.append(inc)

class buildBaseCfg(baseCfg):
    def __init__(self, name, section, parent=None):
        super(buildBaseCfg, self).__init__(name, section, parent)
        self._addOption('pre_compile_option')
        self._addOption('compile_option')
        self._addOption('post_compile_option')
        self._addOption('pre_sim_option')
        self._addOption('sim_option')
        self._addOption('post_sim_option')

    @property
    def compileOption(self):
        return self._buildInOpts['compile_option']

    @property
    def simOption(self):
        return self._buildInOpts['sim_option']

    @ property
    def preCompileOption(self):
        return self._buildInOpts['pre_compile_option']

    @property
    def preSimOption(self):
        return self._buildInOpts['pre_sim_option']

    @property
    def postCompileOption(self):
        return self._buildInOpts['post_compile_option']

    @property
    def postSimOption(self):
        return self._buildInOpts['post_sim_option']


#if __name__ == '__main__':
#    config = ConfigObj(infile=defaultBuildFile(), stringify=True)
#    baseCfg = flowBaseCfg('test',config)
#    baseCfg.parse()
#    #print(baseCfg.subSection['build'].buildInOption)
#    #print(baseCfg.subSection['build'].subSection['dla'].buildInOption)
#    #print(baseCfg.buildInOption.keys())
#    #baseCfg.dump(tab='debug point')