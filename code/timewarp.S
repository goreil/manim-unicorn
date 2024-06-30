.global _start
.intel_syntax noprefix
_start:
    call main
    // Exit
    mov rax, 60
    syscall
puts:
    mov rax, 1
    mov rsi, rdi
    mov rdi, 1
    mov rdx, 5
    syscall
    ret
ret1:
 	mov    rax,0x1
 	ret    
ret0:
 	mov    rax,0x0
 	ret    
main:
	call   ret1
	mov    rdi,rax
	call   ret0
	mov    rsi,rax
	cmp    rdi,rsi
	jne    _end
	lea    rax,[rip+_win]
	mov    rdi,rax
	call   puts
_end:
    ret
_win:
    .string "WIN!\n"
