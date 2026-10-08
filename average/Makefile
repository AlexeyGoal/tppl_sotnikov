all: average

average: main.o
	gcc -no-pie main.o -o average

main.o: main.asm
	nasm -f elf64 main.asm -o main.o

run: average
	./average data.txt

clean:
	rm -f average main.o

.PHONY: all run clean