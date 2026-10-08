global main
extern printf

section .data
    SYS_OPEN    equ 2
    SYS_READ    equ 0
    SYS_CLOSE   equ 3
    O_RDONLY    equ 0

    fmt_success db "%s: %d", 10, 0
    fmt_corrupt db "%s: файл испорчен", 10, 0

    buffer_size equ 65536

section .bss
    filename    resq 1
    file_desc   resq 1
    file_buffer resb buffer_size

section .text
main:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 8                      ; выравнивание стека под printf

    cmp rdi, 2
    jl .error_no_file

    mov rsi, [rsi + 8]
    mov [filename], rsi

    ; --- open ---
    mov rax, SYS_OPEN
    mov rdi, [filename]
    mov rsi, O_RDONLY
    xor rdx, rdx
    syscall
    test rax, rax
    js .file_corrupted
    mov [file_desc], rax

    ; --- read ---
    mov rax, SYS_READ
    mov rdi, [file_desc]
    mov rsi, file_buffer
    mov rdx, buffer_size
    syscall
    test rax, rax
    jle .file_corrupted_close

    ; r15 = размер данных, rbx = курсор
    mov r15, rax
    xor rbx, rbx

    ; --- close ---
    mov rax, SYS_CLOSE
    mov rdi, [file_desc]
    syscall


    ; Парсим строку X → r12 = сумма, r13 = количество    
    call .parse_line
    jc .file_corrupted
    test r13, r13
    jz .file_corrupted              ; пустая строка X

    ; Сохраняем X в r14 (сумма) и rbp-используем для счётчика
    mov r14, r12                    ; r14 = sum_x
    mov rbp, r13                    ; rbp = count_x


    ; Парсим строку Y → r12 = сумма, r13 = количество
    call .parse_line
    jc .file_corrupted
    cmp r13, rbp
    jne .file_corrupted

    ; --- Проверка «хвоста»: только пробелы и переводы строк ---
.trail:
    cmp rbx, r15
    jge .compute
    mov al, [file_buffer + rbx]
    inc rbx
    cmp al, ' '
    je .trail
    cmp al, 9
    je .trail
    cmp al, 10
    je .trail
    cmp al, 13
    je .trail
    jmp .file_corrupted

    
    ; Вычисление: (sum_x - sum_y) / count_x
.compute:
    mov rax, r14
    sub rax, r12
    cqo
    idiv rbp

    mov rdi, fmt_success
    mov rsi, [filename]
    mov rdx, rax
    xor rax, rax
    call printf
    jmp .exit



; ОБРАБОТЧИКИ ОШИБОК
.file_corrupted_close:
    mov rax, SYS_CLOSE
    mov rdi, [file_desc]
    syscall

.file_corrupted:
    mov rdi, fmt_corrupt
    mov rsi, [filename]
    xor rax, rax
    call printf

.exit:
    add rsp, 8
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    xor rax, rax
    ret

.error_no_file:
    add rsp, 8
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    mov rax, 1
    ret

; parse_line: разбирает одну строку чисел
;   вход:  rbx = курсор, r15 = конец буфера
;   выход: r12 = сумма чисел, r13 = количество,
;          rbx сдвинут за '\n' (или на конец буфера),
;          CF = 1 при ошибке формата

.parse_line:
    xor r12, r12                    ; сумма
    xor r13, r13                    ; количество

.next_number:
    ; --- пропускаем пробелы, табы, запятые ---
.skip:
    cmp rbx, r15
    jge .ok                         ; дошли до конца — строка кончилась
    mov al, [file_buffer + rbx]
    cmp al, ' '
    je .skip_inc
    cmp al, 9
    je .skip_inc
    cmp al, ','
    je .skip_inc
    cmp al, 10
    je .end_of_line                 ; '\n' — конец строки
    cmp al, 13
    je .end_of_line                 ; '\r' — тоже
    jmp .parse_number

.skip_inc:
    inc rbx
    jmp .skip

    ; --- читаем число ---
.parse_number:
    xor r10, r10                    ; знак: 0 = плюс, 1 = минус
    cmp al, '-'
    jne .check_plus
    mov r10, 1
    inc rbx
    cmp rbx, r15
    jge .err
    mov al, [file_buffer + rbx]
    jmp .digits

.check_plus:
    cmp al, '+'
    jne .digits
    inc rbx
    cmp rbx, r15
    jge .err
    mov al, [file_buffer + rbx]

.digits:
    xor rdx, rdx                    ; аккумулятор числа
    xor r11, r11                    ; флаг «была цифра»
.digit_loop:
    cmp al, '0'
    jl .end_digits
    cmp al, '9'
    jg .end_digits
    sub al, '0'
    imul rdx, rdx, 10
    movzx rax, al
    add rdx, rax
    mov r11, 1
    inc rbx
    cmp rbx, r15
    jge .end_digits
    mov al, [file_buffer + rbx]
    jmp .digit_loop

.end_digits:
    test r11, r11
    jz .err                         ; ни одной цифры не было
    test r10, r10
    jz .add
    neg rdx
.add:
    add r12, rdx
    inc r13
    jmp .next_number

.end_of_line:
    inc rbx                         ; съедаем '\n' или '\r'
    ; пропускаем возможный парный \r/\n
    cmp rbx, r15
    jge .ok
    mov al, [file_buffer + rbx]
    cmp al, 10
    je .skip_nl
    cmp al, 13
    jne .ok
.skip_nl:
    inc rbx
.ok:
    clc
    ret

.err:
    stc
    ret