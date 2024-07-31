from unicorn import *
from unicorn.x86_const import *
from manim import *
from capstone import *
import json
import textwrap


class EmulationFinished(Exception):
    """Exception when emulation is finished"""
    pass

buf =  b""
buf += b"\xbd\xc1\x74\x21\xa1\xda\xc4\xd9\x74\x24\xf4\x5a"
buf += b"\x2b\xc9\xb1\x06\x31\x6a\x13\x03\x6a\x13\x83\xc2"
buf += b"\xc5\x96\xd4\xe9\x7d\x79\x75\x83\x13\xa9\x0a\x3b"
buf += b"\xeb\x2c\xbc\xef\xb4\x1c\x63\x7a\x71\xf9\x94\x7f"


# buf = bytes.fromhex("b80a000000" * 2)

# EMULATOR SETUP
CODE = buf
ADDRESS = 0x8048000 # RIP START
STACK = 0x1000000
STACK_SIZE = 0x2000
mu = Uc(UC_ARCH_X86, UC_MODE_64)
mu.mem_map(ADDRESS, ((len(CODE) // 0x1000) + 1 ) * 0x1000)
mu.mem_map(STACK, STACK_SIZE)
INITIAL_STACK = STACK + 0x1000
mu.mem_write(ADDRESS, CODE)
mu.reg_write(UC_X86_REG_RSP, INITIAL_STACK)

# Disassembler setup
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

# Animation setup
FORMAT = json.load(open("format.json"))

man_regs = VGroup()
reg_vals = [
    ("rax", UC_X86_REG_RAX),
    # ("rbx", UC_X86_REG_RBX),
    ("rcx", UC_X86_REG_RCX),
    ("rdx", UC_X86_REG_RDX),
    ("rdi", UC_X86_REG_RDI),
    ("rsi", UC_X86_REG_RSI),
    # ("r8", UC_X86_REG_R8),
    # ("r9", UC_X86_REG_R9),
    # ("r10", UC_X86_REG_R10),
    # ("r11", UC_X86_REG_R11),
    # ("r12", UC_X86_REG_R12),
    # ("r13", UC_X86_REG_R13),
    # ("r14", UC_X86_REG_R14),
    # ("r15", UC_X86_REG_R15),
    ("rbp", UC_X86_REG_RBP),
    ("rsp", UC_X86_REG_RSP),
    # ("rip", UC_X86_REG_RIP),
]
for reg_name,_ in reg_vals:
    var = Variable(0, Text(reg_name, **FORMAT["registers"]))
    var.value._get_num_string = lambda x: f"{int(x):x}"
    man_regs += var

man_regs.arrange(DOWN, buff=.1)
man_regs.to_corner(UR)
# man_regs.shift(DOWN * 2)
man_regs.shift(LEFT)


EMULATION_END = float('inf') # For debugging purposes
EMULATION_END = 2
WRAP_SIZE = 32
def wrap(buf):
    """Turn bytes into word_wrapped hex"""
    return textwrap.fill(buf.hex(), WRAP_SIZE)

man_text = Text(wrap(buf), **FORMAT["text"])
man_text.to_edge(UP)

class Animation(Scene):
    def __init__(self, **kwargs):
        self.last_buf = buf
        self.i = 0
        self.last_ins = None
        super(**kwargs).__init__()

    def construct(self):
        self.add(man_regs)
        self.add(man_text)
        self.last_history = Text("History", **FORMAT["text"])
        self.last_history.to_corner(UL)
        self.add(self.last_history)

        # Initialize Register values
        self.reg = {}
        for (reg_name,uni_const) in (reg_vals):
            self.reg[reg_name] = 0

        def hook_code(uc, address, size, user_data):
            print(f"Instruction {self.i}")

            # Change registers
            indicate_anims = []
            set_value_anims = []
            for man_reg,(reg_name,track_value) in zip(man_regs,reg_vals):
                value = mu.reg_read(track_value)
                if value != self.reg[reg_name]:
                    indicate_anims.append(Indicate(man_reg))
                    set_value_anims.append(man_reg.tracker.animate.set_value(value))
                    self.reg[reg_name] = value

            if len(indicate_anims) > 0:
                self.play(*indicate_anims)
                self.play(*set_value_anims)

            # Move instruction to last history
            if self.i != 0:
                self.play(MoveToTarget(self.last_history))

            # Transform Text section
            # TODO: Marking changes doesn't really work
            current_buf = uc.mem_read(ADDRESS, len(CODE))
            if current_buf != self.last_buf:
                # Get 8 byte slice where they differ:
                for i in range(0, 8, len(current_buf)-8):
                    if current_buf[i:i+8] != self.last_buf[i:i+8]:
                        slice = man_text[2*i:2*(i+8)]
                        self.play(Indicate(slice, color=RED))


                new_text = Text(wrap(current_buf), **FORMAT["text"])
                new_text.to_edge(UP)
                self.play(Transform(man_text, new_text))
                self.last_buf = current_buf

            # Grab current instruction
            start = address-ADDRESS
            end = start + size

            def to_wrap(idx):
                return 2* idx

            cur_text = man_text[to_wrap(start):to_wrap(end)]
            cur_text.set_color(YELLOW)
            man_ins = cur_text.copy()

            for _, _, inst, ops in md.disasm_lite(current_buf[start:end], address):
                break
            self.play(AnimationGroup(Indicate(cur_text), man_ins.animate.center()))

            # Transform into instruction
            line = f"{inst} {ops}"
            self.play(Transform(man_ins, Text(line, **FORMAT["text"])))
            cur_text.set_color(WHITE)


            # Add to history
            man_ins.generate_target()
            man_ins.target.next_to(self.last_history, DOWN * .1)
            man_ins.target.scale(.5).align_to(self.last_history, LEFT)
            self.last_history = man_ins


            self.i += 1
            if "syscall" in line or self.i == EMULATION_END:
                raise EmulationFinished

        mu.hook_add(UC_HOOK_CODE, hook_code)
        try:
            mu.emu_start(ADDRESS, ADDRESS+len(CODE))
        except EmulationFinished:
            pass


class TitleCard(Scene):
    def construct(self):
       text = Text("msfvenom -p linux/x64/exec -f python -e x86/shikata_ga_nai", **FORMAT["text"])
       self.play(Write(text))

       man_code = Text(wrap(buf), **FORMAT["text"])
       man_code.to_edge(UP)

       self.play(Write(man_code))
       self.wait(1)
