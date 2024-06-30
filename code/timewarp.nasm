ret1:
 	mov    eax,0x1
 	ret    
ret0:
 	mov    eax,0x0
 	ret    
main:
	[...]
	call   ret1
	mov    edi,eax
	call   ret0
	mov    esi,eax
	cmp    edi,esi
	jne    _end
	lea    rax,[rip+you_win]
	mov    rdi,rax
	call   puts
_end:
