global main
extern printf

section .data
    ; Системные вызовы Linux x86_64
    SYS_OPEN    equ 2
    SYS_READ    equ 0
    SYS_CLOSE   equ 3
    O_RDONLY    equ 0

    ; Форматы для printf
    fmt_success db "%s: %d", 10, 0
    fmt_corrupt db "%s: файл испорчен", 10, 0

    max_elements equ 10000          ; Максимальный размер массивов

section .bss
    filename    resq 1
    file_desc   resq 1
    
    ; Буфер для чтения файла (64 КБ)
    buffer_size equ 65536
    file_buffer resb buffer_size
    
    ; Выделенные массивы чисел
    array_x     resd max_elements
    array_y     resd max_elements

section .text
main:
    push rbp
    mov rbp, rsp

    ; Проверяем argc >= 2
    cmp rdi, 2
    jl .error_no_file

    ; Сохраняем имя файла
    mov rsi, [rsi + 8]
    mov [filename], rsi

    ; 1. Системный вызов open(filename, O_RDONLY)
    mov rax, SYS_OPEN
    mov rdi, [filename]
    mov rsi, O_RDONLY
    xor rdx, rdx
    syscall
    
    cmp rax, 0
    jl .file_corrupted              ; Если дескриптор < 0, то ошибка открытия
    mov [file_desc], rax

    ; 2. Системный вызов read(fd, file_buffer, buffer_size)
    mov rax, SYS_READ
    mov rdi, [file_desc]
    mov rsi, file_buffer
    mov rdx, buffer_size
    syscall
    
    cmp rax, 0
    jle .file_corrupted_close       ; Ошибка чтения или пустой файл
    
    ; Сохраняем реальный размер прочитанных данных в r15
    mov r15, rax 

    ; 3. Системный вызов close(fd)
    mov rax, SYS_CLOSE
    mov rdi, [file_desc]
    syscall

    ; начало парсинга
    xor rbx, rbx                    ; rbx = текущий индекс в file_buffer (указатель)
    
    ; --- ЭТАП 1: Парсим первую строку (массив X) ---
    xor r12, r12                    ; r12 = количество элементов в X

.parse_x_loop:
    ; Пропускаем пробелы и запятые перед числом
    call .skip_spaces_and_commas
    
    ; Если дошли до конца файла или перевода строки — парсинг X окончен
    cmp rbx, r15
    jge .x_parsing_done
    mov al, [file_buffer + rbx]
    cmp al, 10                      ; '\n'
    je .x_parsing_done
    cmp al, 13                      ; '\r'
    je .x_parsing_done

    ; Проверяем лимит массива
    cmp r12, max_elements
    jge .file_corrupted

    ; Считываем число
    call .parse_integer             ; Возвращает число в RAX, обновляет rbx
    jc .file_corrupted              ; Если флаг переноса CF=1, значит встретили не-число
    
    mov [array_x + r12*4], eax      ; Сохраняем в массив X
    inc r12
    jmp .parse_x_loop

.x_parsing_done:
    cmp r12, 0
    je .file_corrupted              ; Если в X ничего нет — ошибка

    ; Пропускаем символы перевода строки, чтобы перейти к строке Y
.skip_nl:
    cmp rbx, r15
    jge .file_corrupted             ; Если файл кончился, а строки Y нет — ошибка
    mov al, [file_buffer + rbx]
    cmp al, 10
    je .next_line
    cmp al, 13
    je .next_line
    jmp .file_corrupted             ; Любой другой символ на месте перевода строки — ошибка
.next_line:
    inc rbx
    cmp rbx, r15
    jge .file_corrupted             ; Опять же, за переводом строки должно что-то быть
    mov al, [file_buffer + rbx]
    cmp al, 10
    je .next_line                   ; Пропускаем возможный парный \n (для \r\n)
    cmp al, 13
    je .next_line

    ; --- ЭТАП 2: Парсим вторую строку (массив Y) ---
    xor r13, r13                    ; r13 = количество элементов в Y
.parse_y_loop:
    call .skip_spaces_and_commas
    
    ; Если дошли до конца файла или новой строки — парсинг Y окончен
    cmp rbx, r15
    jge .y_parsing_done
    mov al, [file_buffer + rbx]
    cmp al, 10
    je .y_parsing_done
    cmp al, 13
    je .y_parsing_done

    cmp r13, r12
    jg .file_corrupted              ; Если в Y уже больше элементов, чем в X — ошибка

    call .parse_integer
    jc .file_corrupted
    
    mov [array_y + r13*4], eax
    inc r13
    jmp .parse_y_loop

.y_parsing_done:
    ; Сравниваем длины массивов X и Y
    cmp r12, r13
    jne .file_corrupted

    ; --- ЭТАП 3: Вычисления ---
    xor r8, r8                      ; r8 = индекс i
    xor r9, r9                      ; r9 = сумма разностей

.loop_calc:
    cmp r8, r12
    jge .calc_average

    movsxd rax, dword [array_x + r8*4]
    movsxd rbx, dword [array_y + r8*4]
    sub rax, rbx
    add r9, rax

    inc r8
    jmp .loop_calc

.calc_average:
    mov rax, r9
    cqo
    idiv r12                        ; rax = r9 / r12 (целочисленное деление)

    ; Вывод через printf
    mov rdi, fmt_success
    mov rsi, [filename]
    mov rdx, rax
    xor rax, rax
    call printf
    jmp .exit_normal

.file_corrupted_close:
    mov rax, SYS_CLOSE
    mov rdi, [file_desc]
    syscall

.file_corrupted:
    mov rdi, fmt_corrupt
    mov rsi, [filename]
    xor rax, rax
    call printf

.exit_normal:
    mov rsp, rbp
    pop rbp
    xor rax, rax
    ret

.error_no_file:
    mov rsp, rbp
    pop rbp
    mov rax, 1
    ret



; Пропуск пробелов, табуляций и запятых
.skip_spaces_and_commas:
    cmp rbx, r15
    jge .skip_done
    mov al, [file_buffer + rbx]
    cmp al, ' '
    je .skip_inc
    cmp al, 9                       ; '\t'
    je .skip_inc
    cmp al, ','
    je .skip_inc
    ret
.skip_inc:
    inc rbx
    jmp .skip_spaces_and_commas
.skip_done:
    ret

; Парсинг знакового целого числа
; Вход: rbx — позиция в буфере. Выход: RAX — число, CF=1 при ошибке
.parse_integer:
    push r10
    push r11
    
    xor r10, r10                    ; r10 = знак (0 - плюс, 1 - минус)
    xor rax, rax                    ; rax = результат аккумулятора
    xor r11, r11                    ; r11 = флаг, прочитана ли хоть одна цифра

    cmp rbx, r15
    jge .parse_int_err

    ; Проверяем знак
    mov cl, [file_buffer + rbx]
    cmp cl, '-'
    je .is_minus
    cmp cl, '+'
    je .is_plus
    jmp .parse_digits

.is_minus:
    mov r10, 1
    inc rbx
    jmp .parse_digits
.is_plus:
    inc rbx

.parse_digits:
    cmp rbx, r15
    jge .parse_int_end
    
    mov cl, [file_buffer + rbx]
    cmp cl, '0'
    jl .parse_int_end
    cmp cl, '9'
    jg .parse_int_end

    ; Перевод символа в цифру и добавление в аккумулятор (rax = rax * 10 + digit)
    sub cl, '0'
    mov rdi, 10
    imul rax, rdi
    movzx rdx, cl
    add rax, rdx
    
    mov r11, 1                      ; Выставляем флаг, что цифра была
    inc rbx
    jmp .parse_digits

.parse_int_end:
    cmp r11, 0                      ; Если ни одной цифры не встретили — это ошибка
    je .parse_int_err
    
    cmp r10, 1                      ; Если был минус, инвертируем число
    jne .parse_int_success
    neg rax

.parse_int_success:
    clc                             ; Сбрасываем флаг переноса (нет ошибки)
    pop r11
    pop r10
    ret

.parse_int_err:
    stc                             ; Устанавливаем флаг переноса (ошибка парсинга)
    pop r11
    pop r10
    ret
