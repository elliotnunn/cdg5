Want to build the Mac OS ROM? Start with a working Docker.

```
make "Mac OS ROM.hqx"
```

Want to explore the Nanokernel? After you do this, builds will assemble a new kernel from the .s file:

```
make kernel-disasm.s
```

And to revert to building with the stock nanokernel:

```
make kernel-revert-to-stock
```

With QEMU 2.7.0 or later installed:

```
make test
```

To see the kernel log: look for `uncomment to debug` in `boot-script`. To change its colour, look at the very end of your `kernel-disasm.s`.