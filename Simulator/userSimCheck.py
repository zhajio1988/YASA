import re
from simCheck import *
class userSimCheck(vcsSimCheck):
    regModelWarnPattern = r'UVM_WARNTNG .+: reporter \[UVM\/RSRC\/NOREGEX\] a resource with meta characters in the field name has been created.*'

    def __init__(self):
        super (userSimCheck, self).__init__()
        self.setExcludeWarnPatterns(userSimCheck.regModelWarnPattern)
