// random.cpp
// Provides a random number generator for the main thread
// and child threads

#include <cassert>
#include <cmath>
#include <random>
#include <chrono>
#include <climits>
#include <ostream>
#include <iostream>
#include "random.h"
//#include "omp.h"
//#include <pybind11/pybind11.h>

//namespace py = pybind11;
namespace BS {

/* public:
    RandomUintGenerator(bool deterministic = false);
    RandomUintGenerator& operator=(const RandomUintGenerator &rhs) = default;
    void randomize();
    uint32_t operator()();
    unsigned operator()(unsigned min, unsigned max); */

// Default is determinstic
RandomUintGenerator::RandomUintGenerator(bool deterministic)
{
    //std::cout << "deterministic " << deterministic << std::endl;
    if (deterministic) {
        // for Marsaglia
        rngx = 123456789;
        rngy = 362436000;
        rngz = 521288629;
        rngc = 7654321;

        // for Jenkins:
        a = 0xf1ea5eed, b = c = d = 123456789;
    } else {
        randomize();
    }
}


void RandomUintGenerator::randomize()
{
    std::mt19937 generator(time(0));  // mt19937 is a standard mersenne_twister_engine

    // for Marsaglia
    do { rngx = generator(); } while (rngx == 0);
    do { rngy = generator(); } while (rngy == 0);
    do { rngz = generator(); } while (rngz == 0);
    do { rngc = generator(); } while (rngc == 0);

    // for Jenkins:
    a = 0xf1ea5eed, b = c = d = generator();
}


// This algorithm is from http://www0.cs.ucl.ac.uk/staff/d.jones/GoodPracticeRNG.pdf
// where it is attributed to G. Marsaglia.
//
uint32_t RandomUintGenerator::operator()()
{
    if (false) {
        // Marsaglia
        uint64_t t, a = 698769069ULL;
        rngx = 69069 * rngx + 12345;
        rngy ^= (rngy << 13);
        rngy ^= (rngy >> 17);
        rngy ^= (rngy << 5); /* y must never be set to zero! */
        t = a * rngz + rngc;
        rngc = (t >> 32);/* Also avoid setting z=c=0! */
        
        uint32_t outval = rngx + rngy + (rngz = t);
        std::cout << "rng " << outval << std::endl;
        return rngx + rngy + (rngz = t);
    } else {
        // Jenkins
        #define rot32(x,k) (((x)<<(k))|((x)>>(32-(k))))
        uint32_t e = a - rot32(b, 27);
        a = b ^ rot32(c, 17);
        b = c + d;
        c = d + e;
        d = e + a;
        
        std::cout << "Jenkins rng " << d << std::endl;
        return d;
    }
}


// Sure, there's a bias when using modulus operator where (max - min) is not
// a power of two, but we don't care if we generate one value a little more
// often than another. Our randomness does not have to be any better quality
// than the randomness of a shotgun. We do care about speed, because this will
// get called inside deeply nested inner loops.
//
unsigned RandomUintGenerator::operator()(unsigned min, unsigned max)
{
    assert(max >= min);
    std::cout << "min " << min << " max " << max << std::endl;
    return ((*this)() % (max - min + 1)) + min;
}


// The globally accessible random number generator. Threads can be
// given their own private copies of this.
extern RandomUintGenerator randomUint;

} // end namespace BS

bool getBoolVal(const std::string &s)
{
    if (s == "true" || s == "1")
        return true;
    else if (s == "false" || s == "0")
        return false;
    else
        return false;
}

int main(int argc, char **argv)
{
    bool thisbool = getBoolVal(argv[1]);
    std::cout << "thisbool " << thisbool << std::endl;
    std::cout << "argc " << (int)argc << std::endl;
    std::cout << "argv[1] " << argv[1] << std::endl;
    //BS::unitTestBasicTypes(); // called only for unit testing of basic types

    // Start the simulator with optional config filename (default "biosim4.ini").
    // See simulator.cpp and simulator.h.
    //BS::RandomUintGenerator();
    auto minX = BS::randomUint(1,1);
    std::cout << "RNG " << minX << std::endl;

    return 0;
}


/* PYBIND11_MODULE(random, m) {
    m.doc() = "pybind11 random plugin"; // optional module docstring

    m.def("randomUint", &randomUint, "RNG function");
} */

/* PYBIND11_MODULE(randomuint, m) {
    py::class_<RandomUintGenerator>(m, "RNG")
        .def(py::init<bool>)
        .def(py::self)
    //py::class_<Dog, Animal>(m, "Dog")
    //    .def(py::init<>());

    m.def("call_rng", &randomUint);
} */
/* public:
    RandomUintGenerator(bool deterministic = false);
    RandomUintGenerator& operator=(const RandomUintGenerator &rhs) = default;
    void randomize();
    uint32_t operator()();
    unsigned operator()(unsigned min, unsigned max); */