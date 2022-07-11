#!/usr/bin/env python3

import sys
from compiler import Procedure, CALL, RETURN, Variable, IF, CONDITION, create_code, compile
import inc


inc.new_unit()
OTHER_TRANSLATION_UNIT = {
    "globals": [
        Variable("some_string", "ptr", "'Hello from the other side!', 0xa, 0")
    ],
    "procedures": []
}
compile(create_code(OTHER_TRANSLATION_UNIT, of="other_unit"))

inc.new_unit()
PROG = {
    "globals": [
    ],
    "procedures": [
        Procedure("naomi_proc",
            [CALL("puts", ["str"]), RETURN()],
            [],
            [Variable("str", "ptr")]
        ),
        Procedure("main",
            [
                CALL("proxy", ["some_string"]),
                RETURN("0")
            ],
            [Variable("msg", "ptr", '"Hello from main, through proxy, back to Naomi!", 10, 0')],
            [Variable("argc", "int32"), Variable("argv", "ptr")]
        )
    ]
}
compile(create_code(PROG), link=True, objs=["build/call_naomi_proc.o", "build/other_unit.o"])