# The CDG5 project

The CDG5 project is an effort to thoroughly reverse-engineer Mac OS 9.2.2, the final release of the "Classic" Mac OS. We place an emphasis on supporting late-model PowerPC G4-based Macs, and also on hacking new features into the OS (e.g. support for >1.5 GB RAM).

Our work is spread over several GitHub repositories:

- 3 MB 68k ROM: <http://github.com/elliotnunn/mac-rom>
- 4 MB PowerPC rom, inc. NanoKernel: <http://github.com/elliotnunn/powermac-rom>
- Bootable "Mac OS ROM" file: <http://github.com/elliotnunn/newworld-rom>
- Disk-based Start Manager: <http://github.com/elliotnunn/boot3>
- Bootloader-NanoKernel shim: <http://github.com/elliotnunn/wedge>

Some tools:

- Get data into and out of [HFS disk images](https://pypi.org/project/machfs) and [resource forks](https://pypi.org/project/macresources), robustly and portably
- Build software in the Mac emulator of your choice: http://github.com/elliotnunn/BuildCubeE
- Move resources around: <http://github.com/elliotnunn/zcp>
- Patch PowerPC binaries: <http://github.com/elliotnunn/patchpef>
- Patch 68k MPW code objects: <http://github.com/elliotnunn/patchobj>
- Extract 68k MPW code objects from a ROM: <https://github.com/elliotnunn/unlink>
- Graft a System Enabler onto a Mac OS ROM file: <https://github.com/elliotnunn/enablifier>
- Use my personal collection of hacky tools: <https://github.com/elliotnunn/ToolboxToolbox>

Most of our testing takes place on the [MacOS9Lives](http://macos9lives.com) forums. Technical discussion is mainly on the [mailing list](https://lists.ucc.gu.uwa.edu.au/mailman/listinfo/cdg5).
