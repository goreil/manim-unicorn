.intel_syntax noprefix
main:
	call   ret1
	mov    rdi,rax
	call   ret2
	mov    rsi,rax
	cmp    rdi,rsi
	jne    _end
	call   win
ret1:
 	mov    rax,10
 	ret    
ret2:
 	mov    rax,30
 	ret    
win:
