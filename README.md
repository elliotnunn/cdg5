# The CDG5 project

The CDG5 project is a wide-ranging effort to hack on the Classic Mac OS. We are motivated in equal parts by curiosity, nostalgia and a wish to see the OS run well on computers and configurations unsupported by Apple.

If you want to contribute, or are just interested, get in touch. Discussion is mainly on the [mailing list](https://lists.ucc.gu.uwa.edu.au/mailman/listinfo/cdg5). Most of our testing takes place on the [MacOS9Lives](http://macos9lives.com) forums.

Reverse engineered source code:

- Patches to the widely distributed "SuperMario" source to compile a System file (7.1) or Mac OS ROM file (~OS 9.2.2): <http://github.com/elliotnunn/supermario>
- Thorough reversal of Gary Davidian's Power Macintosh NanoKernel: <http://github.com/elliotnunn/NanoKernel>
- Less-thorough reversal of René Vega's Multitasking NanoKernel: <http://github.com/elliotnunn/powermac-rom>
- Disk-based Start Manager: <http://github.com/elliotnunn/boot3>
- Bootloader-NanoKernel shim: <http://github.com/elliotnunn/wedge>

Some tools:

- Mac OS guest integration for Qemu: <http://github.com/elliotnunn/classicvirtio>
- Dump, patch and rebuild Mac OS ROM files: <http://github.com/elliotnunn/tbxi>, <http://github.com/elliotnunn/tbxi-patches>
- Get data into and out of [HFS disk images](https://pypi.org/project/machfs) and [resource forks](https://pypi.org/project/macresources), robustly and portably
- Build software in the Mac emulator of your choice: http://github.com/elliotnunn/BuildCubeE
- Patch PowerPC binaries: <http://github.com/elliotnunn/patchpef>
- Patch 68k MPW code objects: <http://github.com/elliotnunn/patchobj>
- Extract 68k MPW code objects from a ROM (used for the Mac OS ROM build above): <https://github.com/elliotnunn/unlink>
- Use my personal collection of hacky tools: <https://github.com/elliotnunn/ToolboxToolbox>
