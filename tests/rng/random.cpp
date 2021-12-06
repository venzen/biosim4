// This code is copied from biosim4.
// https://github.com/davidrmiller/biosim4
//
// MIT License
// Copyright (c) 2021 David R. Miller
//
// This modification allows compilation of a standalone RNG.
// src/random.cpp (source file notes retained)

std::string VERSION = "2.112.02";

// This file provides a random number generator (RNG) for the main thread
// and child threads. There is a global RNG instance named randomUint which
// can be duplicated so that each thread gets a private copy. The global
// RNG must be initialized after program startup by calling its initialize()
// member function, typically at the top of simulator() in simulator.cpp
// after the parameters have been read. The parameters named "deterministic"
// and "RNGSeed" determine whether to initialize the RNG with a
// user-defined deterministic seed or with a random seed.

//#include <cassert>
//#include <cmath>
#include <random>
//#include <chrono>
//#include <climits>
//#include <ostream>
#include <iostream>
#include <sstream>
//#include <cmath>
//#include <bitset>
//#include <stdlib.h>
//#include <string>
#include "random.h"


namespace BS {


RandomUintGenerator::RandomUintGenerator()
    : initialized(false)
{
}


// If parameter p.deterministic is true, we'll initialize the RNG with
// the seed specified in parameter p.RNGSeed, otherwise we'll initialize
// the RNG with a random seed. This initializes both the Marsaglia and
// the Jenkins algorithms. The member function operator() determines
// which algorithm is actually used.
void RandomUintGenerator::initialize(bool deterministic, uint RNGSeed)
{
    if (deterministic) {
        std::cout << "deterministic= " << deterministic << std::endl;
        std::cout << "Seed= " << RNGSeed << std::endl;
        // Initialize Marsaglia. Overflow wrap-around is ok. We just want
        // the four parameters to be unrelated:
        rngx = RNGSeed + 123456789;
        rngy = RNGSeed + 362436000;
        rngz = RNGSeed + 521288629;
        rngc = RNGSeed + 7654321;

        // Initialize Jenkins:
        a = 0xf1ea5eed;
        b = c = d = RNGSeed;
    } else {
        // Non-deterministic
        std::cout << "deterministic= " << deterministic << std::endl;
        std::cout << "Seed= " << RNGSeed << std::endl;
        // Get a random seed from the built-in generator
        std::mt19937 generator(time(0));  // mt19937 is a standard mersenne_twister_engine

        // Initialize Marsaglia, but don't let any of the values be zero:
        do { rngx = generator(); } while (rngx == 0);
        do { rngy = generator(); } while (rngy == 0);
        do { rngz = generator(); } while (rngz == 0);
        do { rngc = generator(); } while (rngc == 0);

        // Initialize Jenkins, but don't let any of the values be zero:
        a = 0xf1ea5eed;
        do { b = c = d = generator(); } while (b == 0);
    }

    initialized = true; // for debugging, remember that we initialized the RNG
}


// This returns a random 32-bit integer. Neither the Marsaglia nor the Jenkins
// algorithms are of cryptographic quality, but we don't need that. We just need
// randomness of shotgun quality. The Jenkins algorithm is the fastest.
// The Marsaglia algorithm is from http://www0.cs.ucl.ac.uk/staff/d.jones/GoodPracticeRNG.pdf
// where it is attributed to G. Marsaglia.
//
uint32_t RandomUintGenerator::operator()()
{
    if (false) {
        // Marsaglia algorithm
        uint64_t t, a = 698769069ULL;
        rngx = 69069 * rngx + 12345;
        rngy ^= (rngy << 13);
        rngy ^= (rngy >> 17);
        rngy ^= (rngy << 5); /* y must never be set to zero! */
        t = a * rngz + rngc;
        rngc = (t >> 32);/* Also avoid setting z=c=0! */
        return rngx + rngy + (rngz = t);
    } else {
        // Jenkins algorithm
        #define rot32(x,k) (((x)<<(k))|((x)>>(32-(k))))
        uint32_t e = a - rot32(b, 27);
        a = b ^ rot32(c, 17);
        b = c + d;
        c = d + e;
        d = e + a;
        return d;
    }
}


// Returns an unsigned integer between min and max, inclusive.
// Sure, there's a bias when using modulus operator where (max - min) is not
// a power of two, but we don't care if we generate one value a little more
// often than another. Our randomness does not have to be high quality.
// We do care about speed, because this will get called inside deeply nested
// inner loops.
//
unsigned RandomUintGenerator::operator()(unsigned min, unsigned max)
{
    assert(max >= min);
    return ((*this)() % (max - min + 1)) + min;
}


// This is the globally-accessible random number generator. Threads can
// be given their own private copies of this. This object needs to be
// initialized once before its first use by calling randomUint.initialize().
RandomUintGenerator randomUint;

} // end namespace BS

