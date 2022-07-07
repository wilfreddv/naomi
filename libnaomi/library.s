%include "constants.inc"

%macro ENTER 1
  push rbp
  mov rbp, rsp
  sub rsp, %1
%endmacro

%macro EXIT 0
  mov rax, SYS_EXIT
  syscall
%endmacro


section .text

global putc
global puts
global println
global u_remainder
global strlen
global exit

extern main
global _start
_start:     ; exit(main(int, char**, char**))
  mov   rdi, [rsp]      ; argc
  lea   rsi, [rsp+8]    ; argv
  lea   rdx, [rsp+(rdi+2)*8] ; envp
  call  main
  mov   rdi, rax    ; use return value as exit value
  EXIT

putc:       ; void putc(char)
  mov   [rsp-8], rdi
  mov   rdx, 1    ; strlen
  lea   rsi, [rsp-8]
  mov   rdi, STDOUT
  mov   rax, SYS_WRITE
  syscall
  ret

puts:       ; void puts(const char*)
  push  rdi
  call  strlen
  pop   rdi
  mov   rdx, rax
  mov   rsi, rdi    ; First argument to the right register
  mov   rdi, STDOUT
  mov   rax, SYS_WRITE
  syscall
  ret

println:      ; void println(const char*)
  call  puts
  mov   rdi, 0xa    ; \n
  call  putc
  ret

u_remainder:    ; uint64 remainder(uint64 dividend, uint64 divisor)
  xor   rdx, rdx
  mov   rax, rdi
  div   rsi
  mov   rax, rdx
  ret

strlen:     ; int strlen(const char*)
  push  rdi ; store rdi for comparison later
  sub   rdi, 1
.L1:
  add   rdi, 1
  cmp   BYTE [rdi], 0
  jne   .L1
  pop   rax
  sub   rdi, rax    ; subtract stored base ptr
  mov   rax, rdi    ; save return value
  ret

exit:   ; void exit(int)
  mov   rax, SYS_EXIT
  syscall