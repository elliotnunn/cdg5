# mount our current dir as /work in the container, and cd /work
# --rm means don't keep this container after command is done
# we are always root inside the container, but stay ourself outside
# next arg should be the image to use (e.g. elliotnunn/toolboxtools)
# then the next one should be the command to run
DOCKER=docker run --volume="$$PWD":/work --workdir=/work --env=HOME=/work --user=$(shell id -u):$(shell id -g) --rm

# If there is a disassembled kernel (possibly edited) then use it. If not, use the stock kernel.
ifeq ($(wildcard kernel-disasm.s),)
	KERNEL=kernel-stock
else
	KERNEL=kernel-built
endif

# We want these to re-run every time they are required
.PHONY: test-boot.img kernel-disasm.s kernel-revert-to-stock test clean

Mac\ OS\ ROM.hqx: tbxi-data tbxi-rsrc 
	$(DOCKER) elliotnunn/toolboxtools binhexmake --data=tbxi-data --rsrc=tbxi-rsrc --type=tbxi --creator=chrp --name='Mac OS ROM' 'Mac OS ROM.hqx'

tbxi-data tbxi-rsrc: base-tbxi rsrc-template datafork-pefs
	$(DOCKER) elliotnunn/toolboxtools tbximake tbxi-data tbxi-rsrc base-tbxi rsrc-template datafork-pefs/NQDResidentCursor datafork-pefs/ProcessMgrLib

base-tbxi: boot-script trampoline.elf prcl
	$(DOCKER) elliotnunn/toolboxtools bootmake --boot-script=boot-script --trampoline=trampoline.elf --parcels=prcl base-tbxi

PowerROM: PowerROM-nokern $(KERNEL)
	cp PowerROM-nokern "$@"
	dd if=$(KERNEL) of="$@" conv=notrunc seek=3211264 bs=1

kernel-built: kernel-built.o
	$(DOCKER) elliotnunn/powerpc-binutils objcopy -O binary -j .text "$<" "$@"

# Don't declare kernel-disasm.s as a dep because we only ever want to remake it manually
kernel-built.o:
	$(DOCKER) elliotnunn/powerpc-binutils as -many -mregnames --nops=2 -o "$@" kernel-disasm.s

kernel-disasm.s: kernel-stock
	$(DOCKER) elliotnunn/powerpc-disasm python kernel-disasm-script.py --disasm "$@" "$<"

# PowerROM is likely tainted by the rebuilt kernel. Kill.
kernel-revert-to-stock:
	rm -f kernel-disasm.s PowerROM

# hfsutils rather annoyingly stores state in $HOME/.hcwd, so we put it here instead
# The rsync allows us to leave the destination read-write in qemu
test-boot.img: Mac\ OS\ ROM.hqx
	rsync test-template.img "$@"
	$(DOCKER) elliotnunn/hfsutils hmount "$@"
	$(DOCKER) elliotnunn/hfsutils hcopy -b 'Mac OS ROM.hqx' 'QEMU HD:System Folder:'
	rm .hcwd

test: test-boot.img
	qemu-system-ppc -M mac99 -m 512 -prom-env 'auto-boot?=true' -g 800x600x32 -drive format=raw,media=disk,file="$<"

clean:
	rm -f .hcwd base-tbxi 'Mac OS ROM.hqx' kernel-built kernel-built.o prcl PowerROM tbxi-data tbxi-rsrc test-boot.img

prcl: prcl-pefs PowerROM
	@echo making parcels... takes a while
	@$(DOCKER) elliotnunn/toolboxtools prclmake prcl \