// venzen:
// Functions to sanity-check command line arguments and
// display usage message
static void show_usage(std::string name)
{
    std::string text = 
    "Usage: " << name << " MIN MAX [OPTION...]\n"
    "BioSim4 random number generator\n"
    "Example: " << name << " 1 1000 -s 1234567\n";
    text +=
R"(
MIN and MAX are the range values of the random number output

    MIN     an integer between -2147483647 and 2147483647
    MAX     an integer > MIN and <= 2147483647

Options:

    -h, --help      display this help message and exit
    -v, --version   output version information and exit
    -s, --seed      provide a uint between 0 and 4294967295
                     if provided, this option prompts the RNG
                     to generate random numbers deterministically
    -r, --repeat    provide an integer >= 1 to repeat generation
    -w, --warm      this option takes no arg and warms the RNG
                     before generating user output

Report bugs to: https://github.com/davidrmiller/biosim4/issues
)";
        std::cerr << text << std::endl;
        //return 0;
}

bool checkIfUint(const std::string &s)
{
    return s.find_first_not_of("0123456789") == std::string::npos;
}

bool checkIfInt(const std::string &s)
{
    //return s.find_first_not_of("-0123456789") == std::string::npos;
    std::istringstream iss(s);
    int i;
    iss >> std::noskipws >> i; // noskipws considers leading whitespace invalid
    // Check the entire string was consumed and if either failbit or badbit is set
    return iss.eof() && !iss.fail();
}

// As suggested in the doc __ the first 4 * 256 random numbers
// should be discarded to warm the RNG instance.
void warmRNG (int min, int max)
{
    // display the first random number for comparison
    std::cout << "warming: " << std::endl;
    auto thisrnd = BS::randomUint(min, max);
    std::cout << " initial random number= " << thisrnd << std::endl;
    for (int i=0; i<4 * 256; ++i) {
        auto thisrnd = BS::randomUint(min, max);
        //std::cout << i << " RN= " << thisrnd << std::endl;
    }
}

// This RNG is adequate for the requirements of simulation,
// but it is not considered cryptographically secure.
// Regardless, and for the purpose of illustration, here
// are 3 methods of producing a Bitcoin private key.
void bitcoinPK (bool det, uint Seed)
{
    #include <bitset>
    #include <cmath>
    long nmax = 1.1578 * pow(10, 77);
    std::string binstr = "";
    int intnum = 0;
    
    BS::randomUint.initialize(det, Seed);
    std::cout << "initialized RNG" << std::endl;
    warmRNG(0, 1);
    while (intnum <= nmax - 1) {
        std::cout << "int too small: " << intnum << std::endl;
        for (int i = 0; i < 256; ++i) {
            binstr += BS::randomUint(0, 1);
        }
        intnum = stoi(binstr, 0, 2);
    }
    std::cout << "256 random binary bits: " << binstr << std::endl;
    std::cout << "  int= " << intnum << std::endl;
    std::bitset<8> set(binstr);  
    std::cout << "  hex= " << std::hex << set.to_ulong() << std::endl;
    //std::cout << "btcPK= " << std::hex.substr(2) << std::endl;
}

