
#from time import sleep, ctime
from pathlib import Path
import subprocess
from pylib import config

global TEMPinifile
TEMPinifile = None


#TODO initialize object (perhaps istantiate class singleton?)
# sectionss, active class, 
# update sections if added, deleted, modified

def updateSections(thisconfig):
    """ Re-read the test config INI file. Load into the
        test environment config object.
        """

    raise NotImplementedError


def showTests(thisconfig):
    """ display all test sections in app config file
        """
    sections = thisconfig.sections()
    tests = [s for s in sections if s != "internal"]
    
    return tests


def getTestSection(thisconfig, testname):
    """ Select the test section 'testname' from the
        test config object. 
        """
    #print("getting config section from ", thisconfig)
    #print("testname ", testname)
    s = None
    try:
        s = thisconfig[testname]
    except KeyError:
        print("section '%s' does not exist")
        # create it here
    except Exception as e:
        print("getTestSection() exception:\n", e)

    return s


def checkFileExists(filename, create=False):
    """ Check if file 'filename' exists. If not, create it. 
        """

    try:
        assert Path(filename).exists()
    except:
        #TODO ensure it is one of the expected patterns/locations
        #       else warn user and exit with an error
        if create:
            # create file
            Path(filename).touch(exist_ok=True)
            print("checkFileExists() created file ", filename)
        else:
            return False
    
    return True

def readTestParamsFromConfig(thisconfig):
    """ (Re)read the test config INI file. 
        """

    try:
        # the config module's load() method loads section
        # keys and values from '.tests/configs/testapp.ini'
        # this filename is an attribute of the config class
        thisconfig.load()
        print("Success.\n")
    except Exception as e:
        print("readTestParams() exception:\n%s" % e)


def writeTestParamsToConfig(thisconfig, sort):
    """ Save the test config object to test config INI file.
        """
    try:
        # the config module's save() method writes section
        # keys and values to '.tests/configs/testapp.ini'
        # this filename is an attribute of the config class
        thisconfig.save(sort)
        print("Success.\n")
    except Exception as e:
        print("writeParams() exception:\n%s" % e)


def readStdConfigFile(param_src):
    """ Read a biosim4 style INI file and cast as a
        dictionary.
        """

    sectiondict = dict()

    checkFileExists(param_src, True)
    try:
        print("reading", param_src)
        with open(param_src, 'r') as src:
            print("src: ", src)
            for line in src:
                if line.startswith("#") or line.startswith(";") or line.startswith(" ") or line.startswith("\n"):
                    continue
                keyval = str.split(line, "=")
                #TODO more succinct way of doing this?
                k = str.strip(keyval[0])
                v = str.strip(keyval[1]) 
                sectiondict[k] = v
        print("completed reading INI source file")
        
        return (sectiondict, True)

    except Exception as e:
        print("readStdConfigFile() exception: %s" % e)

        return (sectiondict, False)


def loadStdParamsFromFile(thisconfig, testname, param_src):
    """ Load biosim4 parameters from an INI file and
        load them into the testing environment in 
        test config format.
        e.g. MaxGenerations -> param-maxgenerations 
        """

    sectiondict, res = readStdConfigFile(param_src)
    numparams = len(sectiondict)
    if not res:
        return False
    elif numparams == 0:
        print("file contains no parameters")
    print("got %s parameters" % numparams)

    section = getTestSection(thisconfig, testname)
    try:
        for k, v in sectiondict.items():
            # check k against default ref params for validity
            k = "param-" + k
            section[k] = v

    except Exception as e:
        print("loadStdParams() exception: %s" % e)


def writeStdTestFile(thisconfig, testname):
    """ Write a biosim4 style INI file prior to running
        a sim test. Test-style params are converted to
        biosim4-style params before being written to file.
        """
    # see https://realpython.com/python-pathlib/
    # can also use methods to Path
    # e.g. .write_text(): open the path, write string data
    global TEMPinifile  # 'tmp.ini'

    s = getTestSection(thisconfig, testname)

    try:
        #if not TEMPinifile.exists():
        #    source.replace(destination)

        # get the absolute path to 'tmp.ini'
        pathstr = "./configs/%s" % TEMPinifile
        relpath = Path(pathstr)
        abspath = relpath.resolve()
        if checkFileExists(abspath, create=True):
            print("using temp file ", abspath)
            with open(abspath, 'w') as ini:
                for k, v in s.items():
                    if 'param' in k:
                        p = str.split(k, '-')
                        ini.write(p[1] + "= " + v + "\n")

    except Exception as e:
        print("writeTestFile() exception: %s" % e)

    
def runtest():
    """ docstring
        """

    global TEMPinifile

    relpath = "./tests/configs/%s" % TEMPinifile
    shellcmd = "./bin/Release/biosim4 %s" % relpath
    print("Running the simulation...")
    # launch biosim4
    process = subprocess.run(shellcmd, cwd='../', shell=True, capture_output=False, text=True, check=True)
    
    return process
    

