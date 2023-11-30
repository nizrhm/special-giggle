Save the assembly code to a file, e.g., your_file.asm.
Use NASM to assemble it: nasm -f elf32 your_file.asm -o your_file.o
Link the object file with LD: ld -m elf_i386 -s -o your_executable your_file.o