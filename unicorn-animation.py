#!/usr/bin/env python
from unicorn import *
from unicorn.x86_const import *
from manim import *

timewarp=[0x1008, 0x1026]
class EmulationFinished(Exception):
    """Exception when emulation is finished"""
    pass
# MANIM FORMATTING
code_formatting = {
    "background":"rectangle",
    "language": "nasm",
    "font_size":24
}
rectange_format = {
        "stroke_width":0,
        "fill_opacity":0.4
}
REG_FORMAT = {
    "font":"monospace",
    # "should_center":False,
    "font_size":30
}

# UNICORN
# code to be emulated
with open('code/timewarp.raw', 'rb') as f:
    CODE = f.read()

# objdump
with open('code/timewarp.objdump') as f:
    DISASS = f.read()
DISASS = DISASS.splitlines()
# Get line numbers
lines = dict()

for cnt, line in enumerate(DISASS):
    line = line.strip()
    if line.startswith("1"):
        addr = int(line.split(":")[0], 16)
        lines[addr] = cnt

# EMULATION Setup
ADDRESS = 0x1000 # RIP START
STACK = 0x1000000
# Initialize emulator in X86-32bit mode
mu = Uc(UC_ARCH_X86, UC_MODE_64)

# map enough memory
mu.mem_map(ADDRESS, ((len(CODE) // 0x1000) + 1 ) * 0x1000)
STACK_SIZE = 0x2000
mu.mem_map(STACK, STACK_SIZE)

INITIAL_STACK = STACK + 0x1000

# write machine code to be emulated to memory
mu.mem_write(ADDRESS, CODE)

# RSP in the middle of the stack
mu.reg_write(UC_X86_REG_RSP, INITIAL_STACK)


print("Emulate code")
END_OFFSET = 0x5 # First 3 steps
# END_OFFSET = 0x24
PAUSE_TIME = 1.5
class Timewarp(Scene):
    def construct(self):
        """timewarp: lines at which the timewarp should take place"""
        if timewarp is not None:
            assert len(timewarp) == 2, "Timewarp needs to be None or [prev, target]"
            prev, target = timewarp
            assert prev in lines
            assert target in lines

        # Code
        asm_code = Code(code="\n".join(DISASS), insert_line_no=False, **code_formatting)
        asm_code.to_corner(UL)
        asm_lines = asm_code.code.lines[0]
        lineheight = asm_lines[0].height * 1.05
        self.add(asm_code)

        # Registers
        reg_vals = [
            ("_ = rax", UC_X86_REG_RAX),
            ("a = rdi", UC_X86_REG_RDI),
            ("b = rsi", UC_X86_REG_RSI),
        ]
        registers = VGroup()
        for reg,_ in reg_vals:
            var = Variable(0, Text(reg, **REG_FORMAT), num_decimal_places=0)
            # Overwrite function that displays the value
            # var.value._get_num_string = lambda x: hex(int(x))
            registers += var

        registers.arrange(DOWN)
        registers.next_to(asm_code, RIGHT * 2)
        self.add(registers)

        # Return Address
        ret_addr = Variable(0, Text("retaddr", **REG_FORMAT))
        ret_addr.value._get_num_string = lambda x: f"{int(x):x}"
        ret_addr.label.set_color(GREEN)
        ret_addr.value.set_color(GREEN)
        ret_addr.value.set_value(0)
        ret_addr.next_to(registers, DOWN * 2)
        self.add(ret_addr)


        self.asm_highlight_last = None
        self.ret_highlight_last = None
        def hook_code(uc, address, size, user_data):
            global timewarp
            global PAUSE_TIME
            # If current instruction is int3 exit
            if timewarp is not None:
                prev, timewarp_target = timewarp
                if address == prev:
                    # Save Memory
                    self.stored_stack = mu.mem_read(STACK, STACK_SIZE)

            lineno = lines[address]
            # print(f"line number:{lineno}, code: {DISASS[lineno]}")
            asm_line = asm_lines[lineno]
            asm_highlight = Rectangle(width=asm_line.width, height=lineheight, fill_color = YELLOW, **rectange_format)
            asm_highlight.move_to(asm_line, DL)
            
            animations = list()
            if self.asm_highlight_last is None:
                self.add(asm_highlight)
            else:
                animations.append(Transform(self.asm_highlight_last, asm_highlight, replace_mobject_with_target_in_scene=True))
            self.asm_highlight_last = asm_highlight

            # Track registers
            for reg,(_,track_value) in zip(registers,reg_vals):
                value = mu.reg_read(track_value)
                animations.append(reg.tracker.animate.set_value(value))
                

            # Track Returnaddress
            value = mu.mem_read(INITIAL_STACK - 8, 8)
            value = int(value[::-1].hex(), 16)
            animations.append(ret_addr.tracker.animate.set_value(value))
            # Check if value != 0:
            if value != 0:
                ret_line = asm_lines[lines[value]]
                ret_highlight = Rectangle(width=ret_line.width, height=lineheight, fill_color = GREEN, **rectange_format)
                ret_highlight.move_to(ret_line, DL)
                if self.ret_highlight_last is None:
                    self.add(ret_highlight)
                else:
                    animations.append(Transform(self.ret_highlight_last, ret_highlight, replace_mobject_with_target_in_scene=True))
                
                self.ret_highlight_last = ret_highlight

            if animations:
                self.play(*animations)
                self.pause(PAUSE_TIME)

            # Trigger Timewarp
            if timewarp and address == timewarp_target:
                warn = Text("Trigger INVD", font_size=72, color=RED, font="monospace")
                square = Rectangle(color=WHITE, fill_color=WHITE, fill_opacity=0.2)
                square.surround(warn)
                self.add(square)
                self.play(Write(warn))
                self.pause()
                self.play(FadeOut(warn), FadeOut(square))

                # Change color of RetAddr
                ret_addr.value.set_color(RED)
                ret_addr.label.set_color(RED)

                # Indicate Important
                self.play(Indicate(ret_addr))
                self.pause()

                animations = []
                # Overwrite memory
                mu.mem_write(STACK, bytes(self.stored_stack))

                value = mu.mem_read(INITIAL_STACK - 8, 8)
                value = int(value[::-1].hex(), 16)
                animations.append(ret_addr.tracker.animate.set_value(value))
                # Check if value != 0:
                if value != 0:
                    ret_line = asm_lines[lines[value]]
                    ret_highlight = Rectangle(width=ret_line.width, height=lineheight, fill_color = RED, **rectange_format)
                    ret_highlight.move_to(ret_line, DL)
                    if self.ret_highlight_last is None:
                        self.add(ret_highlight)
                    else:
                        animations.append(Transform(self.ret_highlight_last, ret_highlight, replace_mobject_with_target_in_scene=True))
                    
                    self.ret_highlight_last = ret_highlight

                self.play(*animations)
                self.pause()

                ret_addr.value.set_color(GREEN)
                ret_addr.label.set_color(GREEN)
                
                # Stop timewarp
                timewarp = None
                # Speed up the rest
                # PAUSE_TIME = 0.5

            if size == 1 and mu.mem_read(address, size) == b'\xcc':
                raise EmulationFinished
            
        mu.hook_add(UC_HOOK_CODE, hook_code)
        # Explanation time at beginning
        self.pause(2)
        try:
            mu.emu_start(ADDRESS, ADDRESS+len(CODE))
        except EmulationFinished:
            # Run until end
            pass
    
        self.pause(1)


        
# class Without_Timewarp(Scene):
#     def construct(self):
#         """timewarp: lines at which the timewarp should take place"""

#         # Code
#         asm_code = Code(code="\n".join(DISASS), insert_line_no=False, **code_formatting)
#         asm_code.to_corner(UL)
#         asm_lines = asm_code.code.lines[0]
#         lineheight = asm_lines[0].height * 1.05
#         self.add(asm_code)

#         # Registers
#         reg_vals = [
#             ("_ = rax", UC_X86_REG_RAX),
#             ("a = rdi", UC_X86_REG_RDI),
#             ("b = rsi", UC_X86_REG_RSI),
#         ]
#         registers = VGroup()
#         for reg,_ in reg_vals:
#             var = Variable(0, Text(reg, **REG_FORMAT), num_decimal_places=0)
#             # Overwrite function that displays the value
#             # var.value._get_num_string = lambda x: hex(int(x))
#             registers += var

#         registers.arrange(DOWN)
#         registers.next_to(asm_code, RIGHT * 2)
#         self.add(registers)

#         # Return Address
#         ret_addr = Variable(0, Text("retaddr", **REG_FORMAT))
#         ret_addr.value._get_num_string = lambda x: f"{int(x):x}"
#         ret_addr.label.set_color(GREEN)
#         ret_addr.value.set_color(GREEN)
#         ret_addr.value.set_value(0)
#         ret_addr.next_to(registers, DOWN * 2)
#         self.add(ret_addr)


#         self.asm_highlight_last = None
#         self.ret_highlight_last = None
#         def hook_code(uc, address, size, user_data):
#             # If current instruction is int3 exit

#             lineno = lines[address]
#             # print(f"line number:{lineno}, code: {DISASS[lineno]}")
#             asm_line = asm_lines[lineno]
#             asm_highlight = Rectangle(width=asm_line.width, height=lineheight, fill_color = YELLOW, **rectange_format)
#             asm_highlight.move_to(asm_line, DL)
            
#             animations = list()
#             if self.asm_highlight_last is None:
#                 self.add(asm_highlight)
#             else:
#                 animations.append(Transform(self.asm_highlight_last, asm_highlight, replace_mobject_with_target_in_scene=True))
#             self.asm_highlight_last = asm_highlight

#             # Track registers
#             for reg,(_,track_value) in zip(registers,reg_vals):
#                 value = mu.reg_read(track_value)
#                 animations.append(reg.tracker.animate.set_value(value))

#             # Track Returnaddress
#             value = mu.mem_read(INITIAL_STACK - 8, 8)
#             value = int(value[::-1].hex(), 16)
#             animations.append(ret_addr.tracker.animate.set_value(value))
#             # Check if value != 0:
#             if value != 0:
#                 ret_line = asm_lines[lines[value]]
#                 ret_highlight = Rectangle(width=ret_line.width, height=lineheight, fill_color = GREEN, **rectange_format)
#                 ret_highlight.move_to(ret_line, DL)
#                 if self.ret_highlight_last is None:
#                     self.add(ret_highlight)
#                 else:
#                     animations.append(Transform(self.ret_highlight_last, ret_highlight, replace_mobject_with_target_in_scene=True))
                
#                 self.ret_highlight_last = ret_highlight

#             if animations:
#                 self.play(*animations)
#                 self.pause()

#             if size == 1 and mu.mem_read(address, size) == b'\xcc':
#                 raise EmulationFinished
            


#         mu.hook_add(UC_HOOK_CODE, hook_code)
#         try:
#             mu.emu_start(ADDRESS, ADDRESS+len(CODE))
#         except EmulationFinished:
#             # Run until end
#             pass

class Test(Scene):
    def construct(self):
        warn = Text("TRIGGER TIMEWARP", font_size=72, color=RED)
        self.play(Write(warn))
        self.pause()
        self.play(FadeOut(warn))