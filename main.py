#!/usr/bin/env python3

from compiler import *
import inc

inc.new_unit()
PROG = {
    "globals": [
        Variable("plus", "ptr", "' + ', 0"),
        Variable("eqsign", "ptr", "' = ', 0")
    ],
    "procedures": [
        Procedure("main",
            [
                ASSIGN("left", [CALL("stoi", ["argv*1"])]),
                ASSIGN("right", [CALL("stoi", ["argv*2"])]),
                ASSIGN("total", "left"),
                ADD("total", "right"),
                CALL("puti", ["left"]),
                CALL("puts", ["plus"]),
                CALL("puti", ["right"]),
                CALL("puts", ["eqsign"]),
                CALL("puti", ["total"]),
                CALL("putc", ["10"]),
                RETURN("0")
            ],
            [
                Variable("left", "int64"),
                Variable("right", "int64"),
                Variable("total", "int64"),
            ],
            [Variable("argc", "int32"), Variable("argv", "ptr")]
        )
    ]
}
compile(create_code(PROG), link=True)