from abc import abstractmethod
from typing import Tuple, List, Mapping

from inc import *


LABEL = ".L", -1
def get_label():
    global LABEL
    LABEL = LABEL[0], LABEL[1]+1
    return f"{LABEL[0]}{LABEL[1]}"


class Operator:
    @abstractmethod
    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        raise NotImplementedError(f"{self.__class__.__name__}.get_asm")

class ASM(Operator):
    def __init__(self, code):
        self.code = code
    
    def get_asm(self, *_) -> str:
        return self.code

class ASSIGN(Operator):
    def __init__(self, var: str, statement):
        self.var = var
        self.statement = statement

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]] = None) -> str:
        output = ""
        cst = ""

        if isinstance(self.statement, list):
            for op in self.statement:
                output += op.get_asm(var_table)
        else:
            cst = self.statement
            if cst in var_table:
                varsz = var_table[cst][0]
                src = f"[rbp-{var_table[cst][1]}]"
            elif cst in GLOBALS:
                varsz = GLOBALS[self.var][0]
                src = f"[{cst}]"
            elif cst in EXTERNS:
                varsz = EXTERNS[self.var]
                src = f"[{cst}]"

            if cst in var_table or cst in GLOBALS or cst in EXTERNS:
                opsz = get_size_decl(varsz, get_operand_size=True)
                reg = REG_BY_SIZE[varsz]['rax']
                output += f"  mov {reg}, {opsz} {src}\n"
                cst = reg

        if self.var in var_table:
            varsz = var_table[self.var][0]
            opsz = get_size_decl(varsz, get_operand_size=True)
            output += f"  mov {opsz} [rbp-{var_table[self.var][1]}], {cst or REG_BY_SIZE[varsz]['rax']}\n"
        elif self.var in GLOBALS:
            varsz = GLOBALS[self.var][0]
            opsz = get_size_decl(varsz, get_operand_size=True)
            output += f"  mov {opsz} [{self.var}], {cst or REG_BY_SIZE[varsz]['rax']}\n"
        elif self.var in EXTERNS:
            varsz = EXTERNS[self.var]
            opsz = get_size_decl(varsz, get_operand_size=True)
            output += f"  mov {opsz} [{self.var}], {cst or REG_BY_SIZE[varsz]['rax']}\n"

        return output

class CALL(Operator):
    def __init__(self, func, args=None):
        self.func = func
        self.args = args if args else []
        
        if not self.func in GLOBAL_FUNCTIONS:
            EXTERN_FUNCTIONS.add(self.func)

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        output = f"  ; CALL {self.func}({','.join(self.args)})\n"
        for reg, arg in zip(CALLER_REGISTERS, self.args):
            arg, *derefs = arg.split("*")
            argsz = 1

            if var_table and arg in var_table.keys():
                argsz = var_table[arg][0]
                operand_size = get_size_decl(argsz, get_operand_size=True)
                reg = REG_BY_SIZE[var_table[arg][0]][reg]
                output += f"  mov {reg}, {operand_size} [rbp-{var_table[arg][1]}]\n"
            elif arg in GLOBALS.keys():
                argsz = GLOBALS[arg][0]
                operand_size = get_size_decl(argsz, get_operand_size=True)
                reg = REG_BY_SIZE[argsz][reg]
                
                if GLOBALS[arg][1] == "ptr":
                    output += f"  mov {reg}, {operand_size} {arg}\n"    
                else:
                    output += f"  mov {reg}, {operand_size} [{arg}]\n"
            elif arg.isidentifier():
                argsz = 8
                EXTERNS.add(arg)
                output += f"  mov {reg}, {arg}\n"
            else:
                # argsz = anyone's guess
                output += f"  mov {reg}, {arg}\n"

            
            for deref in map(int, derefs):
                deref *= argsz
                output += f"  mov {reg}, [{reg}+{deref}] ; deref\n"

        output += f"  call {self.func}\n"
        return output

class CONDITION(Operator):
    def __init__(self, left: str, right: str, operator: str):
        self.left = left
        self.right = right
        self.operator = operator

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        output = ""
        left, right = self.left, self.right
        if left in var_table:
            output += f"  mov {REG_BY_SIZE[var_table[left][0]]['rax']}, {get_size_decl(var_table[left][0], get_operand_size=True)} [rbp-{var_table[left][1]}]\n"
        else: # Either constant or identifier
            output += f"  mov rax, {left}\n"
        if right in var_table:
            output += f"  mov {REG_BY_SIZE[var_table[right][0]]['rdx']}, {get_size_decl(var_table[right][0], get_operand_size=True)} [rbp-{var_table[right][1]}]\n"
        else: # Either constant or identifier
            output += f"  mov rdx, {right}\n"
        
        output += "  cmp rax, rdx\n"

        return output