--prcl -f=00020000 -t=node -n='CodePrepare Node Parcel' -c=''   \
	--bin -f=00000000 -t=cstr -n=name --data AAPL,CodePrepare   \
	--bin -f=00000000 -t=csta -n=AAPL,prepare_order --data Placeholder   \
	--bin -f=00020094 -t=nlib -n=TimeManagerLib -l --src=prcl-pefs/CodePrepare_TimeManagerLib   \
	--bin -f=00020094 -t=nlib -n=NVRAMServicesLib -l --src=prcl-pefs/CodePrepare_NVRAMServicesLib   \
	--bin -f=00020094 -t=nlib -n=RTCServicesLib -l --src=prcl-pefs/CodePrepare_RTCServicesLib   \
\
--prcl -f=00010000 -t=node -n='CodeRegister Node Parcel' -c=''   \
	--bin -f=00000000 -t=cstr -n=name --data AAPL,CodeRegister   \
	--bin -f=00010094 -t=nlib -n=NativePowerMgrLib -l --src=prcl-pefs/CodeRegister_NativePowerMgrLib   \
	--bin -f=00010094 -t=nlib -n=AGPLib -l --src=prcl-pefs/CodeRegister_AGPLib   \
	--bin -f=00010194 -t=nlib -n=EtherPrintfLib -l --src=prcl-pefs/CodeRegister_EtherPrintfLib   \
	--bin -f=00010094 -t=shlb -n=StartLib -l --src=prcl-pefs/CodeRegister_StartLib   \
\
--prcl -f=00000000 -t='rom ' -n='Mac OS ROM Parcel' -c=''   \
	--bin -f=00000005 -t='rom ' -n='' -l --src=PowerROM   \
\
--prcl -f=00000000 -t=psum -n='Property Checksum' -c=''   \
	--bin -f=00000000 -t=csta -n='' --data name model compatible device_type reg assigned-addresses slot-names vendor-id device-id class-code devsel-speed fast-back-to-back bootpath mac-address   \
	--bin -f=00000000 -t=csta -n='' --data boot-rom macos   \
	--bin -f=00000000 -t=csta -n='' --data Placeholder   \
	--bin -f=00000000 -t=csta -n='' --data Placeholder   \
	--bin -f=00000000 -t=csta -n='' --data usb ieee1394   \
\
--prcl -f=0000000c -t=prop -n=apple21143 -c=network   \
	--bin -f=00000006 -t=shlb -n=lanLib,AAPL,MacOS,PowerPC -l --src=prcl-pefs/lanLib_apple21143   \
\
--prcl -f=00000009 -t=prop -n=backlight -c=backlight   \
	--bin -f=00000000 -t=ndrv -n=driver,AAPL,MacOS,PowerPC --src=prcl-pefs/BacklightDriver   \
	--bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data BacklightDriver   \
\
--prcl -f=0000000c -t=prop -n=bmac+ -c=network   \
	--bin -f=00000006 -t=shlb -n=lanLib,AAPL,MacOS,PowerPC -l --src=prcl-pefs/lanLib_bmac+   \
\
--prcl -f=0000000c -t=prop -n=cmd646-ata -c=ata   \
	--bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ATA_CMD646_driver   \
\
--prcl -f=00000008 -t=prop -n=cofb -c=display   \
	--bin -f=00000024 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/Display_driver   \
\
--prcl -f=0000000c -t=prop -n=cuda -c=via-cuda   \
	--bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin_CUDA   \
	--bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
\
--prcl -f=0000000c -t=prop -n=gmac -c=network   \
	--bin -f=00000006 -t=shlb -n=lanLib,AAPL,MacOS,PowerPC -l --src=prcl-pefs/lanLib_gmac   \
\
--prcl -f=0000000c -t=prop -n=grackle -c=pci   \
	--bin -f=00000016 -t=nlib -n=pef,AAPL,MacOS,PowerPC,prepare -l --src=prcl-pefs/PCICyclesLib_Grackle   \
	--bin -f=00000000 -t=cstr -n=code,AAPL,MacOS,name --data Grackle_PCICyclesLib   \
\
--prcl -f=0000000c -t=prop -n=heathrow-ata -c=ide   \
	--bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ATA_Heathrow_driver   \
