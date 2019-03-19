*******************************************************************************
# YASA
Yet Another Simulation Architecture <\br>
Author: Jude Zhang, Email: zhajio.1988@gmail.com

YASA is an open source simulation framework for SystemVerilog/UVM testbentch
released under the terms of Apache License, v. 2.0. 
It support mutli_simulators, multi_languages, lsf etc.
It support several excellent features. Such as:
customized command line option, add any compilation options or simulation options, 
running a testcase with random seeds for several rounds or running a group of 
testcases, each testcase has several command line option.

### Typical Usage:
    %> python3 yasaTop.py -h    
    %> python3 yasaTop.py -doc 
    %> python3 yasaTop.py -version
    %> python3 yasaTop.py -t sanity1 -co
    %> python3 yasaTop.py -t sanity1 -r 5 
    %> python3 yasaTop.py -t sanity1 -seed 352938188
    %> python3 yasaTop.py -t sanity1 -seed 352938188 -so
    %> python3 yasaTop.py -g top_smoke -co
    %> python3 yasaTop.py -g top_smoke -p 5

### help
    %> python3 yasaTop.py -h

### doc 
    %> python3 yasaTop.py -doc

### copyright
******************************************************************************
* Copyright (c) 2019, XtremeDV. All rights reserved.
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://www.apache.org/licenses/LICENSE-2.0
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
* Author: Jude Zhang, Email: zhajio.1988@gmail.com
*******************************************************************************
