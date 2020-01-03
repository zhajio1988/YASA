#******************************************************************************
# * Copyright (c) 2019, XtremeDV. All rights reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
# * Author: Jude Zhang, Email: zhajio.1988@gmail.com
# *******************************************************************************

"""
Provides documentation and version information
"""
def license_text():
    """
    Returns licence text
    """
    return """YASA
-----

YASA is released under the terms of Apache License, Version 2.0.

Copyright (c) 2019, XtremeDV. Jude Zhang All rights reserved.

uvm
-----
uvm is the Universal Verification Methodology (UVM) reference implementation 
from Accellera.

vcs
-----
VCS is a product of Synopsys, Inc.
Copyright 2003-2013 Synopsys, Inc. All Rights Reserved
You are licensed only to use thise products
for which you have lawfully obtained a valid license key.

irun/xrun
-----
Incisive/Xcelium is a product of Cadence Design Systems, Inc.
(c) Copyright 1995-2014 Cadence Design Systems, Inc. All Rights Reserved
You are licensed only to use thise products
for which you have lawfully obtained a valid license key.
"""

def doc():
    """
    Returns short introduction to YASA
    """
    return r"""What is YASA?
==============

YASA is an open source simulation framework for SystemVerilog/UVM testbentch
released under the terms of Apache License, v. 2.0. 
It support mutli_simulators, multi_languages, lsf etc.
It support several excellent features. Such as:
customized command line option, add any compilation options or simulation options, 
running a testcase with random seeds for several rounds or running a group of 
testcases, each testcase has several command line option.

Typical Usage:
    %> python3 yasaTop.py -h    
    %> python3 yasaTop.py -doc 
    %> python3 yasaTop.py -version
    %> python3 yasaTop.py -t sanity1 -co
    %> python3 yasaTop.py -t sanity1 -r 5 
    %> python3 yasaTop.py -t sanity1 -seed 352938188
    %> python3 yasaTop.py -t sanity1 -seed 352938188 -so
    %> python3 yasaTop.py -g top_smoke -co
    %> python3 yasaTop.py -g top_smoke -p 5


License
=======
""" + license_text()


def version():
    """
    Returns YASA version
    """
    if PRE_RELEASE:
        return '%i.%i.%irc0' % (VERSION[0], VERSION[1], VERSION[2] + 1)

    return '%i.%i.%i' % (VERSION[0], VERSION[1], VERSION[2])


VERSION = (1, 0, 0)

# DO NOT TOUCH: Only set to False by PyPI deployment script
PRE_RELEASE = False