class IF(Operator):
    def __init__(self, condition: CONDITION, body: List[Operator]):
        self.condition = condition
        self.body = body

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        output = self.condition.get_asm(var_table)
        
        label = get_label()
        jump = {"==": "jne", "!=": "je", ">": "jle", ">=": "jl", "<": "jge", "<=": "jg"}[self.condition.operator]
        output += f"  {jump} {label}\n"

        for statement in self.body:
            output += statement.get_asm(var_table)

        output += f"{label}:\n"
        return output

class WHILE(Operator):
    pass


class RETURN(Operator):
    def __init__(self, ret_val=None):
        self.ret_val = ret_val
    
    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        if not self.ret_val:
            return "  leave\n  ret\n"

        if var_table and self.ret_val in var_table.keys():
            operand_size = get_size_decl(var_table[self.ret_val][0], get_operand_size=True)
            reg = REG_BY_SIZE[var_table[self.ret_val][0]]["rax"]
            output = f"  mov {reg}, {operand_size} [rbp-{var_table[self.ret_val][1]}]\n"
        elif self.ret_val in GLOBALS.keys():
            operand_size = get_size_decl(GLOBALS[self.ret_val][0], get_operand_size=True)
            reg = REG_BY_SIZE[GLOBALS[self.ret_val][0]][reg]
            output += f"  mov {reg}, {operand_size} [{self.ret_val}]\n"
        elif self.ret_val:
            output = f"  mov rax, {self.ret_val}\n"
        
        if var_table:
            output += "  leave\n"

        output += "  ret\n"
        return output

class SUB(Operator):
    def __init__(self, dest, left, right):
        self.dest = dest
        self.left = left
        self.right = right

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        output = f"  mov rax, [rbp-{var_table[self.left][1]}]\n"
        output += f"  mov rdx, [rbp-{var_table[self.right][1]}]\n"
        output += "  sub rax, rdx\n"
        output += f"  mov [rbp-{var_table[self.dest][1]}], rax\n"
        return output


class ADD(Operator):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        output = ""

        if self.left in var_table:
            varsz = var_table[self.left][0]
            opsz = get_size_decl(varsz, get_operand_size=True)
            reg = REG_BY_SIZE[varsz]['rax']
            offset = var_table[self.left][1]
            output += f"  mov {reg}, {opsz} [rbp-{offset}]\n"
            dest = f"  mov [rbp-{offset}], {opsz} {reg}\n"
        elif self.left in GLOBALS:
            varsz = GLOBALS[self.left][0]
            opsz = get_size_decl(varsz, get_operand_size=True)
            reg = REG_BY_SIZE[varsz]['rax']
            output += f"  mov {reg}, {opsz} [{self.left}]\n"
            dest = f"  mov [{self.left}], {opsz} {reg}\n"
        elif self.left in EXTERNS:
            varsz = EXTERNS[self.left]
            opsz = get_size_decl(varsz, get_operand_size=True)
            reg = REG_BY_SIZE[varsz]['rax']
            output += f"  mov {reg}, {opsz} [{self.left}]\n"
            dest = f"  mov [{self.left}], {opsz} {reg}\n"
        
        if self.right in var_table:
            varsz = var_table[self.left][0]
            opsz = get_size_decl(varsz, get_operand_size=True)
            output += f"  mov {REG_BY_SIZE[varsz]['rbx']}, {opsz} [rbp-{var_table[self.right][1]}]\n"
        elif self.left in GLOBALS:
            varsz = GLOBALS[self.right][0]
            opsz = get_size_decl(varsz, get_operand_size=True)
            output += f"  mov {REG_BY_SIZE[varsz]['rbx']}, {opsz} [{self.left}]\n"
        elif self.left in EXTERNS:
            varsz = EXTERNS[self.right]
            opsz = get_size_decl(varsz, get_operand_size=True)
            output += f"  mov {REG_BY_SIZE[varsz]['rbx']}, {opsz} [{self.left}]\n"

        if self.right == "1":
            output += f"  inc {reg}\n"
        else:
            output += f"  add {reg}, {REG_BY_SIZE[varsz]['rbx']}\n"

        output += dest

        return output

class SUBTRACT(Operator):
    pass