venumprint:       ; void venumprint(int64)
  push  rbp
  mov   rbp, rsp
  sub   rsp, 64

  xor   r11, r11
  mov   rsi, rbp
  xor   rcx, rcx    ; counter
  mov   rax, rdi
  test  rax, rax
  jns   .L1
  add   r11, 1
  neg   rax
  mov   rdi, rax
.L1:    ; get length of number in characters
  mov   rbx, 10
.L1A:
  add   rcx, 1
  cqo       ; convert quad to oct (rax to rdx:rax)
  div   rbx
  test  rax, rax
  jnz   .L1A
  mov   r11, rcx
  mov   rax, rdi

  mov   r12, rcx
  neg   rcx
  test  r11, r11
  jnz   .L2
  sub   rcx, 1
  add   r12, 1
  mov   BYTE [rbp+rcx], '-' ; Add sign
.L2:
  cqo
  div   rbx
  add   dl, '0'
  add   rcx, 1
  mov   BYTE [rbp+rcx], dl
  test  rcx, rcx
  jnz   .L2

  mov   rdx, r12    ; length
  mov   rsi, rbp    ; string
  add   rsi, r12
  mov   rdi, 1      ; STDOUT
  mov   rax, 60     ; SYS_WRITE
  syscall
  
  leave
  ret   ;; venumprint