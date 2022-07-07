TYPES = {
    "char":     1,
    "u_char":   1,
    "int16":    2,
    "u_int16":  2,
    "int32":    4,
    "u_int32":  4,
    "int64":    8,
    "u_int64":  8,
    "ptr":      8
}

def get_size_decl(size, has_value=False, get_operand_size=False):
    if get_operand_size:
        return {
            1: "BYTE",
            2: "WORD",
            4: "DWORD",
            8: "QWORD",
        }[size]
    if has_value:
        return {
            1: "db",
            2: "dw",
            4: "dd",
            8: "dq",
        }[size]
    else:
        return {
            1: "resb",
            2: "resw",
            4: "resd",
            8: "resq",
        }[size]


CALLER_REGISTERS = "rdi", "rsi", "rdx", "rcx", "r8", "r9"

# REG_BY_SIZE[size][reg]
REG_BY_SIZE = {
        1: {"rax": "al", "rcx": "cl", "rdx": "dl", "rbx": "bl", "rsi": "sil", "rdi": "dil", "r8": "r8b", "r9": "r9b", "r10": "r10b", "r11": "r11b"},
        2: {"rax": "ax", "rcx": "cx", "rdx": "dx", "rbx": "bx", "rsi": "si", "rdi": "di", "r8": "r8w", "r9": "r9w", "r10": "r10w", "r11": "r11w"},
        4: {"rax": "eax", "rcx": "ecx", "rdx": "edx", "rbx": "ebx", "rsi": "esi", "rdi": "edi", "r8": "r8d", "r9": "r9d", "r10": "r10d", "r11": "r11d"},
        8: {"rax": "rax", "rcx": "rcx", "rdx": "rdx", "rbx": "rbx", "rsi": "rsi", "rdi": "rdi", "r8": "r8", "r9": "r9", "r10": "r10", "r11": "r11"}
}


EXTERN_FUNCTIONS = set()
GLOBAL_FUNCTIONS = set()
GLOBALS = {}