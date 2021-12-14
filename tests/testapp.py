#!/usr/bin/env python3
# encoding: utf-8

""" This script runs a simulation test of a biosim4 configuration.
    """

_initname = __file__[:-3]  # exclude .py
_appname = "biosim4"
_modname = "%s_mod.py" % _appname
_uiname = "%s_ui" % _appname
_libname = "%s_lib" % _appname
_configfile = "%stest.ini" % _appname
# temporary file used by this app to create test configurations:
_temp_ini = "tmp.ini" 
_version = "21.12.12"


from sys import version_info, platform, argv, exit

try:
    assert version_info >= (3, 4)
except:
    print("Python version >= 3.4 required")
    exit(1)

if platform != "linux":
    print("\nThis test application is running on %s" % platform)
    print("\nReport bugs to https://github.com/davidrmiller/biosim4/\n")


usagemsg = """\nScript for testing a biosim4 simulation.
\ntest.py initializes a test environment and simulation parameters for a biosim4 simulation. Always execute test.py inside the 'tests' working directory. To see a list of configured tests, use the --show flag:

    python3 test.py --show

Run the pre-defined simulation test:

    python3 test.py --test quicktest

To see all available options and flags, run:

    python3 test.py --help


Simulation parameters:

This script uses its own configuration file 'test.ini' for storing and retrieving two sets of parameters:

1) simulation parameters, and
2) expected simulation outcome results

Inspect './configs/test.ini' to see the predefined example 'quicktest'. This test's simulation and result parameters can also be output to the console:

    python3 test.py --test quicktest --params


Configure a new test:

1. Copy the default config file 'biosim4.ini' to the 'configs' directory and rename the copy with the unique name of your new test:

    cp ../biosim4.ini ./configs/my_new_test.ini

2. Edit the new test's parameters in './configs/my_new_test.ini'
3. Import the test parameters into the test environment:

    python3 test.py --import my_new_test.ini

Simulation parameters (from .configs/my_new_test.ini) are converted to test-style format and stored in a new section 'my_new_test' in the configuration file './configs/test.ini'

After being imported, test parameters can be edited directly in the 'test.ini' file.

Result parameters:

Result parameters can be manually added to the config file, or they can be initialed automatically by simply running a test simulation:

    python3 test.py --test my_new_test

After completing the simulation, the script will propose to add result parameters (using actual test result values) to the config file. These can then be manually edited to match variations in test results.
""" % (
    argv[0],
    argv[0],
    argv[0],
)


import argparse

# check args passed from the command line,
argp = argparse.ArgumentParser(
    description = "Application for running biosim4"
    + " simulation tests"
)
argp.add_argument(
    # use this test section
    "--test",
    "-t",
    type = str,
    default=None,
    help="use this simulation test configuration"
)
argp.add_argument(
    # show all test sections found in the config file
    "--show",
    "-s",
    action="store_true",
    default=None,
    help="see a list of configured simulation tests"
)
argp.add_argument(
    # this shows both test amd result params
    "--params",
    "-p",
    action="store_true",
    default=None,
    help="use with --test to see the specified test's config params"
)
argp.add_argument(
    # show result params only
    "--resultparams",
    "-r",
    action="store_true",
    default=None,
    help="use with --test to see the specified test's last results"
)
argp.add_argument(
    "--check",
    "-c",
    action="store_true",
    default=None,
    help="check the test environment"
    # TODO show color [Yes] or [No] env checks
    # offer to repair, else --repair
)
argp.add_argument(
    # use this test section
    "--load",
    "-l",
    type = str,
    default=None,
    help="import parameters for a new test configuration\n"
            + "provide the name of the source .ini file in ./configs/"
)
argp.add_argument(
    "--usage",
    "-u", 
    action="store_true", 
    help="see more detailed usage instructions"
)

args = argp.parse_args()

if args.usage:
    print(usagemsg)
    exit(0)


#
# We made it this far without incident or exiting
# Load additional modules for environment set-up.

import locale
import time
from datetime import timedelta
from pathlib import Path
from pylib import config
import testlib


# the following is for initial config file creation.
# Don't edit here, it will have no effect.
# Instead, add/edit parameters in _configfile 

BS_DEFAULTS = [
    ["internal", "name", _appname],
    ["internal", "version", _version],
    ["internal", "github_url", "https://github.com/davidrmiller/biosim4/"],
    ["quicktest", "description", "Quick test that only runs a few seconds"],
    ["quicktest", "param-stepsPerGeneration", "100"],
    ["quicktest", "param-maxGenerations", "101"],
    ["quicktest", "result-generations", "100"],
    ["quicktest", "result-survivors-min", "980"],
    ["quicktest", "result-survivors-max", "1050"],
    ["quicktest", "result-diversity-min", "0.98465"],
    ["quicktest", "result-diversity-max", "0.999"],
    ["slowtest", "description", "Slow test that runs for years"],
    ["slowtest", "param-stepsPerGeneration", "10000"]
]


