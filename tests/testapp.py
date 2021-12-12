#!/usr/bin/env python3
# encoding: utf-8

""" This script runs a sim test of a biosim4 configuration.
    """

_initname = __file__[:-3]  # exclude .py
_appname = "biosim4"
_modname = "%s_mod.py" % _appname
_uiname = "%s_ui" % _appname
_libname = "%s_lib" % _appname
_configfile = "%stest.ini" % _appname
# temporary file used by this app to create test configurations 
_temp_ini = "tmp.ini" 
_version = "21.12.03"


from sys import version_info, platform, argv, exit

try:
    assert version_info >= (3, 4)
except:
    print("Python version >= 3.4 required")
    exit(1)

if platform != "linux":
    print("\nThis test utility was developed on Linux")
    print("If running on any other OS, your mileage may vary.")
    print("\nReport bugs to https://github.com/davidrmiller/biosim4/\n")


usagemsg = """\nbiosim4 test application.
\nThis script initializes the BioSim4 testing environment
    and menu interface. It provides utilities for ... testing biosim4 ... configure sim parameters
etc.

To use this utility interactively simply start the menu driven user interface:

    python3 %s menu

To see a list of commands run:

    python3 %s help

If you already know which configured test you want to run,
simply specify its name:

    python3 %s quicktest

or type 'h' while running the user interface.

* Python version 3 minimum. 
""" % (
    argv[0],
    argv[0],
    argv[0],
)

helpmsg = """\nFirstly, be sure that you are executing this script in the tests directory.  

To use this utility simply start the menu driven user interface:

    python3 %s menu

Available commands are:

    ...
    ...                                                  

""" % (
    argv[0]
)

import argparse

# before we can start the user interface we check
# args passed from the command line,
argp = argparse.ArgumentParser(
    description = "Trade monitor of RESTful API data"
    + " and trading bot experimentation framework"
)
argp.add_argument(
    "--test",
    type = str,
    #action="store_true",
    default=None,
    help="use this simulation test configuration"
)
argp.add_argument(
    "--show",
    action="store_true",
    #type = str,
    default=None,
    help="see a list of configured simulation tests"
)
argp.add_argument(
    # this should show both test amd result params
    "--params",
    action="store_true",
    #type = str,
    default=None,
    help="use with --test to see the specified test's config params"
)
argp.add_argument(
    # no, the user should only see results after actually
    # running a test
    "--results",
    action="store_true",
    #type = str,
    default=None,
    help="use with --test to see the specified test's last results"
)
argp.add_argument(
    "--check",
    action="store_true",
    #type = str,
    default=None,
    help="check the test environment"
    # show color [Yes] or [No] env checks
    # offer to repair, else --repair
)
argp.add_argument(
    "--usage", 
    action="store_true", 
    help="see more detailed usage instructions"
)

args = argp.parse_args()

if args.usage:
    print(usagemsg)
    exit(0)

try:
    print("passed argv[1]:", argv[1])
    #if not argv[1].startwith("-"):
    testsim = argv[1]
except:
    print("no argv[1]. Showing usage...")
    #testsim = None
    print(usagemsg)
    exit(1)

import locale
from pathlib import Path
#from os.path import expanduser
from pylib import config
import testlib
#import testui
#import subprocess
#from sys import stdout, stderr

# the following is for initial config file creation.
# Don't edit here, it will have no effect.

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


# set US locale to ensure well defined behavior for number formatting.
for loc in ["en_US.UTF8", "en_EN", "C"]:
    try:
        locale.setlocale(locale.LC_NUMERIC, loc)
        break
    except locale.Error:
        continue

# Check paths and files
#currentdir = path.dirname(__file__)
try:
    thispath = Path(__file__)
    assert thispath.parent == Path.cwd()
    testspath = thispath.parent
    print("working in", str(Path.cwd()))
    configspath = testspath.joinpath("configs")
    print("app configpath:", configspath)
    configfile = configspath.joinpath(_configfile)
    print("app configfile:", configfile)
    biosimpath = testspath.parent
    defaultconfigfile = biosimpath.joinpath("biosim4.ini")
    # May not exist at this time:
    #logfile = ".logs/epoch-log.txt"
    #print("testconfig: %s" % filepath)
    print("defaultconfig: %s" % defaultconfigfile)
    # biosim4 does not like an abspath to configfile:
    #tempini = configspath.joinpath(_temp_ini)
    # So, map temporary ini file relative to project root:
    #tempini = "./tests/configs/%s" % _temp_ini
    # Nah, just send the filename _temp_ini
    if testsim:
        simfile = configspath.joinpath(testsim, ".ini")
        print("sim config: %s" % simfile)
except AssertionError:
    print("testapp.py must be executed in the 'tests' directory")
    exit(1)
except Exception as e:
    print("Environment exception:\n%s" % e)
    exit(1)

#thisconfig = config.ToolConfig("./configs/%s" % (_configfile))
thisconfig = config.TestConfig(str(configfile))
thisconfig.init_defaults(BS_DEFAULTS)

if args.show:
    print("args.show: ", args.show)
    tests = testlib.showTests(thisconfig)
    for t in tests:
        print(t)
elif args.test:
    try:
        t = testlib.getTestSection(thisconfig, args.test)
        print("will run %s sim" % t.name)
        print(t['description'])
        print(dir(t))
    except Exception as e:
        print("test exception:\n%s" % e)
        exit(1)
    
    if args.params:
        for k in sorted(t):
            print("%s= %s" % (k, t[k]))
        exit(0)
    if args.results:
        testlib.resultsAnalysis(thisconfig, args.test)

#TODO read default configfile to create simfile containing all params (or have biosim4 add provided params to hardcoded default params)
#TODO implement passing test to run from cmd line (prior to menu)
#TODO add new test via --add arg + provide ini file

#test_cli ?
#testui.main(thisconfig, _temp_ini, testsim)

print("%s done" % _appname)
