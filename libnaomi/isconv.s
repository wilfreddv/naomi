;;
;;  isconv.s
;;  integer-string conversion
;;

section .text

extern puts

global puti
global itos
global stou
global stoi

puti:       ; void vprint(int64)
  push  rbp
  mov   rbp, rsp
  sub   rsp, 32

  mov   rsi, rsp
  push  rsi
  call  itos
  pop   rsi
  mov   rdi, rsi
  call  puts

  leave
  ret   ; vprint

itos:       ; void stos(int64, char[static 21])
  xor   rcx, rcx
  mov   rax, rdi
  test  rax, rax
  jns   .L1
  mov   BYTE [rsi], '-' ; Add sign
  neg   rax
  mov   rdi, rax
  add   rsi, 1
.L1:    ; get length of number in characters
  mov   rbx, 10
.L1A:
  add   rcx, 1
  cqo       ; convert quad to oct (rax to rdx:rax)
  div   rbx
  test  rax, rax
  jnz   .L1A
  mov   rax, rdi
  mov   BYTE [rsi+rcx], 0
.L2:
  cqo
  div   rbx
  add   dl, '0'
  sub   rcx, 1
  mov   BYTE [rsi+rcx], dl
  test  rcx, rcx
  jnz   .L2
  ret   ;; itos

stou:       ; unsigned long int stou(const char*)
  mov   rsi, rdi
  sub   rdi, 1
.L1:        ; seek end of string
  add   rdi, 1
  cmp   BYTE [rdi], 0
  jne   .L1
  xor   r8, r8  ; accumulator
  xor   rcx, rcx; count hundreds (tmp)
.L2:
  sub   rdi, 1
  cmp   rsi, rdi    ; while( beginning < current )
  jg    .END
  movzx rax, BYTE [rdi]     ; tmp=*ptr-'0'
  sub   rax, '0'
  push  rax         ; save digit for later
  mov   rax, 1      ; mult=1
  mov   rdx, rcx    ; x = tmp
  mov   r9, 10
.L3:                ; while( x>=0 )
  cmp   rdx, 0      ; multiply by 10 to get correct magnitude
  jle   .L3END
  push  rdx
  mul   r9          ; mult *= 10
  pop   rdx
  sub   rdx, 1
  jmp   .L3
.L3END:
  mov   r9, rax
  pop   rax         ; get digit back
  mul   r9          ; multiply digit by magnitude
  add   r8, rax     ; add calculated to accumulated
  add   rcx, 1      ; tmp += 1 (increase hundreds count)
  jmp   .L2
.END:
  mov   rax, r8
  ret   ;; stou

stoi:       ; signed long int stoi(const char*)
  cmp   BYTE [rdi], '-'
  je    .SIGN
  call  stou
  jmp  .END
.SIGN:
  add   rdi, 1  ; skip sign
  call  stou
  neg   rax
.END:
  ret   ;; stoi