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
        return ""

class ASM(Operator):
    def __init__(self, code):
        self.code = code
    
    def get_asm(self, *_) -> str:
        return self.code

class CALL(Operator):
    def __init__(self, func, args=None):
        self.func = func
        self.args = args if args else []
        
        if not self.func in GLOBAL_FUNCTIONS:
            EXTERN_FUNCTIONS.add(self.func)

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        output = ""
        for reg, arg in zip(CALLER_REGISTERS, self.args):
            if var_table and arg in var_table.keys():
                operand_size = get_size_decl(var_table[arg][0], get_operand_size=True)
                reg = REG_BY_SIZE[var_table[arg][0]][reg]
                output += f"  mov {reg}, {operand_size} [rbp-{var_table[arg][1]}]\n"
            elif arg in GLOBALS.keys():
                operand_size = get_size_decl(GLOBALS[arg], get_operand_size=True)
                reg = REG_BY_SIZE[GLOBALS[arg]][reg]
                output += f"  mov {reg}, {operand_size} [{arg}]\n"
            else:
                output += f"  mov {reg}, {arg}\n"
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
        else:
            output += f"  mov rax, {left}\n"

        if right in var_table:
            output += f"  mov {REG_BY_SIZE[var_table[right][0]]['rdx']}, {get_size_decl(var_table[right][0], get_operand_size=True)} [rbp-{var_table[right][1]}]\n"
        else:
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
            operand_size = get_size_decl(GLOBALS[self.ret_val], get_operand_size=True)
            reg = REG_BY_SIZE[GLOBALS[self.ret_val]][reg]
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
    def __init__(self, dest, left, right):
        self.dest = dest
        self.left = left
        self.right = right

    def get_asm(self, var_table: Mapping[str, Tuple[int, int]]=None) -> str:
        output = f"  mov rax, [rbp-{var_table[self.left][1]}]\n"
        output += f"  mov rdx, [rbp-{var_table[self.right][1]}]\n"
        output += "  add rax, rdx\n"
        output += f"  mov [rbp-{var_table[self.dest][1]}], rax\n"
        return output