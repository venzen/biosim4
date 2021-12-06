#!/usr/bin/env python3
# encoding: utf-8

""" This script initializes the BioSim4 testing environment
    and menu interface.
    """

_initname = __file__[:-3]  # exclude .py
_appname = "biosim4"
_modname = "%s_mod.py" % _appname
_uiname = "%s_ui" % _appname
_libname = "%s_lib" % _appname
_configfile = "%stest.ini" % _appname
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


usagemsg = """\nBioSim4 testing utilities.
\nThis script initializes the BioSim4 testing environment
    and menu interface. It provides utilities for ... testing biosim4 ... configure sim parameters
etc.

To use this utility interactively simply start the menu driven user interface:

    python3 %s menu

To see a list of commands run:

    python3 %s help

If you already know which configured test you want to run,
simply specify its name:

    python3 %s -t quicktest

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
    "--module",
    action="store",
    default=_modname,
    help="name of module files, comma separated list, default=marginwatch.py",
)
argp.add_argument(
    "--port", action="store", default="5510", help="specify the SUB ZeroMQ port"
)
argp.add_argument(
    "--address",
    action="store",
    default=None,
    help="specify the ZeroMQ trades PUB address",
)
argp.add_argument(
    "--setup-account",
    action="store_true",
    help="prompt for API secret, encrypt it and then exit."
    "Specify acc1 or acc2 using the --acc option",
)
argp.add_argument(
    "--colors",
    action="store_true",
    help="prompt for instrument colors, store and exit.",
)
argp.add_argument(
    "--offline",
    action="store_true",
    default=False,
    help="simulation mode using locally stored positions and orders",
)
argp.add_argument(
    "--usage", action="store_true", help="see more detailed usage instructions"
)

args = argp.parse_args()

if args.usage:
    print(usagemsg)
    exit(0)


import locale
from os import path
#from os.path import expanduser
from pylib import config
import testui
#import subprocess
from sys import stdout, stderr

# the following is for initial config file creation.
# Don't edit here, it will have no effect.
# Instead, use commandline args to make config changes
# The 'ui' section defines colors that are used to display instruments consistently
# across various satellite apps. Avoid red, blue & green.
BS_DEFAULTS1 = [
    ["internal", "name", _appname],
    ["internal", "version", _version],
    ["internal", "github_url", "https://github.com/davidrmiller/biosim4/"],
    ["quicktest", "description", "Quick test that only runs a few seconds"],
    ["quicktest-params", "stepsPerGeneration", "100"],
    ["quicktest-params", "maxGenerations", "2"],
    ["quicktest-results", "generations", "100"],
    ["quicktest-survivors", "min", "980"],
    ["quicktest-survivors", "max", "1050"],
    ["quicktest-diversity", "min", "0.98465"],
    ["quicktest-diversity", "max", "0.999"],
    ["slowtest", "description", "Slow test that runs for years"],
    ["slowtest-params", "stepsPerGeneration", "10000"]
]

BS_DEFAULTS2 = [
    ["internal", "name", _appname],
    ["internal", "version", _version],
    ["internal", "github_url", "https://github.com/davidrmiller/biosim4/"],
    ["quicktest", "description", "Quick test that only runs a few seconds"],
    ["quicktest", "param-stepsPerGeneration", "100"],
    ["quicktest", "params-maxGenerations", "2"],
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
    testspath = Path(__file__)
    assert testspath == Path.cwd()
    configspath = testspath.joinpaths("configs", _configfile))
    configfile = configspath.joinpaths(_configfile)
    biosimpath = testspath.parent
    defaultconfigfile = biosimpath.joinpaths("biosim4.ini"))
    # May not exist at this time:
    #logfile = ".logs/epoch-log.txt"
    print("testconfig: %s" % filepath)
    print("defaultconfig: %s" % defaultconfigfile)
    if sim:
        simfile = configspath.joinpaths(simname)
        print("sim config: %s" % simfile)
except AssertionError:
    print("testapp.py must be executed in the 'tests' directory")
    exit(1)
except Exception as e:
    print("Environment exception:\n%s" % e)
    exit(1)

#thisconfig = config.ToolConfig("./configs/%s" % (_configfile))
thisconfig = config.ToolConfig(str(configfile))
thisconfig.init_defaults(BS_DEFAULTS2)

#TODO read default configfile to create simfile containing all params (or have biosim4 add provided params to hardcoded default params)
#TODO implement passing test to run from cmd line (prior to menu)
#TODO add new test via --add arg + provide ini file

#test_cli ?
testui.main(thisconfig, simname)

print("%s shutdown complete" % _appname)