\
--prcl -f=0000000c -t=prop -n=heathrow-ata -c=ata   \
	--bin -f=00000002 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ATA_Heathrow_driver   \
\
--prcl -f=0000000c -t=prop -n=kauai-ata -c=ata   \
	--bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ATA_Kauai_driver   \
\
--prcl -f=0000000c -t=prop -n=keylargo-ata -c=ata   \
	--bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ATA_KeyLargo_driver   \
\
--prcl -f=0000000c -t=prop -n=keywest-i2c -c=i2c   \
	--bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/I2C_driver   \
\
--prcl -f=0000000a -t=prop -n=mac-io -c=nvram   \
	--bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/NVRAM_mac-io_driver   \
\
--prcl -f=00000001 -t=prop -n=macos -c=''   \
	--bin -f=00000000 -t=cstr -n=MacOSROMFile-version --data 9.6f1   \
\
--prcl -f=0000000c -t=prop -n=nvram,flash -c=nvram   \
	--bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/NVRAM_flash_driver   \
\
--prcl -f=0000000c -t=prop -n=pci104c,ac1a -c=cardbus   \
	--bin -f=00000016 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/CardBus_driver   \
	--bin -f=00010094 -t=nlib -n=PCCard -l --src=prcl-pefs/CardBus_PCCard_lib   \
\
--prcl -f=0000000c -t=prop -n=pci104c,ac50 -c=cardbus   \
	--bin -f=00000016 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/CardBus_driver   \
	--bin -f=00010094 -t=nlib -n=PCCard -l --src=prcl-pefs/CardBus_PCCard_lib   \
\
--prcl -f=0000020c -t=prop -n=pciclass,0c0010 -c=ieee1394   \
	--bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/FireWire_driver   \
	--bin -f=00010096 -t=nlib -n=FWServicesLib -l --src=prcl-pefs/FireWire_FWServicesLib   \
	--bin -f=00010096 -t=nlib -n=DevNLib -l --src=prcl-pefs/FireWire_DevNLib   \
	--bin -f=00010096 -t=nlib -n=DFMLib -l --src=prcl-pefs/FireWire_DFMLib   \
	--bin -f=00010096 -t=nlib -n=GenericDriverFamily -l --src=prcl-pefs/FireWire_GenericDriverFamily   \
\
--prcl -f=0000000c -t=prop -n=pmu -c=power-mgt   \
	--bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin_PMU   \
	--bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
	--bin -f=00000002 -t=cstr -n=target-mode-capable --data SCSI   \
	--bin -f=00010096 -t=nlib -n=PMULib -l --src=prcl-pefs/PMULib   \
\
--prcl -f=0000000c -t=prop -n=uni-n-i2c -c=i2c   \
	--bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/I2C_driver   \
\
--prcl -f=0000000c -t=prop -n=uni-north -c=pci   \
	--bin -f=00000016 -t=nlib -n=pef,AAPL,MacOS,PowerPC,prepare -l --src=prcl-pefs/PCICyclesLib_UniNorth   \
	--bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data UniNorth_PCICyclesLib   \
\
--prcl -f=0000000a -t=prop -n=via-cuda -c=rtc   \
	--bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/RTC_CUDA_driver   \
\
--prcl -f=0000000a -t=prop -n=via-pmu -c=nvram   \
	--bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/NVRAM_PMU_driver   \
\
--prcl -f=0000000a -t=prop -n=via-pmu -c=rtc   \
	--bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/RTC_PMU_driver   \
\
--prcl -f=0000000c -t=prop -n=via-pmu-2000 -c=power-mgt   \
	--bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin_PMU2000   \
	--bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
	--bin -f=00010096 -t=nlib -n=PMULib -l --src=prcl-pefs/PMULib   \
\
--prcl -f=0000000c -t=prop -n=via-pmu-99 -c=power-mgt   \
	--bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin_PMU99   \
	--bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
	--bin -f=00010096 -t=nlib -n=PMULib -l --src=prcl-pefs/PMULib
