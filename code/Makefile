all: timewarp.elf timewarp.raw timewarp.objdump

timewarp.elf: timewarp.S
	gcc timewarp.S -nostdlib -o timewarp.elf

timewarp.raw: timewarp.elf
	objcopy --dump-section .text=timewarp.raw timewarp.elf

timewarp.objdump: timewarp.elf
	objdump -M intel -d timewarp.elf | sed -e '1,6d'> timewarp.objdump

clean:
	rm timewarp.raw timewarp.elf timewarp.objdump


