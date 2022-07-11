#include "std.h"


void br() { putc('\n'); }

int main(int argc, char** argv, char** envp) {
    puti(123);
    br();
    puti(-123);
    br();

    puts("Number of arguments: ");
    puti(argc);
    br();

    if( argc < 2 ) {
        puts("Too few arguments\n");
        return 1;
    }

    println(argv[1]);

    puti(stoi(argv[1]));
    br();

    int i;
    for(i=0; envp[i]; i++);
    puts("envp** has ");
    puti(i);
    println(" entries");

    return 0;
}