import re
from Simulator.vcsInterface import vcsSimCheck
class userSimCheck(vcsSimCheck):
    regModelWarnPattern = r'UVM_WARNTNG .+: reporter \[UVM\/RSRC\/NOREGEX\] a resource with meta characters in the field name has been created.*'
    cevaTestFailPattern = r'^TEST FAILED'
    cevaReportPattern = r'.*SIMULATION SUMMARY.*'    

    def __init__(self):
        super (userSimCheck, self).__init__()
        self.setExcludeWarnPatterns(userSimCheck.regModelWarnPattern)
        self.setErrPatterns(userSimCheck.cevaTestFailPattern)
        self.setEndFlagPatterns(userSimCheck.cevaReportPattern)