def readlog():
    """ docstring
        """
    # analysis
    #path = Path(__file__).parent.joinpath('logs/epoch-log.txt')
    with open('../logs/epoch-log.txt', 'r') as log:
        for line in log:
            pass
        #last_line = line

    return line


def getResultParams(thisconfig, testname):
    """ docstring
        """

    section = getTestSection(thisconfig, testname)
    resultdict = dict()
    for k, v in section.items():
        if 'result' in k:
            kk = str.split(k, "-", 1)  #only split at first "-"
            #print("k, kk", kk)
            try:
                v = int(v)
            except:
                v = float(v)
            resultdict[kk[1]] = v
    if len(resultdict) == 7:
        return (resultdict, True)
    else:
        return (resultdict, False)

def updateResultParams(thisconfig, testname, addrpdict):

    section = getTestSection(thisconfig, testname)
    for k, v in addrpdict.items():
        section[k] = str(v)


def showResultParams(resultdict):

    # display params in dict 
    if len(resultdict) > 0:
        count = 0
        print("\ndefined result params:\n")
        for k, v in resultdict.items():
            print("%s= %s" % (k, v))
            count += 1
        print("%i result param(s) missing" % (7 - count))
    else:
        print("\nthis test has no result params defined")

def resultsAnalysis(thisconfig, testname):
    """ result-generations = int
        result-survivors-min = int
        result-survivors-max = int
        result-diversity-min = float
        result-diversity-max = float
        result-genomesize = int
        result-kills = int
        """
    
    last_line = readlog()
    reslist = str.split(last_line)
    print("reslist: ", reslist)
    if len(reslist) != 5:
        print("Error: unexpected line length in logfile:")
        print(last_line)
        exit(1)

    rp, complete = getResultParams(thisconfig, testname)
    print("rp: ", rp)
    addrp = False
    addrpdict = dict()
    #updaterps = False
    if not complete:
        # either:
        # 1) no results defined
        # 2) incomplete set of resultparams (7)
        # offer to create result params from this test
        #updateResultParams() and write to test config file
        print("incomplete set of results params")
        showResultParams(rp)
        print("\nYou can cancel and manually update the test config file with the missing params, then reload it and run this test again. Or proceed and the missing result params will be added to this test's config\n")
        uadd = input("proceed and add result params? (Y/n) ")
        if uadd in ["y", "Y"]:
            addrp = True
    try:
        generation = int(reslist[0])
        survivors = int(reslist[1])
        diversity = float(reslist[2])
        genomeSize = int(reslist[3])
        kills = int(reslist[4])
        success = 1
    except Exception as e:
        print("\nexception reading logfile:" % e)

    # conditionsals below could be done with a loop that
    # calls a fn() addOrUpdateResultParam()
    # could use param 'maxgenerations' - 1 here, instead...
    if 'generations' in rp:
        if generation != rp['generations']:
            print("Error: generation:: expected %i, got %i" % (rp['generations'], generation))
            success = 0
            # option to update result param
    elif addrp:
        print("adding param 'result-generations = %s' to config" % generation)
        addrpdict['result-generations'] = generation
        success = 0

    if 'survivors-min' in rp and 'survivors-max' in rp:
        if survivors <= rp['survivors-min'] or survivors > rp['survivors-max']:
            print("Error: survivors:: expected %i to %i, got %i" % (rp['survivors-min'], rp['survivors-max'], survivors))
            success = 0
    elif addrp:
        print("adding param 'survivors-min = %s' to config" % survivors)
        addrpdict['result-survivors-min'] = survivors
        print("adding param 'survivors-max = %s' to config" % survivors)
        addrpdict['result-survivors-max'] = survivors
        success = 0

    if 'diversity-min' in rp and 'diversity-max' in rp:
        if diversity < rp['diversity-min'] or diversity > rp['diversity-max']:
            print("Error: diversity:: expected %0.4f to %0.4f, got %0.4f" % (rp['diversity-min'], rp['diversity-max'], diversity))
            success=0
    elif addrp:
        print("adding param 'result-diversity-min' = %s' to config" % diversity)
        addrpdict['result-diversity-min'] = diversity
        print("adding param 'result-diversity-max' = %s' to config" % diversity)
        addrpdict['result-diversity-max'] = diversity
        success = 0

    if 'genomesize' in rp:
        if genomeSize != rp['genomesize']:
            print("Error: genome size:: expected %i, got %i" % (rp['genomesize'], genomeSize))
            success = 0
    elif addrp:
        print("adding param 'result-genomesize = %s' to config" % genomeSize)
        addrpdict['result-genomesize'] = genomeSize
        success = 0

    if 'kills' in rp:
        if kills != rp['kills']:
            print("Error: number of kills:: expected %i, got %i" % (rp['kills'], kills))
            success = 0
    elif addrp:
        print("adding param 'result-kills = %s' to config" % kills)
        addrpdict['result-kills'] = kills
        success = 0

    if addrp:
        updateResultParams(thisconfig, testname, addrpdict)
        print("\nresult parameters were added\nrun the test again")
        return

    if success == 1:
        print("\nPass")
    else:
        print("\nFail")
    
