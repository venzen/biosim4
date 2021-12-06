
from .pylib import config


def printproc(process)
    print()
    print(process.stdout)
    print()
    print(process.stderr)


def analysis(last_line):
    """ docline
        """
    reslist = str.split(last_line)
    if len(reslist) != 5:
        print("Error: unexpected line length in %s:" % logfile)
        print(last_line)
        exit(1)
    try:
        generation = int(reslist[0])
        survivors = int(reslist[1])
        diversity = float(reslist[2])
        genomeSize = int(reslist[3])
        kills = int(reslist[4])
        success = 0
    except Exception as e:
        print("Exception reading logfile:" % e)

    if generation < 100:
        print("Error: generation number, expected 100, got :",  generation)
        success = 0

    if survivors <= 266 or survivors > 284:
        print("Error: survivors, expected 266 to 284, got ", survivors)
        success = 0

    if diversity < 0.314 or diversity > 0.551:
        print("Error: diversity, expected 0.314 to 0.551, got ", diversity)
        success=0

    if genomeSize != 64:
        print("Error: genome size, expected 64, got ", genomeSize)
        success = 0

    if kills != 0:
        print("Error: number of kills, expected 0, got ", kills)
        success = 0

    if success == 1:
        print("Pass")
    else:
        print("Fail")


###
###   menu

def menu():
    """ Main fn() consisting of conditionals that evoke either   
        local functions or functions imported from the testlib module.
        """

    try:
        prompt = input("menu cmd> ")
        if prompt == "":
            menu()
        else:
            userstr = str.split(prompt)
            print(userstr)

        # Conditionals

        if userstr[0] == "test":
            proc = testlib.runtest(testname, inifile)
            ll = testlib.readlog()
            analysis(ll)



    except:
        pass



if __name__ == "__main__":

    try:
        menu()
    except KeyboardInterrupt:
        print("closing UI...")