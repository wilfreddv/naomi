#!/usr/bin/env python3

import sys
from complier import Procedure, CALL, RETURN, Variable, IF, CONDITION, create_code, comply

PROG = {
    "globals": [
    ],
    "procedures": [
        Procedure("newline",
            [CALL("puts", ["msg"]), RETURN()],
            [Variable("msg", "ptr", "10, 0")]
        ),
        Procedure("main",
            [
                IF(CONDITION("argc", "3", "!="),
                    [CALL("puts", ["msg"]), CALL("newline"), RETURN("1")]
                ),
                RETURN("0")
            ],
            [Variable("msg", "ptr", '"Not 3 arguments...", 0')],
            [Variable("argc", "int32"), Variable("argv", "ptr")]
        )
    ]
}

sys.exit(comply(create_code(PROG)))