static int rndbinbits () 
{
    std::string binstr = "";
    for (int i = 0; i < 256; ++i) {
        binstr += BS::randomUint(0, 1);
    }
    std::cout << "256 random binary bits: " << binstr << std::endl;
    return stoi(binstr, 0, 2);
}


int main(int argc, char **argv)
{
    if (argc < 3) {
        show_usage(argv[0]);
        return 1;
    }
    int min;
    int max;
    uint Seed = 0;
    bool det = false;
    int n = 1;
    bool warm = false;
    bool showusage = false;
    std::string errormsg = "";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "-h") || (arg == "--help")) {
            show_usage(argv[0]);
            return 0;
        } else if ((arg == "-v") || (arg == "--version")) {
            std::cout << VERSION << std::endl;
            return 0;
        } else if ((arg == "-w") || (arg == "--warm")) {
            warm = true;
        } else if ((arg == "-b") || (arg == "--btcpk")) {
            bitcoinPK(det, Seed);
            return 0;
        }

        if ((i == 1) or (i == 2)) {
            if (checkIfInt(argv[i])) {
                long argmm = strtol(argv[i], NULL, 10);
                if (argmm >= INT_MIN and argmm <= INT_MAX) {
                    if (i == 1) {
                        min = argmm;
                        std::cout << "min= " << min << std::endl;
                    } else {
                        if (argmm > min) {
                            max = argmm;
                            std::cout << "max= " << max << std::endl;
                        } else {
                            std::cout << "max value " << argmm << " must be greater than min= " << min << std::endl;
                            errormsg = "MAX <= MIN";
                            break;
                        }
                    }
                } else {
                    errormsg << "arg " << i << " out of range";
                    break;
                }
            } else {
                errormsg << "arg " << i << " must be an integer";
                break;
            }
            if (not errormsg.empty()) {
                std::cerr << errormsg << std::endl;
                show_usage(argv[0]);
                return 1;
            }
        if ((arg == "-s") || (arg == "--seed")) {
            int ii = i + 1;
            if (checkIfUint(argv[ii])) {
                long arg = strtol(argv[ii], NULL, 10);
                if (arg >= 0 and arg <= 4294967295) {
                    std::cout << "seed= " << arg << std::endl;
                    Seed = arg;
                    det = true;
                } else {
                    std::cout << "Warning: seed value " << argv[ii] << " > 4294967295 and will produce an error" << std::endl;
                    //return 1;
                }
            } else {
                std::cout << "seed value " << argv[ii] << " should be an integer 0...4294967295" << std::endl;
                errormsg = "SEED value error";
                show_usage(argv[0]);
                return 1;
                //return 1;
            }
        }
        if ((arg == "-s") || (arg == "--seed")) {
            int ii = i + 1;
            if (checkIfUint(argv[ii])) {
                int arg = strtol(argv[ii], NULL, 10);
                if (arg >= 1) {
                    n = arg;
                } else {
                    errormsg = "MULT < 1";
                    std::cerr << errormsg << std::endl;
                }
            } else {
                errormsg = "MULT should be an integer ";
                std::cout << errormsg << argv[ii] << std::endl;
                showusage = true;
            }
        }
    }

/*     if (showusage) {
        if (not errormsg.empty()) {
            std::cout << "\nERROR: " << errormsg << std::endl;
            usage();
            return 1;
        } else {
            usage();
            return 0;
        }
    } */

    // Initialize the random number generator
    BS::randomUint.initialize(det, Seed);
    std::cout << "initialized RNG" << std::endl;
    if (warm) {
        warmRNG(min, max);
    }
    for (int i=0; i<n; ++i) {
        auto thisrnd = BS::randomUint(min, max);
        std::cout << i << " RN= " << thisrnd << std::endl;
    }

    return 0;
}
