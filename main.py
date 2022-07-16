#!/usr/bin/env python3

from compiler import Procedure, CALL, RETURN, Variable, IF, CONDITION, ASM, create_code, compile
import inc

inc.new_unit()
PROG = {
    "globals": [
    ],
    "procedures": [
        Procedure("main",
            [
                CALL("println", ["argv*0"]),
                CALL("println", ["msg"]),
                RETURN("0")
            ],
            [Variable("msg", "ptr", '"Hello Naomi!", 0')],
            [Variable("argc", "int32"), Variable("argv", "ptr")]
        )
    ]
}
compile(create_code(PROG), link=True)