# set US locale to ensure well-defined behavior for number formatting.
for loc in ["en_US.UTF8", "en_EN", "C"]:
    try:
        locale.setlocale(locale.LC_NUMERIC, loc)
        break
    except locale.Error:
        continue

# Check paths and files
try:
    thispath = Path(__file__)
    assert thispath.parent == Path.cwd()
    testspath = thispath.parent
    configspath = testspath.joinpath("configs")
    configfile = configspath.joinpath(_configfile)
    biosimpath = testspath.parent
    defaultconfigfile = biosimpath.joinpath("biosim4.ini")
    # May not exist at this time:
    #logfile = ".logs/epoch-log.txt"
    #print("testconfig: %s" % filepath)
    
    # biosim4 does not like an abspath to configfile:
    #tempini = configspath.joinpath(_temp_ini)
    # So, map temporary ini file relative to project root:
    #tempini = "./tests/configs/%s" % _temp_ini
    # afterthought: just use the filename _temp_ini (defined at top of this file)
except AssertionError:
    print("testapp.py must be executed in the 'tests' directory")
    exit(1)
except Exception as e:
    print("Environment exception:\n%s" % e)
    exit(1)


#
# instantiate configparser 
#
thisconfig = config.TestConfig(str(configfile))
thisconfig.init_defaults(BS_DEFAULTS)

if args.load:
    param_src = None
    try:
        param_src = Path.cwd().joinpath("configs", fname)
        assert param_src.exists()
    except:
        print("\n%s not found in the ./configs/ directory\n" % param_src)
        exit(1)
    stem = param_src.stem
    thisname = stem.name
    # add section with thisname, exit if thisname already exists
    try:
        thisconfig.add_section(thisname)
    except:
        print("add_section exception: section named %s already exists" % thisname)
    try:
        testlib.loadStdParamsFromFile(thisconfig, thisname, param_src)
    except Exception as e:
        print("load exception: ", e)
        exit(1)
    try:
        testlib.writeTestParamsToConfig(thisconfig, False)
    except Exception as e:
        print("save exception: ", e)
        exit(1)

if args.check:
    print("working in", str(Path.cwd()))
    print("app configpath:", configspath)
    print("app configfile:", configfile)
    print("Ref: biosim4 default config file: %s" % defaultconfigfile)
    exit(0)
if args.show:
    tests = testlib.showTests(thisconfig)
    print("\nConfigured tests:\n")
    for t in tests:
        print(t)
    print()
elif args.test:
    #TODO change writeStdTestFile() to take t (section) as arg
    t = testlib.getTestSection(thisconfig, args.test)
    if args.params:
        print("\n%s parameters:\n" % args.test)
        for k in sorted(t):
            if k.startswith('param'):
                print("%s= %s" % (k, t[k]))
        try:
            resdict, comp = testlib.getResultParams(thisconfig, args.test)
            testlib.showResultParams(resdict)
        except Exception as e:
            print("Exception getting results params:\n%s" % e)
        exit(0)

    if args.resultparams:
        try:
            resdict, comp = testlib.getResultParams(thisconfig, args.test)
            testlib.showResultParams(resdict)
        except Exception as e:
            print("Exception getting results params:\n%s" % e)
        exit(0)
    try:
        testlib.TEMPinifile = _temp_ini
        print("Running %s sim" % t.name)
        print(t['description'])
        #print(dir(t))
        testlib.writeStdTestFile(thisconfig, args.test)
        # start objetive time
        start_time = time.monotonic()
        # start processor time
        cpu_start_time = time.perf_counter()
        #
        # simulation run
        proc = testlib.runTest()
        #
        cpu_end_time = time.perf_counter()
        end_time = time.monotonic()
        print(proc)
        print("completed test")
        print("clock time: %s seconds" % timedelta(seconds=end_time - start_time))
        print("CPU time: %s seconds" % (cpu_end_time - start_time))
        #ll = testlib.readlog()
        testlib.resultsAnalysis(thisconfig, args.test)
    except Exception as e:
        print("test exception:\n%s" % e)
        exit(1)
else:
    print("\nYou must specify the name of a test configuration\n")
    print("Example:\tpython3 %s --test quicktest [other options]" % _appname)
    print("\nTo see the available test config names, run:\n")
    print("\tpython3 %s --show\n" % _appname)


print("%s done" % _appname)
exit(0)
