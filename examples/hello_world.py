from ..compiler import *
from .. import inc

inc.new_unit()
PROG = {
    "globals": [],
    "procedures": [
        Procedure("main",
            [
                CALL("println", ["message"]),
                RETURN("0")
            ],
            [
                Variable("message", "ptr", "'Hello, world!', 0"),
            ],
            [Variable("argc", "int32"), Variable("argv", "ptr")]
        )
    ]
}
compile(create_code(PROG, "hello_world"), link=True)