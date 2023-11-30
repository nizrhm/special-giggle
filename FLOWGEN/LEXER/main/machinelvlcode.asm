section .data
    output_fmt db "%d", 10 ; Format string for printing integers

section .bss
    a resd 1 ; Integer variable a
    b resd 1 ; Integer variable b
    c resd 1 ; Integer variable c
    d resq 1 ; Real variable d

section .text
    global _start

_start:
    ; Initialize variables
    mov dword [a], 1  ; a := 1
    mov dword [b], 10 ; b := 10

loop_start:
    ; while c < d
    mov eax, [a]
    cmp eax, [b]
    jnl loop_end ; Jump to loop_end if not less than

    ; Inside the loop
    ; c := c + 1
    mov eax, [a]
    inc eax
    mov [a], eax

    ; print(c)
    mov eax, [a]
    mov ebx, 1       ; File descriptor (stdout)
    mov ecx, output_fmt
    mov edx, 4       ; Message length
    int 0x80         ; System call for sys_write

    jmp loop_start   ; Jump back to loop_start

loop_end:
    ; Program exit
    mov eax, 1       ; System call for sys_exit
    xor ebx, ebx     ; Exit code 0
    int 0x80         ; System call interrupt
