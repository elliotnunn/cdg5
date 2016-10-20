Want to build the Mac OS ROM?

```
make "Mac OS ROM.hqx"
```

Remember BinHex? Me neither.

Want to explore the Nanokernel? After you do this, builds will assemble a new kernel from the .s file:

```
make kernel-disasm.s
```

Want to test it out? With QEMU 2.7.0 or later installed:

```
make test
```
