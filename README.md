# naomi
Naomi is a project to explore generating assembly, and eventually compilation of IR/source code too.

Naomi is being built in the opposite direction of the flow of data; first, the code generation was done, then an abstraction on top of it, and so on.

## Usage
First, build libnaomi using `./build_library.pl`. Then run `./main.py` to generate and assemble.
For now, there is a lack of any documentation, so you're on your own if you try to figure out how to write programs in it :)

## TODO
* Function call in argument
* Loops
* More operators
* Possible reverse IF-blocks
* Stack usage optimisation
* Variable optimisation