#!/usr/bin/env python3

from compiler import *
import inc

inc.new_unit()
PROG = {
    "globals": [],
    "procedures": [
        Procedure("fib",
            [
                IF(CONDITION("i", "1", "<="),
                    [RETURN("i")]
                ),
                ASM("  push rbx\n"),
                SUB("i", "i", "1"),
                CALL("fib", ["i"]),
                ASM("  mov rbx, rax\n"),
                SUB("i", "i", "1"),
                CALL("fib", ["i"]),
                ASM("  add rax, rbx\n"),
                ASM("  pop rbx\n"),
                RETURN()
            ],
            [],
            [Variable("i", "int64")]
        ),
        Procedure("main",
            [
                IF(CONDITION("argc", "2", "!="),
                    [CALL("println", ["ERR_MSG"]), RETURN("1")]
                ),
                CALL("stoi", ["argv*1"]),
                ASM("  mov rdi, rax\n"),
                CALL("fib"),
                ASM("  mov rdi, rax\n"),
                CALL("puti"),
                CALL("putc", ["10"]),
                RETURN("0")
            ],
            [
                Variable("ERR_MSG", "ptr", "'Program takes 1 argument...', 0"),
            ],
            [Variable("argc", "int32"), Variable("argv", "ptr")]
        )
    ]
}
compile(create_code(PROG), link=True)