export PATH := /usr/cross/powerpc-eabi/bin:$(HOME)/mac-project/toolboxtoolbox:$(PATH)

copy: tbxi.hqx
	scp tbxi.hqx sweetpotato.local:$(HOME)/macstuff/

tbxi.hqx: tbxi-data tbxi-rsrc 
	binhexmake --data=tbxi-data --rsrc=tbxi-rsrc --type=tbxi --creator=chrp --name='Mac OS ROM' tbxi.hqx

tbxi-data tbxi-rsrc: boot rsrc-template datafork-pefs
	tbximake tbxi-data tbxi-rsrc boot rsrc-template datafork-pefs/NQDResidentCursor datafork-pefs/ProcessMgrLib

boot: chrp-boot-script MacOS.elf prcl
	bootmake --boot-script=chrp-boot-script --trampoline=MacOS.elf --parcels=prcl boot

prcl: prcl-pefs rom
	@prclmake prcl \
--prcl -f=00020000 -t=node -n='CodePrepare Node Parcel' -c=''   \
  --bin -f=00000000 -t=cstr -n=name --data AAPL,CodePrepare   \
  --bin -f=00000000 -t=csta -n=AAPL,prepare_order --data Placeholder   \
  --bin -f=00020094 -t=nlib -n=TimeManagerLib -l --src=prcl-pefs/TimeManagerLib@CodePrepare   \
  --bin -f=00020094 -t=nlib -n=NVRAMServicesLib -l --src=prcl-pefs/NVRAMServicesLib@CodePrepare   \
  --bin -f=00020094 -t=nlib -n=RTCServicesLib -l --src=prcl-pefs/RTCServicesLib@CodePrepare   \
\
--prcl -f=00010000 -t=node -n='CodeRegister Node Parcel' -c=''   \
  --bin -f=00000000 -t=cstr -n=name --data AAPL,CodeRegister   \
  --bin -f=00010094 -t=nlib -n=NativePowerMgrLib -l --src=prcl-pefs/NativePowerMgrLib@CodeRegister   \
  --bin -f=00010094 -t=nlib -n=AGPLib -l --src=prcl-pefs/AGPLib@CodeRegister   \
  --bin -f=00010194 -t=nlib -n=EtherPrintfLib -l --src=prcl-pefs/EtherPrintfLib@CodeRegister   \
  --bin -f=00010094 -t=shlb -n=StartLib -l --src=prcl-pefs/StartLib@CodeRegister   \
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
  --bin -f=00000006 -t=shlb -n=lanLib,AAPL,MacOS,PowerPC -l --src=prcl-pefs/lanLib@apple21143:network   \
\
--prcl -f=00000009 -t=prop -n=backlight -c=backlight   \
  --bin -f=00000000 -t=ndrv -n=driver,AAPL,MacOS,PowerPC --src=prcl-pefs/ndrv@backlight:backlight   \
  --bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data BacklightDriver   \
\
--prcl -f=0000000c -t=prop -n=bmac+ -c=network   \
  --bin -f=00000006 -t=shlb -n=lanLib,AAPL,MacOS,PowerPC -l --src=prcl-pefs/lanLib@bmac+:network   \
\
--prcl -f=0000000c -t=prop -n=cmd646-ata -c=ata   \
  --bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@cmd646-ata:ata   \
\
--prcl -f=00000008 -t=prop -n=cofb -c=display   \
  --bin -f=00000024 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@cofb:display   \
\
--prcl -f=0000000c -t=prop -n=cuda -c=via-cuda   \
  --bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin@cuda:via-cuda   \
  --bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
\
--prcl -f=0000000c -t=prop -n=gmac -c=network   \
  --bin -f=00000006 -t=shlb -n=lanLib,AAPL,MacOS,PowerPC -l --src=prcl-pefs/lanLib@gmac:network   \
\
--prcl -f=0000000c -t=prop -n=grackle -c=pci   \
  --bin -f=00000016 -t=nlib -n=pef,AAPL,MacOS,PowerPC,prepare -l --src=prcl-pefs/PCICyclesLib@grackle:pci   \
  --bin -f=00000000 -t=cstr -n=code,AAPL,MacOS,name --data Grackle_PCICyclesLib   \
\
--prcl -f=0000000c -t=prop -n=heathrow-ata -c=ide   \
  --bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src='prcl-pefs/ndrv@heathrow-ata:ata|ide'   \
\
--prcl -f=0000000c -t=prop -n=heathrow-ata -c=ata   \
  --bin -f=00000002 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src='prcl-pefs/ndrv@heathrow-ata:ata|ide'   \
\
--prcl -f=0000000c -t=prop -n=kauai-ata -c=ata   \
  --bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@kauai-ata:ata   \
\
--prcl -f=0000000c -t=prop -n=keylargo-ata -c=ata   \
  --bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@keylargo-ata:ata   \
\
--prcl -f=0000000c -t=prop -n=keywest-i2c -c=i2c   \
  --bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src='prcl-pefs/ndrv@keywest-i2c|uni-n-i2c:i2c'   \
\
--prcl -f=0000000a -t=prop -n=mac-io -c=nvram   \
  --bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@mac-io:nvram   \
