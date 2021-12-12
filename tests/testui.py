
from pathlib import Path
from pylib import config
import testlib

global tCURR_TEST
tCURR_TEST = None
global tCONFIG
tCONFIG = None

#[ ] TODO - add ref objs: quicktest and default configs for 
# comparisons. 
# e.g. quicktest results are calibrated to specific params.
#       (allow but discourage the user from changing these)
# e.g. user may want to use default config as base
#[ ] TODO code 'result' reading, creation and updates
#       (provided curr config does not deviate from ref) 
#       (updates to result min/max only if ref quicktest passed
#        first)
#[ ] TODO create new test from scratch or from existing.
#[ ] TODO view existing tests (sections) from init and from menu
#[ ] TODO manage sections (change name, change param vals, backup
#       section, delete section, add new params)
#[ ] TODO run test straight from init (i.e. import & use testlib)
#[ ] TODO add speed/time measure
#[ ] TODO tidy code, remove unused code & comments, PEP8
#[ ] TODO check if config contains release params
#       if not, then offer user to 
#       1) add to config file and reload or
#       2) run test(s) to calibrate results, add to config
#[ ] TODO define test env [internal] dirs & files

#[ ] TODO main repo: testapp + testlib only
#[ ] TODO own repo: boisimtool:: ui + matplot + genome edit, rng
#[ ] TODO custom docker to run biosim4 with ZMQ start & comms
#[ ] TODO think abt p2p / blockchain


def showParams():

    global tCONFIG, tCURR_TEST

    print("tCONFIG= ", tCONFIG)
    print("tCURR_TEST= ", tCURR_TEST)

    if tCONFIG and tCURR_TEST:
        section = tCONFIG[tCURR_TEST]
        print("\n[%s]" % tCURR_TEST)
        # sort alphanumerically
        slist = list()
        for k in section:
            slist.append(k)
        for k in sorted(slist):
            print("%s= %s" % (k, section[k]))
        #for k, v in section.items():
        #    print("%s= %s" % (k, v))
        print()


def printproc(process):
    print()
    print(process.stdout)
    print()
    print(process.stderr)


def quit():
    usrquit = input("quit? (y/N) ")
    if usrquit == "y":
        exit(0)
    else:
        return

def wait():
    print()
    i = input("press any key...")
    

###
###   menu

def menu():
    """ Main fn() consisting of conditionals that evoke either   
        local functions or functions imported from the testlib module.
        """
    global tCURR_TEST, tCONFIG

    page1 = """

    run a simulation test               - test
    results of most recent sim test     - results
    display active test parameters      - showconfig
    select another test                 - selectconfig
    clear active test parameters        - clearconfig
    reload test parameters              - reloadconfig
    save current parameters to file     - saveconfig
    load sim parameters from file       - load
    quit                                - quit or <Ctrl+C>

    | active test:  %s

""" % tCURR_TEST

    try:
        print(page1)
        prompt = input("menu cmd> ")
        if prompt == "":
            return
        else:
            userstr = str.split(prompt)
            print(userstr)

        # Conditionals

        if userstr[0] == "test":

            if not tCURR_TEST:
                tCURR_TEST = "quicktest"
            testlib.writeStdTestFile(tCONFIG, tCURR_TEST)
            proc = testlib.runtest()
            print("completed test")
            #ll = testlib.readlog()
            testlib.resultsAnalysis(tCONFIG, tCURR_TEST)
            wait()
            return

        elif userstr[0] == "results":
            testlib.resultsAnalysis(tCONFIG, tCURR_TEST)
            wait()
            return


        elif userstr[0] == "load":
            param_src = None
            print("\nMove the .ini file you want to load to the ./configs directory.\nNext you will be asked to provide its filename.\n")
            while True:
                fname = input("name of the config file you want to load: ")
                param_src = Path.cwd().joinpath("configs", fname)
                #TODO use testlib.checkFileExists() instead
                if param_src.exists():
                    break
                else:
                    print("invalid filename\n")
                    continue
            #TODO offer to inspect contents
            proceed = input("\nload parameters into %s ? (y/N) " % tCURR_TEST)
            if proceed not in ["y", "Y"]:
                return
            testlib.loadStdParamsFromFile(tCONFIG, tCURR_TEST, param_src)
            look = input("\nShow parameters ? (y/N) ") 
            if look in ["y", "Y"]:
                showParams()
        
        elif userstr[0] == "reloadconfig":
            print("unsaved parameters and results will be lost.")
            proceed = input("\nreload config file? (y/N) ")
            if proceed in ["y", "Y"]:
                testlib.readTestParamsFromConfig(tCONFIG)

        elif userstr[0] == "saveconfig":
            sort = False
            proceed = input("\nsave modified parameters for %s ? (y/N) " % tCURR_TEST)
            if proceed in ["y", "Y"]:
                usort = input("sort params alphabetically? (y/N) ")
                if usort in ["y", "Y"]:
                    sort = True
                testlib.writeTestParamsToConfig(tCONFIG, sort)
            wait()

        elif userstr[0] == "clearconfig":
            proceed = input("\nclear parameters for %s ? (y/N) " % tCURR_TEST)
            if proceed in ["y", "Y"]:
                tCONFIG[tCURR_TEST].clear()

        elif userstr[0] == "selectconfig":
            # select a diff test
            #TODO check for modifications to current test
            #   prompt user to save
            #   display all sections and allow user to select
            pass

        elif userstr[0] == "showconfig":
            showParams()
            wait()

        elif userstr[0] in ["q", "quit"]:
            quit()

        else:
            print("unknown command")
            wait()
            return

    except KeyboardInterrupt:
        print("\n<Ctrl+C> closes the test menu")
        print("\nunsaved changes will be lost...")
        quit()

    except Exception as e:
        print("ui exception:\n%s" % e)


def main(thisconfig, tempini, testname):

    global tCURR_TEST, tCONFIG

    if not testname:
        tCURR_TEST = "quicktest"
    else:
        tCURR_TEST = testname

    tCONFIG = thisconfig
    #testlib.APPinifile = appini
    testlib.TEMPinifile = tempini

    while True:
        print("in main()")
        menu()

if __name__ == "__main__":

    try:
        print("in __main__")
    except KeyboardInterrupt:
        print("closing UI...")
