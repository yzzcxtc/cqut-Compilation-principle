
assume cs:code,ds:data,ss:stack,es:extended
extended segment              
        db 1024 dup (0)
extended ends
stack segment                 
        db 1024 dup (0)
stack ends
data segment                 
        _buff_p db 256 dup (24h)
        _buff_s db 256 dup (0)
        LL_w db 0ah,'Output:',0
	    LL_r db 0ah,'Input:',0
		_i dw 0
		_N dw 0
		_sum dw 0

data ends
code segment                  
start:  mov ax,extended       
        mov es,ax             
        mov ax,stack
        mov ss,ax
        mov sp,1024
        mov bp,sp
        mov ax,data
        mov ds,ax
_0:     MOV AX,0
		MOV _sum,AX
_1:     CALL _read
		MOV ES:[0],AX
_2:     MOV AX,ES:[0]
		MOV _N,AX
_3:     MOV AX,1
		MOV _i,AX
_4:     MOV AX,_i
		CMP AX,_N
		JLE _9
_5:     JMP far ptr _15
_6:     MOV AX,_i
		ADD AX,1
		MOV ES:[2],AX
_7:     MOV AX,ES:[2]
		MOV _i,AX
_8:     JMP far ptr _4
_9:     MOV AX,_i
		MOV DX,0
		MOV BX,2
		DIV BX
		MOV ES:[4],DX
_10:    MOV AX,ES:[4]
		CMP AX,1
		JE _12
_11:    JMP far ptr _14
_12:    MOV AX,_sum
		ADD AX,_i
		MOV ES:[6],AX
_13:    MOV AX,ES:[6]
		MOV _sum,AX
_14:    JMP far ptr _6
_15:    MOV AX,_sum
		PUSH AX
_16:    CALL _write
		MOV ES:[8],AX
quit:	mov ah,4ch
		int 21h

_read:      push bp
            mov bp,sp
            mov bx,offset LL_r
            call _print
            mov bx,offset _buff_s
            mov di,0
_r_lp_1:	mov ah,1
            int 21h
            cmp al,0dh
            je _r_brk_1
            mov ds:[bx+di],al
            inc di
            jmp short _r_lp_1
_r_brk_1:	mov ah,2
            mov dl,0ah
            int 21h
            mov ax,0
            mov si,0
            mov cx,10
_r_lp_2:	mov dl,ds:[bx+si]
            cmp dl,30h
            jb _r_brk_2
            cmp dl,39h
            ja _r_brk_2
            sub dl,30h
            mov ds:[bx+si],dl
            mul cx
            mov dl,ds:[bx+si]
            mov dh,0
            add ax,dx
	        inc si
	        jmp short _r_lp_2
_r_brk_2:	mov cx,di
	        mov si,0
_r_lp_3:	mov byte ptr ds:[bx+si],0
	        loop _r_lp_3
	        mov sp,bp
	        pop bp
	        ret
_write: 	push bp
            mov bp,sp
            mov bx,offset LL_w
            call _print
            mov ax,ss:[bp+4]
            mov bx,10
            mov cx,0
_w_lp_1:	mov dx,0
            div bx
            push dx
            inc cx
            cmp ax,0
            jne _w_lp_1
            mov di ,offset _buff_p
_w_lp_2:	pop ax
            add ax,30h
            mov ds:[di],al
            inc di
            loop _w_lp_2
            mov dx,offset _buff_p
            mov ah,09h
            int 21h
            mov cx,di
            sub cx,offset _buff_p
            mov di,offset _buff_p
_w_lp_3:	mov al,24h
            mov ds:[di],al
            inc di
            loop _w_lp_3
            mov ax,di
            sub ax,offset _buff_p
            mov sp,bp
            pop bp
            ret 2
_print:    	mov si,0
	        mov di,offset _buff_p
_p_lp_1:	mov al,ds:[bx+si]
            cmp al,0
            je _p_brk_1
            mov ds:[di],al
            inc si
            inc di
            jmp short _p_lp_1
_p_brk_1:	mov dx,offset _buff_p
            mov ah,09h
            int 21h
            mov cx,si
            mov di,offset _buff_p
_p_lp_2:    mov al,24h
            mov ds:[di],al
            inc di
            loop _p_lp_2
            ret
code ends
end start

