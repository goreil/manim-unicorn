from manim import *
from unicorn import *
from unicorn.x86_const import *

code_formatting = {
    "background":"rectangle",
    "insert_line_no":False,
    "font_size":24
}
rectange_format = {
        "stroke_width":0,
        "stroke_color":YELLOW,
        "fill_color":YELLOW,
        "fill_opacity":0.2
}
REG_FORMAT = {
    "should_center":False, 
    "font":"monospace",
    "font_size":30
}

def initial_image(self):
    c_code = Code("code/timewarp.c", insert_line_no=False, **code_formatting)
    c_code.to_corner(UL)
    asm_code = Code("code/timewarp.nasm", **code_formatting)
    asm_code.to_corner(UR)
    self.add(c_code, asm_code)

    return c_code, asm_code

class INVD(Scene):
    def construct(self):
        warn = Text("Trigger INVD", font_size=72, color=RED, font="monospace")
        square = Rectangle(color=WHITE, fill_color=WHITE, fill_opacity=0.2)
        square.surround(warn)
        self.add(square)
        self.play(Write(warn))
        self.pause()
        self.play(FadeOut(warn), FadeOut(square))

class Transform(Scene):
    def construct(self):
        c_code = Code("code/timewarp.c", **code_formatting)
        c_code.to_corner(UL)
        asm_code = Code(code=open("code/timewarp.objdump").read(), **code_formatting, language="nasm")
        asm_code.to_corner(UR)

        self.play(Write(c_code))

        lines = c_code.code.lines[0]
        self.play(Indicate(lines[3]))
        self.play(Indicate(lines[4]))
        self.pause()
        self.play(Indicate(lines[1]), Indicate(lines[8]))
        self.pause()
        self.play(Indicate(lines[2]), Indicate(lines[11]))

        self.play(TransformFromCopy(c_code, asm_code))
        self.wait(2.5)
        asm_code.generate_target()
        asm_code.target.to_corner(UL)
        self.play(FadeOut(c_code), MoveToTarget(asm_code))
        self.pause()
        # self.play()

class TitleCard(Scene):
    def construct(self):
        text = Text("Cachewarp", font_size=72, color=ORANGE)
        self.play(Write(text))
        subtext = Text("Dropping one write to take over AMD-SEV", font_size=50)
        subtext.next_to(text, DOWN)
        self.play(Write(subtext))
        self.pause()
        self.play(Unwrite(text), Unwrite(subtext))
        self.pause()

class NormalBehaviorText(Scene):
    def construct(self):
        text = Text("Normal Behavior", font_size=72, color=GREEN)
        self.play(Write(text))
        self.pause()
        self.play(Unwrite(text))
        self.pause()

class WithTimewarpText(Scene):
    def construct(self):
        text = Text("With Timewarp", font_size=72, color=RED)
        self.play(Write(text))
        self.pause()
        self.play(Unwrite(text))
        self.pause()
    

class Combined(Scene):
    def construct(self):
        c_code, asm_code = initial_image(self)

        c_lines = c_code.code.lines[0]
        asm_lines = asm_code.code.lines[0]
        # One fixed lineheight for consistency
        lineheight = asm_lines[0].height * 1.05
        
        asm_order = [7,8,9,  1,2,3,  10,11,  4,5,6, 12, 13, 14, 18]
        c_order =   [7,7,8,  1,2,2,  8 ,9 ,  4,5,5, 9 , 10, 10, 13]
        asm_highlight_last = None
        c_highlight_last = None
        for asm_idx, c_idx in zip(asm_order, c_order):
            # Create both highlights
            asm_idx, c_idx = asm_idx-1, c_idx - 1
            asm_line, c_line = asm_lines[asm_idx], c_lines[c_idx]
            asm_highlight = Rectangle(width=asm_line.width, height=lineheight, **rectange_format)
            c_highlight = Rectangle(width=c_line.width, **rectange_format)

            # Position the rectangle to cover the line
            asm_highlight.move_to(asm_line, DL)
            c_highlight.move_to(c_line, DL)

            if asm_highlight_last is None:
                self.add(asm_highlight)
                self.add(c_highlight)
            else:
                self.play(
                    Transform(asm_highlight_last, asm_highlight, replace_mobject_with_target_in_scene=True),
                    Transform(c_highlight_last, c_highlight, replace_mobject_with_target_in_scene=True)
                )

            asm_highlight_last = asm_highlight
            c_highlight_last = c_highlight