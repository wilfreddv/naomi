import sys
from typing import List
import subprocess

from inc import *
from operators import *
from containers import *


DEBUG = False
def printd(msg):

    global DEBUG
    if DEBUG:
        print(msg)


def parse_procedures(procs: List[Procedure]) -> str:
    procedures = ""

    for proc in procs:
        EXTERN_FUNCTIONS.discard(proc.name) # It is global if defined here, not extern
        GLOBAL_FUNCTIONS.add(proc.name)

        procedures += f"section .text\n{proc.name}:\n"

        if not proc.body:
            procedures += f"  ret\n\n"
            continue

        enter = "  push rbp\n  mov rbp, rsp\n"


        var_section = ""
        data = "section .data\n"
        has_data = False
        var_table = {} # name: (size, offset)
        rolling_offset = 0
        if proc.parameters:
            for arg, reg in zip(proc.parameters, CALLER_REGISTERS):
                rolling_offset += arg.size
                var_table[arg.name] = (arg.size, rolling_offset)
                reg = REG_BY_SIZE[arg.size][reg]
                var_section += f"  mov {get_size_decl(arg.size, get_operand_size=True)} [rbp-{rolling_offset}], {reg}\n"
        
        if proc.locals:
            for var in proc.locals:
                rolling_offset += var.size
                var_table[var.name] = (var.size, rolling_offset)
                if var.type == "ptr":
                    data += f".{var.name}:\n  db {var.value}\n"
                    has_data = True
                    var_section += f"  mov QWORD [rbp-{rolling_offset}], .{var.name}\n"
                elif var.value:
                    var_section += f"  mov {get_size_decl(var.size, get_operand_size=True)} [rbp-{rolling_offset}], {var.value}\n"

        enter += f"  sub rsp, {rolling_offset}\n"

        if var_section:
            procedures += enter
            procedures += var_section
        for op in proc.body:
            procedures += op.get_asm(var_table)

        procedures += f"{data}\n" if has_data else "\n"

    return procedures


def parse_globals(variables: List[Variable]) -> str:
    data = "section .data\n"
    bss = "section .bss\n"
    has_data, has_bss = False, False

    for var in variables:
        name = var.name
        value = var.value
        size = var.size
        size_decl = get_size_decl(size, has_value=value is not None)
        GLOBALS[name] = size
        if var.type == "ptr" and value:
            size_decl = "db"
        if value:
            has_data = True
            data += f"{name}:\n  {size_decl} {value}\n"
        else:
            has_bss = True
            bss += f"{name}:\n  {size_decl} 1\n"

    ret = f"{data}\n" if has_data else ""
    ret += f"{bss}\n" if has_bss else ""
    return ret


def create_code(program, of="prog") -> str:
    of += ".s"
    procedures = parse_procedures(program["procedures"])
    globals = parse_globals(program["globals"])
    assert not (GLOBAL_FUNCTIONS & EXTERN_FUNCTIONS), "Cannot have extern and global declaration"

    with open(of, "w") as f:
        f.write("\n".join([f"extern {f}" for f in EXTERN_FUNCTIONS | EXTERNS]) + "\n\n")
        f.write("\n".join([f"global {f}" for f in GLOBAL_FUNCTIONS]) + "\n")
        f.write("\n".join([f"global {f}" for f in GLOBALS.keys()]) + "\n\n")
        f.write(f"{procedures}")
        f.write(f"{globals}")

    return of


def compile(fin: str, link=False, objs: List[str] = None) -> int:
    new_unit()
    base = fin.split('.')[0]
    nasm = f"nasm -o build/{base}.o -gdwarf -felf64 {fin}"

    if objs:
        ld = f"ld -o {base} libnaomi.a {' '.join(objs)} build/{base}.o"
    else:
        ld = f"ld -o {base} libnaomi.a build/{base}.o"

    return subprocess.call(nasm.split()) or \
        link and subprocess.call(ld.split())


if __name__ == '__main__':
    pass
    # if "-d" in sys.argv:
    #     DEBUG = True
    # fout = create_code(PROG)
    # exit(comply(fout))
