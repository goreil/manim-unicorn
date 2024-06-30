all: timewarp.elf timewarp.raw

timewarp.elf: timewarp.S
	gcc timewarp.S -nostdlib -o timewarp.elf

timewarp.raw: timewarp.elf
	objcopy --dump-section .text=timewarp.raw timewarp.elf


