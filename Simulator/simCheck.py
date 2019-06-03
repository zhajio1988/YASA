import re
class simCheck(object):
    uvmErrorPattern = r'^.*UVM_((ERROR)|(FATAL)) .*\@.*:'
    uvmWarningPattern = r'^.*UVM_WARNING .*\@.*:'
    uvmReportPattern = r'^--- UVM Report Summary ---'
    errorTaskPattern = r'^Error.+:'

    def __init__(self):
        super(simCheck, self).__init__()
        self._errPatterns = []
        self._excludeErrPatterns = []
        self.setErrPatterns(simCheck.uvmErrorPattern)
        self.setErrPatterns(simCheck.errorTaskPattern)
        self._warnPatterns = []
        self._excludeWarnPatterns = []
        self.setWarnPatterns(simCheck.uvmWarningPattern)
        self._endFlagPatterns = []
        self.setEndFlagPatterns(simCheck.uvmReportPattern)
        self._failStatus = ''
        self._reasonMsg = ''
        self._endFlagHit = False
        self._simEndPattern = None 

    def resetStatus(self):
        self._failStatus = ''
        self._reasonMsg = ''
        self._endFlagHit = False

    @property
    def status (self):
        if self._failStatus:
            return self._failStatus, self._reasonMsg
        elif not self._endFlagHit:
            self._failStatus = 'UNKNOWN®'
            self._reasonMsg = 'No Simulation End Flag!'
            return self._failStatus, self._reasonMsg
        else:
            return 'PASS', ''

    def setErrPatterns(self, pattern):
        self._errPatterns.append(re.compile(pattern))
    
    def setWarnPatterns(self, pattern):
        self._warnPatterns.append(re.compile(pattern))
    
    def setExcludeErrPatterns(self, pattern):
        self._excludeErrPatterns.append(re.compile(pattern))
    
    def setExcludeWarnPatterns(self, pattern):
        self._excludeWarnPatterns.append(re.compile(pattern))
    
    def setEndFlagPatterns(self, pattern):
        self._endFlagPatterns.append(re.compile(pattern))

    def check(self, string):
        for errPattern in self._errPatterns:
            if errPattern.match(string):
                excluded = filter(lambda x: x.match(string), self._excludeErrPatterns)
                if not list(excluded):
                    if self._failStatus != 'FAIL':
                        self._failStatus = 'FAIL'
                        self._reasonMsg = string

        for warnPattern in self._warnPatterns:
            if warnPattern.match(string):
                excluded = filter(lambda x:x.match(string), self._excludeWarnPatterns)
                if not list(excluded):
                    if not self._failStatus:
                        self._failStatus = 'WARN'
                        self._reasonMsg = string 
    
        for endFlagPattern in self._endFlagPatterns:
            if endFlagPattern.match(string) :
                self._endFlagHit = True
    
        if self._simEndPattern.match(string):
            return True
