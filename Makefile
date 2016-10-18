export PATH := /usr/cross/powerpc-eabi/bin:$(HOME)/mac-project/toolboxtoolbox:$(PATH)

tbxi.hqx: tbxi-data tbxi-rsrc 
	binhexmake --data=tbxi-data --rsrc=tbxi-rsrc --type=tbxi --creator=chrp --name='Mac OS ROM' tbxi.hqx

tbxi-data tbxi-rsrc: boot rsrc-template datafork-pefs
	tbximake tbxi-data tbxi-rsrc boot rsrc-template datafork-pefs/NQDResidentCursor datafork-pefs/ProcessMgrLib

boot: chrp-boot-script MacOS.elf prcl
	bootmake --boot-script=chrp-boot-script --trampoline=MacOS.elf --parcels=prcl boot

prcl: prcl-pefs rom
	@echo making parcels... takes a while
	@prclmake prcl \
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
  --bin -f=00000005 -t='rom ' -n='' -l --src=rom   \
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

rom: rom-nokern kern
	cp rom-nokern rom; \
	dd if=kern of=rom conv=notrunc seek=3211264 bs=1

kern: kern.o
	powerpc-eabi-objcopy -O binary -j .text kern.o kern

kern.o: kern.asm
	powerpc-eabi-as -many -mregnames -o kern.o kern.asm


qemu-test.dd: FORCE tbxi.hqx
	rsync ../qemu-template.dd qemu-test.dd
	HOME=$$PWD hmount qemu-test.dd
	HOME=$$PWD hcopy -b tbxi.hqx 'QEMU HD:System Folder:'
	rm .hcwd

qemu: qemu-test.dd
	qemu-system-ppc -M mac99 -m 512 -prom-env 'auto-boot?=true' -g 800x600x32 -drive format=raw,media=disk,file=qemu-test.dd

upload: tbxi.hqx
	printf "open 192.168.0.6\nuser anonymous cdg5\ndelete tbxi.hqx\nput tbxi.hqx\ndelete \"System Folder\"/tbxi.hqx\nrename tbxi.hqx \"System Folder\"/tbxi.hqx\nclose\nexit\n" | ftp -n

clean:
	rm -f boot tbxi.hqx kern kern.o prcl rom tbxi-data tbxi-rsrc qemu-test.dd


FORCE:
