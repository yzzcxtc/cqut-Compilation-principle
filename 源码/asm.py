def get_asm(four_formula, variate_na, variate_di):
        r = 0
        w = 0
        program = '''
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
	    LL_r db 0ah,'Input:',0\n'''
        for i in variate_na:
            if "parameter" in variate_di[i].keys():
                continue
            program += "\t\t_" + i + " dw 0\n"
        program += '''
data ends
code segment                  
start:  mov ax,extended       
        mov es,ax             
        mov ax,stack
        mov ss,ax
        mov sp,1024
        mov bp,sp
        mov ax,data
        mov ds,ax\n'''
        for i in range(len(four_formula)):
            print(str(i) + "   " + str(four_formula[i]))
            asm = ""
            op = four_formula[i][0]
            v1 = four_formula[i][1]
            v2 = four_formula[i][2]
            vr = four_formula[i][3]
            if v1 != "":
                if str(v1).isidentifier():
                    if v1[0] == "T":
                        v1 = int(v1[1:]) * 2 - 2
                        v1 = 'ES:[%s]' % v1
                    else:
                        v1 = "_"+v1
            if v2 != "":
                if str(v2).isidentifier():
                    if v2[0] == "T":
                        v2 = int(v2[1:]) * 2 - 2
                        v2 = 'ES:[%s]' % v2
                    else:
                        v2 = "_" + v2
            if vr != "":
                if str(vr).isidentifier():
                    if vr[0] == "T":
                        vr = int(vr[1:]) * 2 - 2
                        vr = 'ES:[%s]' % vr
                    else:
                        vr = "_"+vr
            if op == "+":
                asm += "MOV AX,%s\n\t\tADD AX,%s\n\t\tMOV %s,AX\n" % (v1, v2, vr)
            elif op == "-":
                asm += "MOV AX,%s\n\t\tSUB AX,%s\n\t\tMOV %s,AX\n" % (v1, v2, vr)
            elif op == "*":
                asm += "MOV AX,%s\n\t\tMOV BX,%s\n\t\tMUL BX\n\t\tMOV %s,AX\n" % (v1, v2, vr)
            elif op == "/":
                asm += "MOV AX,%s\n\t\tMOV DX,0\n\t\tMOV BX,%s\n\t\tDIV BX\n\t\tMOV %s,AX\n" % (v1, v2, vr)
            elif op == "%":
                asm += "MOV AX,%s\n\t\tMOV DX,0\n\t\tMOV BX,%s\n\t\tDIV BX\n\t\tMOV %s,DX\n" % (v1, v2, vr)
            elif op == "<":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,%s\n\t\tJB _LT\n\t\tMOV DX,0\n\t\t_LT: MOV %s ,DX\n" % (
                    v1, v2, vr)
            elif op == ">=":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,%s\n\t\tJNB _GE\n\t\tMOV DX,0\n\t\t_GE: MOV %s ,DX\n" % (
                           v1, v2, vr)
            elif op == ">":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,%s\n\t\tJA _GT\n\t\tMOV DX,0\n\t\t_GT: MOV %s ,DX\n" % (
                           v1, v2, vr)
            elif op == "<=":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,%s\n\t\tJNA _LE\n\t\tMOV DX,0\n\t\t_LE: MOV %s ,DX\n" % (
                           v1, v2, vr)
            elif op == "==":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,%s\n\t\tJE _EQ\n\t\tMOV DX,0\n\t\t_EQ: MOV %s ,DX\n" % (
                           v1, v2, vr)
            elif op == "!=":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,%s\n\t\tJNE _NE\n\t\tMOV DX,0\n\t\t_NE: MOV %s ,DX\n" % (
                           v1, v2, vr)
            elif op == "&&":
                asm += "MOV DX,0\n\t\tMOV AX,%s\n\t\tCMP AX,0\n\t\tJE _AND\n\t\tMOV AX,%s\n\t\tCMP AX,0\n\t\tJE _AND\n\t\tMOV DX,1\n\t\t_AND: MOV %s ,DX\n" % (
                           v1, v2, vr)
            elif op == "||":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,0\n\t\tJNE _OR\n\t\tMOV AX,%s\n\t\tCMP AX,0\n\t\tJE _OR\n\t\tMOV DX,0\n\t\t_OR: MOV %s ,DX\n" % (
                           v1, v2, vr)
            elif op == "!":
                asm += "MOV DX,1\n\t\tMOV AX,%s\n\t\tCMP AX,0\n\t\tJE _NOT\n\t\tMOV DX,0\n\t\t_NOT: MOV %s ,DX\n" % (
                           v1, vr)
            elif op == "j":
                asm += "JMP far ptr _%d\n" % vr
            elif op == "jz":
                asm += "MOV AX,%s\n\t\tCMP AX,0\n\t\tJNE _NE\n\t\tJMP far ptr _%d\n\t\t_NE: NOP\n" % (
                           v1, vr)
            elif op == "jnz":
                asm += "MOV AX,%s\n\t\tCMP AX,0\n\t\tJE _EZ\n\t\tJMP far ptr _%d\n\t\t_EZ: NOP\n" % (
                           v1, vr)
            elif op == "para":
                asm += "MOV AX,%s\n\t\tPUSH AX\n" % v1
            elif op == "call":
                if four_formula[i][1] == 'read':
                    r = 1
                elif four_formula[i][1] == "write":
                    w = 1
                asm += "CALL _%s\n\t\tMOV %s,AX\n" % (four_formula[i][1], str(vr))
            elif op == "ret":
                if vr != "":
                    asm += "MOV AX,%s\n\t\tMOV SP,BP\n\t\tPOP BP\n\t\tRET\n" % vr
                else:
                    asm += "MOV SP,BP\n\t\tPOP BP\n\t\tRET\n"
            elif op == "j>":
                asm += "MOV AX,%s\n\t\tCMP AX,%s\n\t\tJG _%d\n" % (v1, v2, vr)
            elif op == "j>=":
                asm += "MOV AX,%s\n\t\tCMP AX,%s\n\t\tJGE _%d\n" % (v1, v2, vr)
            elif op == "j==":
                asm += "MOV AX,%s\n\t\tCMP AX,%s\n\t\tJE _%d\n" % (v1, v2, vr)
            elif op == "j<":
                asm += "MOV AX,%s\n\t\tCMP AX,%s\n\t\tJL _%d\n" % (v1, v2, vr)
            elif op == "j<=":
                asm += "MOV AX,%s\n\t\tCMP AX,%s\n\t\tJLE _%d\n" % (v1, v2, vr)
            elif op == "=":
                asm += "MOV AX,%s\n\t\tMOV %s,AX\n" % (v1, vr)
            elif op == "sys":
                asm += "quit:\tmov ah,4ch\n\t\tint 21h\n"
                program += asm
                continue
            elif str(op).isidentifier() and op != 'main':
                asm += ("_" + op + ":").ljust(8, " ") + "PUSH BP\n\t\tMOV BP,SP\n\t\tSUB SP,2\n"
                program += asm
                continue
            elif op == 'main':
                continue
            program += str("_%d:" % i).ljust(8, " ") + asm
        if r == 1:
            program += '''
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
	        ret'''
        if w == 1:
            program += '''
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
            ret\n'''
        program += "code ends\nend start\n"
        return program