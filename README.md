*******************************************************************************
# YASA

Yet Another Simulation Architecture

Author: Jude Zhang, Email: zhajio.1988@gmail.com

YASA is an open source simulation framework for SystemVerilog/UVM testbentch
released under the terms of Apache License, v. 2.0. 
It support mutli_simulators, multi_languages, lsf etc.
It support several excellent features. Such as:
customized command line arguments, can add any compilation options or simulation options, 
can running a testcase with random seeds for several rounds or running a group of 
testcases, each testcase has several command line options.

### Dependencies:
* python 3.6
* configobj
* argparse

* vcs or incisive simulator

### Typical Usage:
* show help doc

    `%> python3 yasaTop.py -h`
    
* show YASA doc file and copyright

    `%> python3 yasaTop.py -doc`
    
* show YASA version

    `%> python3 yasaTop.py -version`
    
* compile only, build candy_lover, unique_sim mode

    `%> python3 yasaTop.py -b candy_lover -co -u`
    
* compile only, testcase sanity1

    `%> python3 yasaTop.py -t sanity1 -co`
    
* running testcase sanity1, 5 times,each time with random seed

    `%> python3 yasaTop.py -t sanity1 -r 5`
    
* running testcase sanity1 with seed 352938188

    `%> python3 yasaTop.py -t sanity1 -seed 352938188`

* running testcase sanity1 with seed 352938188, sim only

    `%> python3 yasaTop.py -t sanity1 -seed 352938188 -so`
    
* compile only, group top_smoke

    `%> python3 yasaTop.py -g top_smoke -co`
    
* running group top_smoke, use 5 threads

    `%> python3 yasaTop.py -g top_smoke -p 5`

### help:
    %> python3 yasaTop.py -h
******************************************************************************
```
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
    
### License:
******************************************************************************
```
=======
YASA
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

irun
-----
Incisive is a product of Cadence Design Systems, Inc.
(c) Copyright 1995-2014 Cadence Design Systems, Inc. All Rights Reserved
You are licensed only to use thise products
for which you have lawfully obtained a valid license key.
```
*******************************************************************************
