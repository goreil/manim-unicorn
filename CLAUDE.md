# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

manim-unicorn is a framework for creating animated visualizations of x86/x86-64 code execution by combining Manim (animation) with Unicorn (CPU emulation) and Capstone (disassembly). Included examples demonstrate a Cachewarp (AMD-SEV INVD exploit) animation and a shellcode decoder animation.

## Build Commands

```bash
# Build the assembly payload (from repo root or code/)
cd code && make all        # Produces timewarp.elf, timewarp.raw, timewarp.objdump
cd code && make clean

# Render Manim animations
manim -pql unicorn-animation.py Timewarp      # Main Unicorn+Manim visualization (low quality preview)
manim -pql asm-animation.py Combined           # C/ASM side-by-side walkthrough
manim -pql shellcode-animation.py Animation    # Shellcode decoder visualization

# Higher quality render
manim -pqh unicorn-animation.py Timewarp
```

## Dependencies

- **Manim** - animation framework (`from manim import *`)
- **Unicorn** - CPU emulator (`from unicorn import *`)
- **Capstone** - disassembler (`from capstone import *`, used in shellcode-animation.py)
- **GCC + binutils** - for compiling `timewarp.S` with `gcc -nostdlib` and `objdump`/`objcopy`

## Architecture

The animation pipeline has two stages:

1. **Assembly build** (`code/Makefile`): `timewarp.S` -> `timewarp.elf` -> `timewarp.raw` (raw .text bytes) + `timewarp.objdump` (Intel-syntax disassembly)
2. **Manim render**: Python scripts load code into Unicorn, step through instructions via `UC_HOOK_CODE`, and drive Manim animations from the hook callback.

### Animation scripts

- **unicorn-animation.py** (`Timewarp` scene) - Emulates x86-64 code, tracks registers (rax, rdi, rsi) and the return address on stack. The `timewarp` list `[prev_addr, target_addr]` controls when stack memory is saved and when INVD is triggered to restore it, simulating the cache attack.
- **asm-animation.py** (`Combined` scene) - Side-by-side C source and assembly with synchronized line highlighting. The `asm_order`/`c_order` arrays map assembly execution order to corresponding C lines.
- **shellcode-animation.py** (`Animation` scene) - Visualizes shellcode (msfvenom output) byte-by-byte decoding with Capstone disassembly and register tracking.

### Configuration

- **format.json** - Shared Manim text/code styling (font, font_size, background) used by shellcode-animation.py.
- Inline formatting dicts (`code_formatting`, `REG_FORMAT`, `rectange_format`) in each animation script.

### Unicorn memory layout

- Code base: `0x1000` (unicorn-animation) or `0x8048000` (shellcode-animation)
- Stack: `0x1000000`, size `0x2000`, initial RSP at `STACK + 0x1000`
- Return address tracked at `INITIAL_STACK - 8`
