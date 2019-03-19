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

### Dependencies:
* python 3.6
* configobj
* argparse

* vcs or incisive simulator

### Typical Usage:
* show help doc

    echo /usr/local/bin/fish | sudo tee -a /etc/shells

    %> python3 yasaTop.py -h 
    
* show YASA doc file and copyright
    %> python3 yasaTop.py -doc
* show YASA version
    %> python3 yasaTop.py -version
    %> python3 yasaTop.py -t sanity1 -co
    %> python3 yasaTop.py -t sanity1 -r 5 
    %> python3 yasaTop.py -t sanity1 -seed 352938188
    %> python3 yasaTop.py -t sanity1 -seed 352938188 -so
    %> python3 yasaTop.py -g top_smoke -co
    %> python3 yasaTop.py -g top_smoke -p 5

### help:
    %> python3 yasaTop.py -h
```bash
******************************************************************************
usage: yasaTop.py [-h] [-g GROUP] [-show {test,group,build}] [-so] [-co]
                  [-b BUILD] [-test_prefix TESTPREFIX] [-r REPEAT] [-c]
                  [-fail-fast] [-o OUTPUT_PATH] [-x [XUNIT_XML]]
                  [-xunit-xml-format {jenkins,bamboo}] [-exit-0]
                  [-dont-catch-exceptions] [-v] [-q] [-no-color]
                  [-log-level {info,error,warning,debug}] [-p NUM_THREADS]
                  [-u] [-version] [-doc] [-t TEST] [-w [{vpd,fsdb,gui}]]
                  [-cov [COV]] [-seed SEED] [-vh] [-prof]
                  [-wave_name WAVE_NAME] [-pre_comp_option PRE_COMP_OPTION]
                  [-comp_option COMP_OPTION]
                  [-post_comp_option POST_COMP_OPTION]
                  [-pre_sim_option PRE_SIM_OPTION] [-sim_option SIM_OPTION]
                  [-post_sim_option POST_SIM_OPTION]
                  {lsf} ...

Yet another simulation architecture® top scripts

positional arguments:
  {lsf}

optional arguments:
  -h, --help            show this help message and exit
  -g GROUP, -group GROUP
                        assign test group name
  -show {test,group,build}
                        show test list, group list or build list
  -so, -simonly         Only run simulation without compile step
  -co, -componly        Only compile without running tests
  -b BUILD, -build BUILD
                        assign a specific build
  -test_prefix TESTPREFIX
                        add testcase prefix
  -r REPEAT, -repeat REPEAT
                        testcase will random run in given repeat round
  -c, -clean            Remove output build dir
  -fail-fast            Stop immediately on first failing test
  -o OUTPUT_PATH, -output-path OUTPUT_PATH
                        Output path for compilation and simulation artifacts
  -x [XUNIT_XML], -xunit-xml [XUNIT_XML]
                        Xunit test report .xml file
  -xunit-xml-format {jenkins,bamboo}
                        Only valid with --xunit-xml argument. Defines where in
                        the XML file the simulator output is stored on a
                        failure. "jenkins" = Output stored in <system-out>,
                        "bamboo" = Output stored in <failure>.
  -exit-0               Exit with code 0 even if a test failed. Still exits
                        with code 1 on fatal errors such as compilation
                        failure
  -dont-catch-exceptions
                        Let exceptions bubble up all the way. Useful when
                        running with "python -m pdb".
  -v, -verbose          Print test output immediately and not only when
                        failure
  -q, --quiet           Do not print test output even in the case of failure
  -no-color             Do not color output
  -log-level {info,error,warning,debug}
                        Log level of Yasa internal python logging. Used for
                        debugging
  -p NUM_THREADS, -num-threads NUM_THREADS
                        Number of tests to run in parallel. Test output is not
                        continuously written in verbose mode with p > 1
  -u, -unique_sim       Do not re-use the same simulator process for running
                        different test cases (slower)
  -version              show program's version number and exit
  -doc                  print doc file
  -t TEST, -test TEST   assign test name
  -w [{vpd,fsdb,gui}], -wave [{vpd,fsdb,gui}]
                        dump waveform(vpd or fsdb), default fsdb
  -cov [COV]            collect code coverage, default all kinds
                        collect(line+cond+fsm+tgl+branch+assert
  -seed SEED            set testcase ntb random seed
  -vh                   set verbosity to UVM_HIGH
  -prof                 user defined option
  -wave_name WAVE_NAME  set fsdb waveform name
  -pre_comp_option PRE_COMP_OPTION
                        previous compile option
  -comp_option COMP_OPTION
                        compile option
  -post_comp_option POST_COMP_OPTION
                        post compile option
  -pre_sim_option PRE_SIM_OPTION
                        previous sim option
  -sim_option SIM_OPTION
                        sim_option
  -post_sim_option POST_SIM_OPTION
                        post sim option
```
******************************************************************************

### doc:
    %> python3 yasaTop.py -doc

### copyright:
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
