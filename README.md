# [EnumMSR](https://github.com/stfnw/enummsr)

This is a small experiment for enumerating all possible model-specific registers (MSRs) of a Intel CPU under Linux.
Disclaimer: This idea is of course nothing new and [has been done before much much better already](#existing-tools).

*For educational purposes only.*


## How To Run

```
$ # sudo apt install -y build-essential linux-headers-amd64
$ sudo pacman -S base-devel linux-headers
...


$ # watch output
$ sudo dmesg -w

$ make test
make -C /lib/modules/6.9.8-arch1-1/build M=EnumMSR modules
make[1]: Entering directory '/usr/lib/modules/6.9.8-arch1-1/build'
  CC [M]  EnumMSR/enum-msr.o
  MODPOST EnumMSR/Module.symvers
  CC [M]  EnumMSR/enum-msr.mod.o
  LD [M]  EnumMSR/enum-msr.ko
  BTF [M] EnumMSR/enum-msr.ko
make[1]: Leaving directory '/usr/lib/modules/6.9.8-arch1-1/build'
sudo insmod enum-msr.ko
```


## What this does and how it works

Model-specific registers (MSRs) are CPU-specific additional registers.[^1][^2]
They "control functions for testability, execution tracing, performance-monitoring, and machine check errors."[^2]
This includes for example Intel VTx -- Intels instruction set extension for hardware-assisted virtualization.

[^1]: Intel® 64 and IA-32 Architectures Software Developer's Manual:
      https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html
      All references here use Intel® 64 and IA-32 Architectures Software Developer’s Manual Combined Volumes: 1, 2A, 2B, 2C, 2D, 3A, 3B, 3C, 3D, and 4; Order Number: 325462-084US; June 2024

[^2]: Volume 2B Instruction Set Reference, M-U: RDMSR—Read From Model Specific Register

MSRs can be read with the RDMSR instruction, which returns the value of the MSR specified in ECX (high-order 32 bits of RCX are ignored).
That means that there are in total $2^{32}$ different possible MSRs (from 0x00000000 to 0xFFFFFFFF).
This program iterates through this integer range and tries to read from the corresponding MSR;
if the read succeeds, this is taken as indication that an MSR with the respective id exists:[^2]

> This [RDMSR] instruction must be executed at privilege level 0 or in real-address mode;
> otherwise, a general protection exception #GP(0) will be generated.
> Specifying a reserved or unimplemented MSR address in ECX will also cause a general protection exception.

Since RDMSR (and its correspondent WRMSR) as a privileged instruction must be run in kernel mode (CPL 0), this tools is implemented as a Linux kernel module.
The naive approach would be simply iterating and issuing RDMSR using inline assembly.
The problem with this is exception handling: the general protection fault would crash the code.
One possible solution would be to hook the interrupt descriptor table (IDT) manually and overwrite the corresponding interrupt handler to prevent a crash of the code.
Fortunately, this is not necessary since it already has been implemented in Linux in the wrapper function `rdmsrl_safe` in `arch/x86/include/asm/msr.h`,
which handles possibly occurring exceptions and exposes whether or not a GP occurred as the returned error code.

Volume 4[^3] of the manual lists all documented MSRs (this is specific to each processor family).

[^3]: Volume 4: Model-specific Registers: Chapter 2: Model-Specific Registers (MSRs)


## Results

After running the program on various laptops I tried to compare the identified MSRs with the documented ones to maybe identify potentially interesting undocumented MSRs.
Documented MSRs have been extracted from the previously referenced manual Volume 4 using [the script `extract-documented-msrs.py`](extract-documented-msrs.py).

Overall conclusion: for the CPUs in the laptops I had laying around, there seem to be many undocumented MSR available.
This surprised me; I didn't expect that.
Some that are not mentioned in Volume 4 at all are: (note that there could very well be false positive if a presented format in the PDF isn't handled correctly by the scirpt).

0x00000020,
0x00000021,
0x00000022,
0x00000023,
0x0000002E,
0x0000003E,
0x00000059,
0x00000095,
0x000000B9,
0x00000102,
0x00000103,
0x00000104,
0x00000110,
0x0000011F,
0x00000121,
0x00000132,
0x00000133,
0x00000134,
0x0000013A,
0x0000013D,
0x00000150,
0x000001A8,
0x000001C6,
0x000001E1,
0x000001F0,
0x000002E0,
0x000002E7,
0x00000397,
0x00000502,
0x00000503,
0x00000602,
0x00000603,
0x00000604,
0x00000607,
0x00000608,
0x00000609,
0x00000615,
0x0000061D,
0x00000621,
0x00000622,
0x00000623,
0x00000633,
0x00000634,
0x00000635,
0x00000636,
0x00000637,
0xC0010000,
0xC0010001,
0xC0010002,
0xC0010003,
0xC0010004,
0xC0010005,
0xC0010006,
0xC0010007,
0xC0010010,
0xC0010015,
0xC001001B,
0xC001001F,
0xC0010055,
0xC0010058,
0xC0010112,
0xC0010113,
0xC0010117,
0xC0011022,
0xC0011023,
0xC001102A,
0xC001102C

Out of those, the following ones were readable *and* writable:

0x0000002E,
0x0000003E,
0x00000095,
0x00000102,
0x00000103,
0x00000104,
0x0000011F,
0x0000013D,
0x00000150,
0x000001A8,
0x000002E7,
0x00000397,
0x00000503,
0x00000603,
0x00000607,
0x00000608,
0x00000609,
0x00000615,
0x00000622,
0x00000633,
0x00000634,
0x00000635,
0x00000636


# Existing tools

Note, that e.g. this repo https://github.com/rizerev/msrs and the associated bachelor thesis "MSRS - an LKM to Find Undocumented MSRs on x86_64" implements this approach better and more complete and also incorporates analysis about register values and functions.
Relevant are also [the corresponding paper](https://ieeexplore.ieee.org/document/9833599) and [implementation](https://github.com/IAIK/msrevelio).
It is a very interesting read.

[This research from 2018](https://www.blackhat.com/us-18/briefings/schedule/#god-mode-unlocked---hardware-backdoors-in-x86-cpus-10194) is also very good.

Of course there is most likely also other research I missed that also does this.
