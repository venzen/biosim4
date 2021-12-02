// This code is copied from biosim4.
// https://github.com/davidrmiller/biosim4
//
// MIT License
// Copyright (c) 2021 David R. Miller
//
// This modification allows compilation of a standalone RNG.
// src/random.cpp (source file notes retained)

// This file provides a random number generator (RNG) for the main thread
// and child threads. There is a global RNG instance named randomUint which
// can be duplicated so that each thread gets a private copy. The global
// RNG must be initialized after program startup by calling its initialize()
// member function, typically at the top of simulator() in simulator.cpp
// after the parameters have been read. The parameters named "deterministic"
// and "RNGSeed" determine whether to initialize the RNG with a
// user-defined deterministic seed or with a random seed.

#include <cassert>
#include <cmath>
#include <random>
#include <chrono>
#include <climits>
#include <ostream>
#include <iostream>
#include <sstream>
#include <stdlib.h>
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
// Functions to sanity-check command line arguments
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


int main(int argc, char **argv)
{
    bool det = false;
    uint Seed = 0;
    int min;
    int max;

    if (argc >= 3 && argc <= 4) {
        if (argc == 4) {
            if (checkIfUint(argv[3])) {
                long arg = strtol(argv[3], NULL, 10);
                if (arg <= 4294967295) {
                    std::cout << "seed= " << arg << std::endl;
                    Seed = arg;
                    det = true;
                } else {
                    std::cout << "seed value " << argv[3] << " > 4294967295 is invalid" << std::endl;
                    return 1;
                }
            } else {
                std::cout << "seed value " << argv[3] << " should be an integer 0...4294967295" << std::endl;
                return 1;
            }
        }
        if (argc >= 3) {
            if (checkIfInt(argv[1])) {
                long arg = strtol(argv[1], NULL, 10);
                if (arg >= 0) {
                    std::cout << "min= " << arg << std::endl;
                    min = arg;
                } else {
                    std::cout << "min value " << argv[1] << " cannot be negative" << std::endl;
                    return 1;
                }
            } else {
                std::cout << "min value " << argv[1] << " should be an integer" << std::endl;
                return 1;
            }
            if (checkIfInt(argv[2])) {
                long arg = strtol(argv[2], NULL, 10);
                if (arg > min) {
                    std::cout << "max= " << arg << std::endl;
                    max = arg;
                } else {
                    std::cout << "max value " << arg << " should be greater than min= " << min << std::endl;
                    return 1;
                }
            } else {
                std::cout << "max value " << argv[2] << " should be an integer" << std::endl;
                return 1;
            }
        }
    } else if (argc == 1) {
        std::cout << "BioSim4 RNG (standalone)" << std::endl;
        std::cout << " takes two req. args: (int)min>=0 (int)max<=INT_MAX" << std::endl;
        std::cout << " these are the range values of the random number output" << std::endl;
        std::cout << " an optional third arg is a (int)seed<=4294967295" << std::endl;
        std::cout << " if provided then the RNG output will be deterministic.\n" << std::endl;
        return 0;
    } else {
        std::cout << " Invalid number of args: " << argc << "\n" << std::endl;
        return 1;
    }

    // Initialize the random number generator
    BS::randomUint.initialize(det, Seed);
    std::cout << "initialized RNG" << std::endl;
    auto thisrnd = BS::randomUint(min, max);
    std::cout << "RN= " << thisrnd << std::endl;

    return 0;
}