\https://github.com/elliotnunn/toolboxtoolbox
--prcl -f=00000001 -t=prop -n=macos -c=''   \
  --bin -f=00000000 -t=cstr -n=MacOSROMFile-version --data 9.6f1   \
\
--prcl -f=0000000c -t=prop -n=nvram,flash -c=nvram   \
  --bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@nvram,flash:nvram   \
\
--prcl -f=0000000c -t=prop -n=pci104c,ac1a -c=cardbus   \
  --bin -f=00000016 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src='prcl-pefs/ndrv@pci104c,ac1a|pci104c,ac50:cardbus'   \
  --bin -f=00010094 -t=nlib -n=PCCard -l --src='prcl-pefs/PCCard@pci104c,ac1a|pci104c,ac50:cardbus'   \
\
--prcl -f=0000000c -t=prop -n=pci104c,ac50 -c=cardbus   \
  --bin -f=00000016 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src='prcl-pefs/ndrv@pci104c,ac1a|pci104c,ac50:cardbus'   \
  --bin -f=00010094 -t=nlib -n=PCCard -l --src='prcl-pefs/PCCard@pci104c,ac1a|pci104c,ac50:cardbus'   \
\
--prcl -f=0000020c -t=prop -n=pciclass,0c0010 -c=ieee1394   \
  --bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@pciclass,0c0010:ieee1394   \
  --bin -f=00010096 -t=nlib -n=FWServicesLib -l --src=prcl-pefs/FWServicesLib@pciclass,0c0010:ieee1394   \
  --bin -f=00010096 -t=nlib -n=DevNLib -l --src=prcl-pefs/DevNLib@pciclass,0c0010:ieee1394   \
  --bin -f=00010096 -t=nlib -n=DFMLib -l --src=prcl-pefs/DFMLib@pciclass,0c0010:ieee1394   \
  --bin -f=00010096 -t=nlib -n=GenericDriverFamily -l --src=prcl-pefs/GenericDriverFamily@pciclass,0c0010:ieee1394   \
\
--prcl -f=0000000c -t=prop -n=pmu -c=power-mgt   \
  --bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin@pmu:power-mgt   \
  --bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
  --bin -f=00000002 -t=cstr -n=target-mode-capable --data SCSI   \
  --bin -f=00010096 -t=nlib -n=PMULib -l --src='prcl-pefs/PMULib@pmu|via-pmu-2000|via-pmu-99:power-mgt'   \
\
--prcl -f=0000000c -t=prop -n=uni-n-i2c -c=i2c   \
  --bin -f=00000006 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src='prcl-pefs/ndrv@keywest-i2c|uni-n-i2c:i2c'   \
\
--prcl -f=0000000c -t=prop -n=uni-north -c=pci   \
  --bin -f=00000016 -t=nlib -n=pef,AAPL,MacOS,PowerPC,prepare -l --src=prcl-pefs/PCICyclesLib@uni-north:pci   \
  --bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data UniNorth_PCICyclesLib   \
\
--prcl -f=0000000a -t=prop -n=via-cuda -c=rtc   \
  --bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@via-cuda:rtc   \
\
--prcl -f=0000000a -t=prop -n=via-pmu -c=nvram   \
  --bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@via-pmu:nvram   \
\
--prcl -f=0000000a -t=prop -n=via-pmu -c=rtc   \
  --bin -f=00000004 -t=ndrv -n=driver,AAPL,MacOS,PowerPC -l --src=prcl-pefs/ndrv@via-pmu:rtc   \
\
--prcl -f=0000000c -t=prop -n=via-pmu-2000 -c=power-mgt   \
  --bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin@via-pmu-2000:power-mgt   \
  --bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
  --bin -f=00010096 -t=nlib -n=PMULib -l --src='prcl-pefs/PMULib@pmu|via-pmu-2000|via-pmu-99:power-mgt'   \
\
--prcl -f=0000000c -t=prop -n=via-pmu-99 -c=power-mgt   \
  --bin -f=00000000 -t=ndrv -n=pef,AAPL,MacOS,PowerPC,register -l --src=prcl-pefs/PowerMgrPlugin@via-pmu-99:power-mgt   \
  --bin -f=00000002 -t=cstr -n=code,AAPL,MacOS,name --data PowerMgrPlugin   \
  --bin -f=00010096 -t=nlib -n=PMULib -l --src='prcl-pefs/PMULib@pmu|via-pmu-2000|via-pmu-99:power-mgt'

rom: rom-nokern kern
	cp rom-nokern rom; \
	dd if=kern of=rom conv=notrunc seek=3211264 bs=1

kern: kern.o
	powerpc-eabi-objcopy -O binary -j .text kern.o kern

kern.o: kern.asm
	powerpc-eabi-as -many -mregnames -o kern.o kern.asm

clean:
	rm boot tbxi.hqx kern kern.o prcl rom tbxi-data tbxi-rsrc





qemu: qemu-test.img
	qemu-system-ppc -M mac99 -m 128 -prom-env 'auto-boot?=true' -g 800x837x32 -drive readonly,format=raw,media=disk,file=qemu-test.img
