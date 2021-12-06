## Tests

The _tests_ directory contains tools to test _biosim4_. Some tools are scripts, typically written in shell or Python. Other tools (like _rng/random_) need to be compiled.

### simtest.sh

This shell script starts a short simulation and evaluates _biosim4_ console output for both expected output and errors. The scripts uses _configs/biosim4-test-1.ini_ to configure simulation parameters. From the _tests_ working directory execute the following from a shell:

`./simtest.sh`

If this script reports any errors, search for this error in Issues.

### Random Number Generator

Written in C++, the _biosim4_ random number generator (RNG) allows random numbers to be generated both non-deterministically and deterministically depending on whether or not a seed is provided. See the _biosim4_ README and _rnd/random.cpp_ for more information about the RNG implementation.

To run the RNG in isolation it must first be compiled.

`$ g++ -Wall -Wextra -g -std=c++17 -fpermissive -o random random.cpp`

Execute the resulting binary (_random_) to see usage instructions:

```
$ ./random
Usage: random MIN MAX [SEED] [MULT]
BioSim4 random number generator
Example: random 1 1000 1234567 3

Arguments:
    MIN     an integer between -2147483647 and 2147483647
    MAX     an integer > MIN and <= 2147483647
    SEED    (optional) a uint between 0 and 4294967295
    MULT    (optional) an integer >= 1 to repeat generation

 MIN and MAX are the range values of the random number output.
 The optional third argument SEED, if provided, prompts the RNG to generate random numbers deterministically. Without SEED the RNG output is non-determinstic (default).
 The optional fourth argument MULT (multiplier) prompts repeat
 RNG using the same parameters.

 Report bugs to: https://github.com/davidrmiller/biosim4/issues 
 Version 2.112.02
 ```

 > __Note:__ In C++ the value of INT_MIN = -2147483647 - 1
. INT_MAX = 2147483647. The value of UINT_MAX = 4294967295 (0xffffffff).