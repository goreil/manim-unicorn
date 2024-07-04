from manim import *
from unicorn import *
from unicorn.x86_const import *

code_formatting = {
    "background":"rectangle",
    # "font_size":24
}
rectange_format = {
        "stroke_width":0,
        "stroke_color":YELLOW,
        "fill_color":YELLOW,
        "fill_opacity":0.2
}
REG_FORMAT = {
    # "should_center":False, 
    # "font":"monospace",
    "font_size":24
}

def initial_image(self):
    c_code = Code("code/timewarp.c", insert_line_no=False, **code_formatting)
    c_code.to_corner(UL)
    asm_code = Code("code/timewarp.nasm", **code_formatting)
    asm_code.to_corner(UR)
    self.add(c_code, asm_code)

    return c_code, asm_code


# class Background(Scene):
#     """Used for testing"""
#     def construct(self):
#         c_code, asm_code = initial_image(self)

#         registers = VGroup()
#         for reg in ["rax", "rdi", "rsi"]:
#             registers += Text(f"{reg} : 0", **REG_FORMAT)

#         registers.arrange(DOWN)
#         registers.to_corner(DL)
#         self.add(registers)

#         rax = registers[0]
#         rax.text = "rax : 1"
#         self.play(Transform(registers[0], Text("rax : 1", **REG_FORMAT), replace_mobject_with_target_in_scene=True))


    

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
            c_highlight = Rectangle(width=c_line.width, height=lineheight, **rectange_format)

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