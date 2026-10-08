all: average

average: average.o
	gcc -no-pie average.o -o average

average.o: average.asm
	nasm -f elf64 average.asm -o average.o

run: average
	./average data.txt

clean:
	rm -f average average.o

.PHONY: all run clean