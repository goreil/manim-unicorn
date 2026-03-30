# manim-unicorn

Animated visualizations of x86/x86-64 code execution, combining [Manim](https://www.manim.community/) for animation with [Unicorn](https://www.unicorn-engine.org/) for CPU emulation and [Capstone](https://www.capstone-engine.org/) for disassembly.

The idea: hook into each instruction step of an emulated binary and generate a corresponding animation frame — register changes, memory modifications, and control flow are all visualized in real time.

## Showcase

### Cachewarp exploit visualization (`unicorn-animation.py`)

Emulates x86-64 assembly step-by-step, tracking registers and the return address on the stack. Demonstrates a [Cachewarp](https://cachewarpattack.com/) (AMD-SEV INVD) exploit — a single dropped memory write hijacks control flow.

https://github.com/goreil/manim-unicorn/raw/main/showcase/timewarp.mp4

### C / Assembly side-by-side (`asm-animation.py`)

Synchronized line-by-line highlighting of C source code and its compiled assembly, showing how high-level constructs map to instructions.

https://github.com/goreil/manim-unicorn/raw/main/showcase/combined.mp4

### Shellcode decoder (`shellcode-animation.py`)

Decodes and steps through shikata_ga_nai encoded shellcode, showing byte-level mutations and disassembled instructions.

## Dependencies

- Python 3
- [Manim Community](https://docs.manim.community/en/stable/installation.html)
- [Unicorn](https://pypi.org/project/unicorn/)
- [Capstone](https://pypi.org/project/capstone/)
- GCC and binutils (for building the assembly payload)

```bash
pip install manim unicorn capstone
```

## Usage

### Build the assembly payload

```bash
cd code && make all
```

This compiles `timewarp.S` into `timewarp.raw` (raw .text bytes) and `timewarp.objdump` (Intel-syntax disassembly), which are loaded at runtime by `unicorn-animation.py`.

### Render animations

```bash
# Low quality preview (fast)
manim -pql unicorn-animation.py Timewarp

# High quality
manim -pqh unicorn-animation.py Timewarp

# Other examples
manim -pql asm-animation.py Combined
manim -pql shellcode-animation.py Animation
```

## How It Works

1. **Unicorn** emulates the binary instruction-by-instruction
2. A `UC_HOOK_CODE` callback fires on each step, reading register state and memory
3. The callback drives **Manim** animations: highlighting the current instruction, updating register displays, and visualizing memory changes
4. For the Cachewarp example, stack memory is snapshot at a configurable address and later restored (simulating INVD), showing how a single dropped write leads to control flow hijacking

## License

MIT
