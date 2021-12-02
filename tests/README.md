## Tests

The _tests_ directory contains tools to test _biosim4_. Some tools are scripts, typically written in shell or Python. Other tools (like _rng/random_) need to be compiled.

### simtest.sh

This shell script starts a short simulation and evaluates _biosim4_ console output for both expected output and errors. The scripts uses _configs/biosim4-test-1.ini_ as to configure simulation parameters. From the _tests_ working directory, execute the following from a shell:

`./simtest.sh`

If this script reports any errors, search for this error in this repository's Issues section.

### Random Number Generator

The _biosim4_ random number generator (RNG) allows random numbers to be generated both non-deterministically and non-deterministically. See the _biosim4_ README and _rnd/random.cpp_ for more information.

To run the RNG in isolation it must first be compiled, as follows:

`$ g++ -Wall -Wextra -g -std=c++17 -fpermissive -o random random.cpp`

Execute the resulting binary (_random_) to see command line arguments and their parameters:

```
$ ./random
BioSim4 RNG (standalone)
 Takes two required args: (int)min>=0 (int)max<=INT_MAX
 min, max are the range values of the random number output.
 An optional third arg is (int)seed<=4294967295
 If provided then the RNG will be deterministic.
 ```