
from time import sleep, ctime
from pathlib import Path
import subprocess


def runtest(testname, inifile):
# launch biosim4

    shellcmd = "./bin/Release/biosim4 %s" % inifile
    process = subprocess.run(shellcmd, cwd='../', shell=True, capture_output=True, text=True, check=True)
    
    return process
    

def readlog():
    # analysis
    path = Path(__file__).parent.joinpath('logs/epoch-log.txt')
    with path.open() as log:
        for line in log:
            pass
        #last_line = line

    return line



