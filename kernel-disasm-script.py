#!/usr/bin/env python3

import disasm as da
from sys import argv
from os import path
from functools import partial
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('SRC', help='probably called 02.28')
parser.add_argument('--disasm', action='store',  metavar='DEST', help='put in cdg5/kern.asm!')
parser.add_argument('--dump-constants', action='store', metavar='DEST')

cmdline = parser.parse_args()


#
# READ THE KERNEL
#

with open(cmdline.SRC, 'rb') as f:
    p = da.Project(f.read())


#
# Data structures that I know about
#

# TLAs:
# KDP = kernel data page
# EDP = emulator data page
# EWA = exception working area?
# IRP = interrupt *response* page?

# 0x564 : 0x6e0 (the end) is code!
# some of this info from SheepShaver, so possibly dodgy
p.struct('ConfigInfo', {
    0x008: 'bl_fffff93c',
    0x024: 'bl_fffff93c',
    0x040: 'bl_fffff93c_from_start',
    0x044: 'DiagPEFBundleOffset',
    0x04c: 'KernelCodeOffset',
    0x05c: 'OpcodeTableOffset_bl_fffff93c', # replaced in NKv2?
    0x064: 'rom_version_string_16char',
    0x078: '00000100',
    0x080: 'emu_offset_80',
    0x084: 'emu_offset_e8c0',
    0x098: 'u8_pih_kind',
    0x09c: 'logi_InfoRecord',        # 5fffe000
    0x0a0: 'logi_KernelData',        # 68ffe000
    0x0a4: 'logi_EmulatorData',      # 68fff000
    0x0a8: 'logi_DispatchTable',     # 68080000
    0x0ac: 'logi_EmulatorCode',      # 68060000
    0x35c: '40820160',
    0x360: 'phys_ram_base',
    0xfd8: '68k_reset_vector', # out of range of struct
})

p.struct('sys_info', {
    0x00: 'u32_ram_size',
    0x2c: 'phys_toolboxrom',
})

p.struct('hw_info', {
    0x038: 'rtas_private_data',
})

p.struct('irp', {
    0xdc0: 'phys_ram',
    0xf00: 'irp_start',
})

p.struct('kdp', {
    -0xb90: 'htab_lock',
    -0xb70: 'pih_lock',
    -0xb50: 'sch_lock',
    -0xb30: 'thud_lock',
    -0xb10: 'rtas_lock',
    -0xaf0: 'dbug_lock',
    -0xad0: 'pool_lock',

    -0x41c: 'system_address_space',
    -0x360: 'uint16_log_window_y',
    -0x35e: 'uint16_log_window_x',
    -0x35c: 'uint16_log_window_height',
    -0x35a: 'uint16_log_window_width',
    -0x020: 'irp',
    0x288: 'bat0l',
    0x28c: 'bat0u',
    0x298: 'bat1l',
    0x29c: 'bat1u',
    0x2a8: 'bat2l',
    0x2ac: 'bat2u',
    0x2b8: 'bat3l',
    0x2bc: 'bat3u',
    0x5b0: 'pih_proc_ptr',
    0x630: 'pa_ConfigInfo',
    0x634: 'pa_edp',
    0x640: 'phys_ram_base',
    0x644: 'configinfo_40820160',
    0x64c: 'phys_kern_base',
    0x648: 'emu_e8c0',
    0x650: 'phys_funny_debug_place',
    0x658: 'system_context',
    0x6a8: 'phys_pages',
    0x6ac: 'logi_pages',
    0x6b4: 'VMMaxVirtualPages',
    0xb50: 'big_lock',
    0x908: 'rtas_proc', # 'RTAS' or 0
    0x90c: 'rtas_private_data',
    0xec4: 'blue_task',

    # start of processor_info
    0xf20: 'u32_pvr',
    0xf24: 'u32_cpu_clock_freq',
    0xf28: 'u32_bus_freq',
    0xf2c: 'u32_timebase_freq',
    # below here gets overwritten on old cpus
    0xf30: 'u32_cpuinfo_page_size',
    0xf34: 'u32_cpuinfo_dcache_size',
    0xf38: 'u32_cpuinfo_icache_size',
    0xf3c: 'u16_cpuinfo_coherency_block_size',
    0xf3e: 'u16_cpuinfo_reservation_granule_size',
    0xf40: 'u16_cpuinfo_unified_caches',
    0xf42: 'u16_cpuinfo_icache_line_size',
    0xf44: 'u16_cpuinfo_dcache_line_size',
    0xf46: 'u16_cpuinfo_dcache_block_size_touch',
    0xf48: 'u16_cpuinfo_icache_block_size',
    0xf4a: 'u16_cpuinfo_dcache_block_size',
    0xf4c: 'u16_cpuinfo_icache_assoc',
    0xf4e: 'u16_cpuinfo_dcache_assoc',
    0xf50: 'u16_cpuinfo_tlb_size',
    0xf52: 'u16_cpuinfo_tlb_assoc',
    # </overwritten>
    # 108 bytes yet unaccounted for ... 0xfc0
    # but in Trampoline processor info, mostly empty
    # Probably related to L2 cache.
    # end of processor_info

    0xfe4: 'u16_version',
    
    0x1184: 'la_emulator_entry',
    0x119c: 'la_opcode_tbl',
})

p.struct('ewa', { # same as a system context!
    -0xb90: 'psa', # what's a PSA?
    -0x340: 'cpu_id',
    -0x338: 'sch_info_struct',
    -0x116: 'cpu_which',
    -0x01c: 'address_space_struct',
    -0x008: 'cur_task_struct',
    0x0d4: 'xer',
})

p.struct('task', {
    0x00: 'id',
    0x60: 'owning_process_id',
    0x6c: 'owning_process_struct',
    0x74: 'fourcc',
})

p.struct('addrspc', {
    0x00: 'id',
})

p.struct('lock', {
    0x00: 'count',
    0x04: 'fourcc',
    0x10: 'holder',
})

# Strings (and sometimes arrays) between a bl and an mflr are common
#
# An alternative way to customise control flow is to add an edge before disassembly.
#

blrls_with_data = [
    0x17678,
    0x19018,
    0x19058,
    0x190a0,
    0x19ab0,
    0x19b00,
    0x19b20,
]

returned_blrls = [
    0x0665c,
    0x00bcc,
    0x00c08,
    0x00c58,
    0x00cb0,
    0x00d14,
    0x00d90,
    0x00da8,
    0x00e60,
    0x00e9c,
    0x00f88,
    0x010b8,
    0x010c4,
    0x048ac,
]

def bl_literals(insn):
    if insn.mnemonic == 'blrl':
        if insn.address in blrls_with_data:
            return False
        elif insn.address in returned_blrls:
            return True
        else:
            return False
    
    if 'lr' in insn.mnemonic or 'ctr' in insn.mnemonic:
        return False
    
    # Try something different:
    data_start = insn.address + insn.size
    data_end = insn.operands[-1].imm

    if p.data[data_end] >> 2 != 0x1f: return True

    if not 4 <= (data_end - data_start) < 80: return True

    data = p.data[data_start : data_end]
    if b'\x60\x00\x00\x00' in data: return True
    if b'\0' not in data[::4] and not data.endswith(b'\0\0'): return True
    
    p.label(data_end, '1')

    # String literal?
    if b'\0' not in data.rstrip(b'\0') and data.endswith(b'\0\0'):
        nul_stripped = data.rstrip(b'\0')
        str_end = data_start + len(nul_stripped)

        for i in range(data_start, data_end):
            p.semantic_list[i] = None
        p._insert_semantic(da._SemanticString(data_start, nul_stripped))
        p._insert_semantic(da._SemanticFixedSize(str_end, b'\0\0'))
    
    return False

p.linkreg_data_checker = bl_literals


#
# Boot entry point
#
p.flow_graph.add_edge('boot_newworld', 0x00000, obj=da._FlowEdge())
p.flow_graph.add_edge('boot_oldworld', 0x00040, obj=da._FlowEdge())
p.flow_graph.add_edge('temp', 0x08804, obj=da._FlowEdge())

p.flow_graph.add_edge(0x0003c, 'ConfigInfo.bl_fffff93c_from_start', obj=da._FlowEdge())


#
# This is pretty messy, because it needs to be done before disassembly time.
#

lisori_caller_name = 'lisori_caller'

lisori_offsets_and_callers = [
    # Earliest lisoris
    (0x000e8, [lisori_caller_name, ]),
    (0x00810, [lisori_caller_name, ]),

    # To functions from setup
    (0x01394, [lisori_caller_name, ]),
    (0x013a4, [lisori_caller_name, ]),
    (0x014e8, [lisori_caller_name, ]),
    (0x01530, [lisori_caller_name, ]),
    (0x01554, [lisori_caller_name, ]),
    (0x01568, [lisori_caller_name, ]),
    (0x0157c, [lisori_caller_name, ]),
    (0x01590, [lisori_caller_name, ]),
    (0x015a4, [lisori_caller_name, ]),
    (0x015b4, [lisori_caller_name, ]),
    (0x015c4, [lisori_caller_name, ]),
    (0x015d8, [lisori_caller_name, ]),
    (0x015ec, [lisori_caller_name, ]),
    (0x01600, [lisori_caller_name, ]),
    (0x01614, [lisori_caller_name, ]),
    (0x01628, [lisori_caller_name, ]),
    (0x0163c, [lisori_caller_name, ]),
    (0x01658, [lisori_caller_name, ]),
    (0x0166c, [lisori_caller_name, ]),
    (0x01684, [lisori_caller_name, ]),
    (0x01694, [lisori_caller_name, ]),
    (0x016a4, [lisori_caller_name, ]),
    (0x016b4, [lisori_caller_name, ]),
    (0x016c4, [lisori_caller_name, ]),
    (0x016dc, [lisori_caller_name, ]),
    (0x016ec, [lisori_caller_name, ]),
    (0x016fc, [lisori_caller_name, ]),
    (0x0170c, [lisori_caller_name, ]),
    (0x01724, [lisori_caller_name, ]),
    (0x01734, [lisori_caller_name, ]),
    (0x01744, [lisori_caller_name, ]),
    (0x01754, [lisori_caller_name, ]),
    (0x01764, [lisori_caller_name, ]),
    (0x01784, [lisori_caller_name, ]),
    (0x01794, [lisori_caller_name, ]),
    (0x017a4, [lisori_caller_name, ]),
    (0x017b4, [lisori_caller_name, ]),
    (0x017c4, [lisori_caller_name, ]),
    (0x017d4, [lisori_caller_name, ]),
    (0x017e4, [lisori_caller_name, ]),
    (0x017f4, [lisori_caller_name, ]),
    (0x01804, [lisori_caller_name, ]),
    (0x01814, [lisori_caller_name, ]),
    (0x01f04, [lisori_caller_name, ]),

    # And the rest
    (0x0687c, [lisori_caller_name, ]),
    (0x07658, [lisori_caller_name, ]),
    (0x0795c, [lisori_caller_name, ]),
    (0x07a88, [lisori_caller_name, ]),
    (0x07d10, []),
    (0x07dac, []),
    (0x08788, []),
    (0x08794, []),
    #(0x098f4, [lisori_caller_name, ]),
    (0x09ce4, [lisori_caller_name, ]),
    (0x09d00, [lisori_caller_name, ]),
    (0x0aef4, []),
    (0x0bc2c, [lisori_caller_name, ]),
    (0x0bccc, [lisori_caller_name, ]),
    (0x0bdc8, [lisori_caller_name, ]),
    (0x12fa0, []),
]

for offset, callers in lisori_offsets_and_callers:
    callee = p.read_lisori(offset)
    for caller in callers:
        p.flow_graph.add_edge(caller, callee, obj=da._FlowEdge())

#
# syscall jump points
#
tbl_base = 0x0acb8
syscall_count = 134
syscall_majors = []

syscall_names = {
    2: 'NKRegisterCpuPlugin',
    46: 'NKCpuPlugin',
    45: 'NKStopScheduling',
    99: 'NKSetBlueProcessID',
    126: 'NKSetTaskType',
    57: 'NKThrowException',
    68: 'NKGetPageSizeClasses',
    69: 'NKGetPageSize',
    117: 'NKCurrentAddressSpace',
    118: 'NKHomeAddressSpace',
    119: 'NKSetTaskAddressSpace',
    76: 'NKSetAreaAccess',
    100: 'NKGetFreePageCount',
    101: 'NKGetUnheldFreePageCount',
    85: 'NKMapPage',
    86: 'NKUnmapPages',
    127: 'NKMakePhysicallyContiguous',
    87: 'NKLockPages',
    88: 'NKUnlockPages',
    89: 'NKHoldPages',
    90: 'NKUnholdPages',
    104: 'NKRegisterThermalHandler',
    105: 'NKRegisterPMFHandler',
    106: 'NKMarkPMFTask',
    121: 'NKRegisterExternalHandler',
    # 122: 'NKPropogateExternalInterrupt',
    131: 'NKSetClockStep',
    132: 'NKSetClockDriftCorrection',

    # As it turns out, these would only work on debug builds!
    # 109: 'NKSetPrInfoPageSize',
    # 110: 'NKSetPrInfoILockSizes',
    # 111: 'NKSetPrInfoTransCache',
    # 112: 'NKSetPrInfoL1Cache',
    # 113: 'NKSetPrInfoL2Cache',
}

for i in range(syscall_count):
    entry_offset = tbl_base + i*4

    entry = p.semantic_list[entry_offset].get_imm_val(0)
    target_offset = i*4 + entry
    syscall_majors.append(target_offset)

    new_expr = '(%d:^-.) + (%d:^-0:^)' % (tbl_base, target_offset)

    p.indirect_imm(entry_offset, 0, new_expr)
    p.flow_graph.add_edge(0x0af08, target_offset, obj=da._FlowEdge(taken_branch=True))
    p.major_list.split_at(target_offset)
    p.major_cmt_dict[target_offset].append('syscall %d' % i)


p.flow_graph.add_edge(0x0af08, 0x0af0c, obj=da._FlowEdge())


#
# Debugger command jumps (indirect via blrl-loaded list)
#
tbl_base = 0x1769c

cmd_names = [
    'dumpmem_physical',
    'dumpmem_logical',
    'goto',
    'opaque_id_info',
    'display_kern_data',
    'dump_registers',
    'help',
    'help',
]

for i in range(8):
    entry_offset = tbl_base + i*4
    entry = p.semantic_list[entry_offset].get_imm_val(0)
    target_offset = tbl_base + entry

    p.indirect_imm(entry_offset, 0, '%d:^ - %d:^' % (target_offset, tbl_base))
    p.flow_graph.add_edge(tbl_base-4, target_offset, obj=da._FlowEdge(taken_branch=True))
    p.label(target_offset, 'cmd_%s' % cmd_names[i])


p.flow_graph.add_edge('who_the_hell_knows', 0x05800, obj=da._FlowEdge())

#
# Another thing that rather awkwardly must go *before* the disassembly stage
#
list_base = 0x154a8
for short_offset in range(list_base, 0x154c0, 2):
    entry_b = p.data[short_offset : short_offset+2]
    entry = int.from_bytes(entry_b, byteorder='big')
    target = list_base + entry
    p._insert_semantic(da._SemanticFixedSize(short_offset, entry_b))

    if not entry: continue
    p.flow_graph.add_edge(0x04668, target, obj=da._FlowEdge(taken_branch=True))
    p.indirect_imm(short_offset, 0, '%d:^ - %d:^' % (target, list_base))


for target in range(0x07674, 0x076b4, 4):
    p.flow_graph.add_edge(0x07670, target, da._FlowEdge(taken_branch=True))

#
# Copied code!
#
p.flow_graph.add_edge(0x00bcc, 0x00fd4, obj=da._FlowEdge(taken_branch=True))
p.flow_graph.add_edge(0x00c08, 0x00fd4, obj=da._FlowEdge(taken_branch=True))
p.flow_graph.add_edge(0x00c58, 0x00fd4, obj=da._FlowEdge(taken_branch=True))
p.flow_graph.add_edge(0x00cb0, 0x00fd4, obj=da._FlowEdge(taken_branch=True))
p.flow_graph.add_edge(0x00d14, 0x00fd4, obj=da._FlowEdge(taken_branch=True))

p.flow_graph.add_edge(0x00e60, 0x01088, obj=da._FlowEdge(taken_branch=True))
p.flow_graph.add_edge(0x00e9c, 0x01088, obj=da._FlowEdge(taken_branch=True))
p.flow_graph.add_edge(0x00e60, 0x01088, obj=da._FlowEdge(taken_branch=True))
p.flow_graph.add_edge(0x00f88, 0x01088, obj=da._FlowEdge(taken_branch=True))

#
# Duh.
#
p.disasm()


#
# Use the best-guess function-finder
#
p.guess_majors()

#
# Need to use setup_lisoris from before, now that I can do indirects
#
for offset, callers in lisori_offsets_and_callers:
    try:
        p.indirect_lisori(offset)
    except ValueError:
        print('Lisori at 0x%05x not yet disassembled?' % offset)
    p.major_list.split_at(offset)


#
# And stuff I've figured out by iterating frantically
#

p.major(0x00000, 0x00040, 'nk_start')
p.arg('r3', 'ConfigInfo')
p.arg('r4', 'processor_info')
p.arg('r5', 'sys_info')
p.arg('r6', 'boot_r6')
p.arg('r7', 'rtas_fourcc')
p.arg('r8', 'rtas_proc')
p.arg('r9', 'boot_hw_info')
p.cmt('Entry point from Trampoline on NewWorld.')
p.cmt('Only continues loading if the DR (data address translation) bit of the MSR is unset. Be not fooled by the linking call, which never returns. If DR is set, then we RFI to a location *in* the ConfigInfo struct with DR and IR unset, and r9 containing the address of our caller ')


p.major(0x00040, 0x00400, 'replace_old_kernel')
p.indirect_imm(0x000d8, 0)
p.label(0x000d8, '88')
p.label(0x000dc, '99')
p.indirect_imm(0x000e0, 2, '0:^ - 0x000d8:^ - 4')

p.major(0x00400, 0x00484, '')

p.major(0x00484, 0x004a8, 'wipe_irp')
p.arg('r1', 'kdp')
p.cmt('Fill the irp with 0x68f1.')

p.major(0x004a8, 0x00fd4, 'new_world')
p.arg('r3', 'ConfigInfo')
p.arg('r4', 'processor_info')
p.arg('r5', 'sys_info')
p.arg('r6', 'boot_r6')
p.arg('r7', 'rtas_fourcc', end=0x00680)
p.arg('r8', 'rtas_proc', end=0x00710)
p.arg('r9', 'boot_hw_info')
p.cmt('1. Fill segment registers very basically.')
p.cmt('2. Zero the BAT.')
p.cmt('3. Lay out the kernel\'s memory and copy some tables.')
p.cmt('4. Print the first debug message: "Hello from..."')
p.cmt('5. Choose an interrupt handler.')
p.cmt('6. Copy some ConfigInfo stuff.')
p.cmt('7. Override info for old CPUs then go to main setup.')
p.cmt('8. Do something with caches for newer G4s.')
p.cmt(0x004ac, 'Load seg reg 0 with 0x20000000 and all others with zeros')
p.cmt(0x004f8, 'Get all but lowest bit of CPU version')
p.cmt(0x00504, 'CPU is 601:')
p.label(0x00548, 'end_if_601')
p.label(0x00520, 'not_601')
p.cmt(0x00550, 'search sys_info for the physical address of the Toolbox ROM')
p.cmt(0x0055c, 'now r11=toolbox and r12=ram')
p.cmt('Some really tricky stuff happens here with the memory data.')
p.cmt('The location of the KDP and the irp get chosen.')
p.ptr(0x00618, 0x00fd4, 'r1', 'kdp')
p.ptr(0x00680, 0x0070c, 'r9', 'hw_info')
p.label(0x006ac, 'no_rtas')
p.label(0x006b4, 'end_if_rtas')
p.indirect_imm(0x00800, 0)
p.label(0x00800, '88')
p.label(0x00804, '99')
p.indirect_imm(0x00808, 2, '0:^ - 0x00800:^ - 4')
p.cmt(0x00a1c, 'check for several (some unknown) pre-7410 CPUs, and load their info')
p.indirect_imm(0x00a20, 2, '0x0120c:^ - 0:^')
p.cmt(0x00a90, 'get base of page table (why?)')
p.cmt(0x00a94, 'r21 = SDR1 & 0xffff0000')
p.cmt(0x00a98, 'r22 = (SDR1 << 16) & 0x007F0000')
p.indirect_imm(0x00b74, 1, '(0x01088:$ - 0x00fd4:^) / 4')
p.indirect_imm(0x00b80, 2, '0x01088:$ - 0:^')
p.indirect_imm(0x00dbc, 1, '(0x0114c:$ - 0x01088:^) / 4')
p.indirect_imm(0x00dc8, 2, '0x0114c:$ - 0:^')
p.label(0x00fd0, 'skip_cache_hackery_never')

p.major(0x00fd4, 0x01088, 'copied_code_1')

p.major(0x01088, 0x0114c, 'copied_code_2')

p.major(0x0114c, 0x0115c, 'cpu_pre_7410_infobytes_1')
p.major(0x0115c, 0x0116c, 'cpu_7410plus_infobytes_1')
p.major(0x0116c, 0x0117c, 'cpu_pre_7410_infobytes_2')
p.major(0x0117c, 0x0118c, 'cpu_7410plus_infobytes_2')
p.major(0x0118c, 0x011cc, 'cpu_pre_7410_infolongs')
p.major(0x011cc, 0x0120c, 'cpu_7410plus_infolongs')

p.major(0x0120c, 0x01350, 'cpuinfo_override_table')
p.cmt('For 7400(only) and earlier CPUs. Overwrites info in KDP copied from bootloader.')

p.major(0x01350, 0x01360, 'new_world_hardcode_cpu_info')
p.cmt('All G3s and earler, plus the G4-7400 (only). Overwrite part of the CPU info that we got from the bootloader (the important bits), and go to setup.')
p.arg('r3', 'ConfigInfo')
p.arg('r4', 'processor_info')
p.arg('r5', 'sys_info')
p.arg('r6', 'boot_r6')
p.arg('r9', 'cpuinfo_size')
p.arg('r10', 'kdp_cpuinfo')
p.arg('r11', 'static_cpuinfo')

p.major(0x01360, 0x01430, 'new_world_final_common')
p.arg('r1', 'kdp')

p.major(0x01430, 0x01434, 'setup_new_world')
p.cmt('Sometimes (?) on NewWorld machines, blue issues a 68k reset trap to reinit the kernel. Rene says that this is necessary to set up address spaces.')
p.arg('r1', 'kdp')

p.major(0x01434, 0x02674, 'setup')
p.cmt('Final common pathway. Prints a whole heap of stuff.')
p.cmt('cr5.eq is set for OldWorld, unset for NewWorld')
p.cmt('')
p.cmt('SPRG0: ("EWA" -- core-specific Exception Work Area)')
p.cmt('"Software may load a unique physical address in this register to identify an area of memory reserved for use by the first-level exception handler. This area must be unique for each processor in the system."')
p.cmt('')
p.cmt('SPRG1: ("r1" = "KDP" = kernel data page)')
p.cmt('"This register may be used as a scratch register by the first-level exception handler to save the content of a GPR. That GPR then can be loaded from SPRG0 and used as a base register to save other GPRs to memory."')
p.cmt('')
p.cmt('SPRG2: ("LR" = interrupt-saved link register')
p.cmt('"This register may be used by the operating system as needed."')
p.cmt('')
p.cmt('SPRG3: ("vecBase" = pointer to one of six 48-member vector tables in KDP or KCP)')
p.cmt('"This register may be used by the operating system as needed."')
p.arg('r1', 'kdp')
p.cmt(0x014b8, 'Copy 64b from 0xfc0(kdp) to 0xfc0(irp)...')
p.cmt(0x014dc, '...done')
p.cmt(0x014e8, 'Fill SIX vector tables, in kdp and below, with CRASHes...')
p.cmt(0x01530, '...done')
p.cmt(0x01530, 'Fill ONE vector table, below kdp, with something ELSE...')
p.cmt(0x01548, '...done')
p.cmt(0x0154c, 'Point SPRG3=vecBase at one of those tables.')
p.ptr(0x0154c, 0x01680, 'r9', 'kdp', p.semantic_list[0x0154c-4].get_imm_val(2))
p.ptr(0x01554, 0x01680, 'r8', 'kdp', p.semantic_list[0x01554-4].get_imm_val(2))
p.ptr(0x01684, 0x016d0, 'r8', 'kdp', p.semantic_list[0x01684-4].get_imm_val(2))
p.ptr(0x016d4, 0x01720, 'r8', 'kdp', p.semantic_list[0x016d4-4].get_imm_val(2))
p.ptr(0x01724, 0x01770, 'r8', 'kdp', p.semantic_list[0x01724-4].get_imm_val(2))
p.ptr(0x01774, 0x01824, 'r8', 'kdp', p.semantic_list[0x01774-4].get_imm_val(2))
p.label(0x01778, 'loop_memset')
p.cmt(0x01824, 'super boring stuff over. now cpu-specific stuff!')
p.cmt('(I have only listed CPUs that I think Apple used)')
p.cmt('PVR = version << 16 | revision')
p.cmt('')
p.cmt('Pre-G3:')
p.cmt('0001 = 601')
p.cmt('0003 = 603')
p.cmt('0006 = 603e')
p.cmt('0007 = 606ev/606r')
p.cmt('0004 = 604')
p.cmt('0004 = 604e')
p.cmt('')
p.cmt('G3:')
p.cmt('0008 = 750/750CX/750CXe/755')
p.cmt('0007 = 750FX')
p.cmt('')
p.cmt('G4:')
p.cmt('000c = 7400')
p.cmt('800c = 7410')
p.cmt('8000 = 7450')
p.cmt('8001 = 7445/7455')
p.cmt('8002 = 7447/7457 (upgrades only!)')
p.cmt('')
p.cmt('G5:')
p.cmt('0039 = 970')
p.cmt('003c = 970FX')
p.cmt(0x01834, 'pre-7410 CPUs (not that a 7400 is anything like a G3)')
p.cmt(0x01838, 'the only CPUs >= 0x0010 are G5s')
p.label(0x01840, 'skip_zeroing_G5')
p.label(0x01870, 'G4_7410_or_later')
p.cmt(0x01870, 'clear the high (8000) bit and have fun')
p.cmt(0x0187c, 'treat 8010 (doesnt exist) as 8FF0 -- why??')
p.label(0x01880, 'skip_spoofing_weird_G4')
p.cmt(0x018b0, 'im not even going to complain that this compiler is so dumb')
p.label(0x018b4, 'post_cpu_specific')
p.cmt(0x018b4, 'fill a buncha r1 stuff with 0xFFFFFFFF')

p.cmt(0x018c8, 'Initialise the seven kernel locks with zero in the count field...')
p.cmt(0x018e8, '...and a name in the fourcc field.')
for x in range(0x018e8, 0x0193c, 12):
    p.indirect_str_lisori(x)
    p.cmt(x + 12, '')

p.cmt(0x01954, 'Now what?')
p.indirect_str_lisori(0x01984)
p.indirect_str(0x0199c, 1)
p.indirect_str(0x019a4, 2)
p.indirect_str(0x01d3c, 1)
p.indirect_str(0x01d40, 2)
p.indirect_str(0x01ebc, 1)
p.indirect_str(0x01ec0, 2)
p.label(0x024e4, '*_skip_grabbing_more_pages')
p.label(0x0255c, 'finish_old_world')

p.major(0x02674, 0x026cc, 'undo_failed_kernel_replacement')
p.cmt('Inits or reinits the log')

p.major(0x026cc, 0x026f0, 'old_world_rfi_to_userspace_boot')
p.arg('r1', 'kdp')

p.major(0x02700, 0x0289c, 'lock')
p.cmt('Gets something from -0x340(ewa)')
p.cmt('Lock struct: word@0=count, word@16=holder')
p.cmt('Return pretty quick-smart if we get the lock.')
p.cmt('If hands must be dirtied, put r22-r31 into EWA.')
p.arg('r8', 'lock')
p.ptr(0x0270c, 0x02714, 'r9', 'kdp')
p.ptr(0x02730, 0x0289c, 'r9', 'kdp')
p.label(0x02730, '*_already_held')

p.major(0x0289c, 0x02940, 'spinlock_what')

p.major(0x02940, 0x02944, 'panic_wrapper_0x02940')

p.major(0x02960, 0x02964, 'panic_wrapper_0x02960')

p.major(0x02cb0, 0x02ccc, 'skeleton_key')
p.cmt('Called when a Gary reset trap is called. When else?')

p.major(0x03b40, 0x03bd8, 'dsi_vector')

p.major(0x03d40, 0x03d98, 'int_prepare')
p.arg('r6', 'saved at *(ewa + 0x18)')
p.arg('sprg1', 'saved at *(ewa + 4)')
p.arg('rN (0,7,8,9,10,11,12,13, not r1)', 'saved at *(*(ewa - 0x14) + 0x104 + 8*N)')
p.ret('r0', '0')
p.ret('r1', '*(ewa - 4)')
p.ret('r6', 'kdp')
p.ret('r7', '*(ewa - 0x10) # flags?')
p.ret('r8', 'ewa')
p.ret('r10', 'srr0')
p.ret('r11', 'srr1')
p.ret('r12', 'sprg2')
p.ret('r13', 'cr')

p.major(0x03ce0, 0x03d34, 'save_all_registers')

p.major(0x037c8, 0x03934, 'memretry_machine_check')

p.major(0x04508, 0x04518, 'wordfill')
p.arg('r8', 'dest')
p.arg('r22', 'len in bytes')
p.arg('r23', 'fillword')

p.major(0x04520, 0x045b0, 'reset_trap')
p.cmt('Handle a 68k reset trap.')
p.cmt('Some messing around with 601 RTC vs later timebase registers.')
p.cmt("If Gary Davidian's first name and birthdate were in the 68k's A0/A1 (the 'skeleton key'), do something. Otherwise, farm it out to non_skeleton_reset_trap.")
p.arg('r3', 'a0')
p.arg('r4', 'a1')
p.indirect_str(0x0452c, 2)
p.label(0x0453c, '*_cpu_not_601')
p.label(0x04540, '*_endif')
p.indirect_str(0x04544, 1)

p.major(0x045b0, 0x04660, 'non_skeleton_reset_trap')
p.cmt("A 68k reset trap without Gary Davidian's magic numbers.")

p.major(0x04660, 0x0466c, 'pih_indirect')
p.arg('r1', 'kdp')

p.major(0x04680, 0x046d0, 'regsave_debug')
p.cmt('r2-r5 and r14-r31 (real registers) and r6-r13 (regsave) into compact area, then debug.')
p.arg('r1', 'compact area')

p.major(0x048e0, 0x04a20, 'SIGP')
p.cmt('Really need to figure out what this does...')
p.arg('r7', 'flags')
p.arg('r8', 'usually 2?')

p.major(0x04ac0, 0x04b54, 'sc_vector')
p.cmt('Not fully sure about this one')
p.label(0x04b38, '*_not_special')

p.major(0x04b80, 0x04bbc, 'return_to_kern_from_dummy_interrupt')

p.major(0x04c00, 0x04c04, 'panic_wrapper_0x04c00')

p.major(0x05278, 0x054b8, '')

p.major(0x05524, 0x055e0, '')

p.major(0x055e0, 0x05618, 'flush_tlb')

p.major(0x05800, 0x05808, 'funny_debug_place')

p.major(0x06870, 0x06a14, '')
p.cmt('Mess with some whacko undocumented SPRs. QEMU complains. Called by setup. Boots fine if clobbered? Temporarily overwrites a KDP vector with a dummy handler. Knowing what vec[7] does will help.')

p.indirect_lisori(0x07658)

p.major(0x08620, 0x08624, 'panic_wrapper_0x08620')

p.major(0x09ce0, 0x09d1c, 'panic_offset_to_r1_minus_0x810_x48__0x9dfc_to_prev_plus_4_20_36')

p.major(0x09d20, 0x09dfc, 'bootstrap_cpu')
p.cmt('NB: I was probably wrong about this.')
p.cmt('Contains a (very rare) mtsprg0 instruction.')
p.indirect_imm(0x0a408, 0)
p.label(0x0a408, '88')
p.label(0x0a40c, '99')
p.indirect_imm(0x0a410, 2, '0x0a600:^ - 0x0a408:^ - 4')


p.major(0x0a620, 0x0a624, 'panic_wrapper_0x0a620')

p.major(0x0a640, 0x0a8bc, 'rtas_call')
p.arg('r1', 'kdp')
p.arg('r6', 'some kind of place')
p.arg('r7', 'some kind of flags')
p.cmt('Only major that hits the RTAS globals.')
p.cmt('RTAS requires some specific context stuff.')
p.label(0x0a654, 'rtas_is_available')
p.label(0x0a8b4, 'rtas_make_actual_call')

p.major(0x0aca0, 0x0af0c, 'syscall')
p.arg('r1', 'kdp')
p.arg('r6', 'save area')
p.label(0x0acb8, '*_tbl')
p.label(0x0aed0, '*_tbl_end', of_start=False)
p.cmt(0x0aed0, 'Increment a counter. All but LS 10 bits ignored, giving 1024 entries.')
p.cmt('r16 = &perf_tbl')
p.cmt('r17 = offset into counter table')
p.label(0x0aeec, '*_skip_counter')
p.indirect_imm(0x0aeec, 1, '(0x0aed0:^-0x0acb8:^)/4')
p.cmt(0x0aeec, 'r14 = offset of entry in jump table')
p.cmt('r16 = offset of jump table in kernel')
p.cmt('r15 = content of entry')
p.cmt('jump assumes kernel mapped at zero')
p.indirect_lisori(0x0aef4)

p.major(0x0af38, 0x0af58, 'syscall_return_assert_lock_unheld')
p.arg('r1', 'kdp')

p.major(0x0af0c, 0x0af14, 'bad_syscall')
p.cmt('Handler for out-of-range or unimplemented (debug) syscalls.')

p.major(0x0af58, 0x0af60, 'syscall_return_noErr')

p.major(0x0b024, 0x0b02c, 'syscall_return_kMPInsufficientResourcesErr')

p.major(0x0b04c, 0x0b054, 'syscall_return_wtf')

p.major(0x0b074, 0x0b07c, 'syscall_return_paramErr')

p.major(0x0b0c4, 0x0b0cc, 'syscall_return_kMPInvalidIDErr')

p.major(0x0b0f4, 0x0b0fc, 'syscall_return_noErr_again')

p.major(0x0b124, 0x0b144, 'syscall_return')

p.major(0x0b144, 0x0b248, '')

p.major(0x0b24c, 0x0b3b0, 'NKRegisterCpuPlugin')

p.major(0x0b3b0, 0x0b3cc, 'nk_cpu_count')
p.cmt('Called by MPProcessors and MPProcessorsScheduled')
p.arg('r3', '0:all, 1:scheduled')
p.ret('r3', 'cpu_count')

p.major(0x0b598, 0x0b640, 'nk_yield_with_hint')

p.major(0x0b76c, 0x0b788, 'nk_get_next_id_unowned')
p.cmt('Replace the provided process/coherence/console ID with the "next" one. IDs were opaque but were only longs. Wrapped by MPGetNext*ID, which indirects the opaque ID structure.')
p.cmt('')
p.cmt('From MP docs: A coherence group is the set of processors and other bus controllers that have cache-coherent access to memory. Mac OS 9 defines only one coherence group, which is all the processors that can access internal memory (RAM). Other coherence groups are possible; for example, a PCI card with its own memory and processors can comprise a coherence group.')
p.arg('r3', 'kind (process=1,coherence=10,console=13)')
p.arg('r4', 'prev_id')
p.ret('r3', 'MP result code')
p.ret('r4', 'next_id')

p.major(0x0bd44, 0x0bdfc, 'NKStopScheduling')

# odd to find this here
p.major(0x0be4c, 0x0be50, '_bad_syscall')

p.major(0x0be50, 0x0beac, 'NKxprintf')

p.major(0x0c12c, 0x0c240, 'NKSetClockStep')
p.cmt('Debug string matches MPLibrary!')
p.cmt('0xf7e(r1) = clock_step (half-word)')
p.arg('r3', 'new_clock_step  # (half-word)')

p.major(0x0b788, 0x0b8b8, 'nk_get_next_id_owned')
p.cmt('Replace the provided address space/task/queue/semaphore/critical region/timer/event/notification ID with the "next" one. IDs were opaque but were only longs. Wrapped by MPGetNext*ID, which indirects the opaque ID structure. Differs from nk_get_next_id_unowned because it deals in objects owned by a particular process.')
p.arg('r3', 'owningProcessID')
p.arg('r4', 'kind (task=2,timer=3,queue=4,sema=5,crit_rgn=6,addr_spc=8,evt=9,notif=12)')
p.arg('r5', 'prev_id')
p.ret('r3', 'MP result code')
p.ret('r5', 'next_id')
p.label(0x0b798, 'try_another_id')
p.label(0x0b804, 'want_task_id')
p.label(0x0b828, 'want_timer_id')
p.label(0x0b838, 'want_queue_id')
p.label(0x0b848, 'want_sema_id')
p.label(0x0b858, 'want_critrgn_id')
p.label(0x0b868, 'want_addrspc_id')
p.label(0x0b878, 'want_evt_id')
p.label(0x0b888, 'want_11_id')
p.label(0x0b898, 'want_notif_id')
p.label(0x0b8a8, 'want_13_id')

p.major(0x0c240, 0x0c3ac, 'adjust_tb_drift')
p.cmt("There's a one-billion constant in here, for fractional expression.")
p.cmt('-0x36c(r1) = tb_drift_numerator')
p.cmt('-0x368(r1) = tb_drift_denominator')
p.arg('r3', 'to')

p.major(0x0c5d4, 0x0c5d8, 'panic_wrapper_0x0c5d4')

p.major(0x0c8b4, 0x0c968, '')

p.major(0x0ccf4, 0x0cd9c, '')

p.major(0x0d35c, 0x0d504, '')

p.major(0x0db04, 0x0dc0c, '')

p.major(0x0dce8, 0x0dd64, '')

p.major(0x0e280, 0x0e284, 'panic_wrapper_0x0e280')

p.major(0x0e330, 0x0e548, 'mktask')

p.major(0x0e95c, 0x0ea58, 'NKThrowException')
p.cmt('Throws an exception to a specified task.')
p.arg('r3', 'MPTaskID task')
p.arg('r4', 'MPExceptionKind kind')
p.ret('r3', 'result code')

p.major(0x0f380, 0x0f384, 'panic_wrapper_0x0f380')

p.major(0x0f384, 0x0f3b8, '')

p.major(0x0f3b8, 0x0f7a0, 'convert_pmdts_to_areas')
p.cmt('Pretty obvious from log output.')

p.major(0x0f7a0, 0x0f7a8, 'NKGetPageSizeClasses')
p.arg('r1', 'kdp')
p.ret('r3','pageClass')

p.major(0x0f7a8, 0x0f7b8, 'NKGetPageSize')
p.arg('r1', 'kdp')
p.arg('r3', 'pageClass')
p.ret('r3', 'byteCount')

p.major(0x0f824, 0x0f9f8, 'NKCreateAddressSpaceSub')
p.cmt('Guessing by strings -- but maybe that name applies to syscall?')

p.major(0x0fbec, 0x10284, 'createarea')

p.major(0x10284, 0x102a8, '')

p.major(0x102a8, 0x102c8, '')

p.major(0x102c8, 0x10320, '')

p.major(0x10cb8, 0x10d38, '')

p.major(0x114fc, 0x11538, 'free_list_add_page')
p.arg('r1', 'kdp')
p.arg('r8', 'maybe the page')

p.major(0x12780, 0x12784, 'panic_wrapper_0x12780')

p.major(0x12784, 0x1281c, 'pool_init')
p.arg('r1', 'kdp')
p.cmt('Allocate one page for the kernel pool. Same layout at Memtop starts at 7 pages below KDP.')
p.cmt('Take note of the structure from kdp-ab0 to kdp-aa0')
p.cmt(0x127ac, 'bit of a mystery')
p.indirect_str_lisori(0x127bc)
p.indirect_str_lisori(0x127d8)
p.indirect_str_lisori(0x127ec)
p.cmt(0x127f8, 'set up linked list')
p.indirect_str_lisori(0x1280c)

p.major(0x1281c, 0x129a0, 'pool_malloc')
p.cmt('Easy to use! 0xfd8 (a page minus 10 words) is the largest request that can be satisfied.')
p.arg('r1','kdp')
p.arg('r8', 'size')
p.ret('r8', 'ptr')
p.label(0x12824, '*_with_crset')
p.indirect_str(0x128e0, 1)
p.indirect_str(0x128ec, 2)
p.indirect_str_lisori(0x12968)

p.major(0x129a0, 0x129cc, 'looks_like_poolextend')

p.major(0x129cc, 0x129fc, '')

p.major(0x129fc, 0x12a34, '')

p.major(0x12a34, 0x12a80, '')

p.major(0x12a80, 0x12b94, 'poolextend')
p.cmt(' 0xed0(r1) = pool extends (I increment)')
p.cmt('-0xa9c(r1) = virt last page (I update)')
p.cmt('-0xaa0(r1) = phys last page (I update)')
p.cmt('Assumes that cache blocks are 32 bytes! Uh-oh.')
p.cmt('')
p.cmt('Page gets decorated like this:')
p.cmt("000: 00 00 0f e8")
p.cmt("004: 87 'B 'G 'N")
p.cmt("008: 00 00 0f e8")
p.cmt("00c: 87 'l 'o 'c")
p.cmt("...     zeros    << r8 passes ptr to here")
p.cmt("fe8: phys offset from here to prev page")
p.cmt("fec: 87 'E 'N 'D")
p.cmt("ff0: logical abs address of prev page")
p.cmt("ff4: 00 00 00 00")
p.cmt("ff8: 00 00 00 00")
p.cmt("ffc: 00 00 00 00")
p.cmt('')
p.arg('r1', 'kdp')
p.arg('r8', 'anywhere in new page (phys)')
p.arg('r9', 'page_virt')
p.label(0x12b18, '*_zeroloop')
p.cmt(0x12b28, 'Put the funny stuff in')
p.indirect_str(0x12b30, 1)
p.indirect_str(0x12b34, 2)
p.indirect_str(0x12b48, 1)
p.indirect_str(0x12b4c, 2)
p.indirect_str(0x12b64, 1)
p.indirect_str(0x12b68, 2)
p.cmt(0x12b78, 'Update globals')
p.cmt(0x12b80, 'Unknown func calls')

p.major(0x12d40, 0x12d44, 'panic_wrapper_0x12d40')

p.major(0x12d44, 0x12e88, 'say_nanodebugger_activated')

p.major(0x1301c, 0x13060, 'say_starting_timeslicing')

p.major(0x13060, 0x130f0, '')

# SOMETHING IN THIS GAP IS NON-RELOCATABLE (and there sure is a lot of un-disassembled code here)

p.major(0x13708, 0x13750, 'scale_timebase')
p.arg('r1', 'kdp')
p.arg('r8', 'multiple (pos: /250; neg: /250000)')
p.ret('r8', 'hi')
p.ret('r9', 'lo')
p.label(0x13728, '*_divisor_250000')
p.indirect_lisori(0x1372c, '250000')
p.label(0x13734, '*_divisor_250')

p.major(0x13750, 0x137b4, 'bizarre')

p.major(0x137c0, 0x137c4, 'panic_wrapper_0x137c0')

p.major(0x137c4, 0x138ac, 'init_rdyqs')
p.arg('r1', 'kdp')
p.cmt('Four queues, hardcoded. Not sure why. Each queue knows about 0.001042*tbfreq -- timeslicing quantum?')
p.indirect_str(0x137f0, 1)
p.indirect_str(0x137f4, 2)


p.major(0x138ac, 0x138d4, 'save_registers_from_r14')
p.cmt('Save r14-r31 to 0x174(r6), 8-byte spaced.')
p.cmt('Looks very very optimised?')
p.cmt('stmw not used because registers are spaced out?')
p.arg('r6', 'ewa')
p.ret('r8', 'sprg0 (not used by me)')

p.major(0x138d4, 0x1391c, 'save_registers_from_r20')
p.arg('r6', 'ewa')
p.ret('r8', 'sprg0 (not used by me)')

p.major(0x1391c, 0x13988, 'restore_registers_from_r14')
p.cmt('Restore r14-r31 from 0x174(r6), 8-byte spaced.')
p.cmt('Again, well optimised')
p.arg('r6', 'ewa')

p.major(0x13c90, 0x13e4c, '')

p.major(0x13e4c, 0x13ed8, '')

p.major(0x13ed8, 0x13f78, '')

p.major(0x13f78, 0x142a8, '')

p.major(0x142a8, 0x142dc, '')

p.major(0x142dc, 0x144cc, '')

p.major(0x144cc, 0x14548, 'int_teardown')
p.cmt('All syscalls get here?')
p.cmt('r0,7,8,9,10,11,12,13 restored from r6 area')
p.cmt('r1,6 restored from sprg0 area')
p.cmt('')
p.cmt('Apple used the "reserved" (not first three) bits of XER.')
p.cmt('If bit 27 of 0xedc(r1) is set:')
p.cmt('   Bit 22 of XER is cleared')
p.cmt('   Bit 10 of r7 is inserted into XER at bit 23')
p.arg('sprg0', 'for r1 and r6')
p.arg('r1', 'kdp')
p.arg('r6', 'register restore area')
p.arg('r7', 'flag to insert into XER')
p.arg('r10', 'new srr0 (return location)')
p.arg('r11', 'new srr1')
p.arg('r12', 'lr restore')
p.arg('r13', 'cr restore')

p.major(0x14548, 0x148ec, '')

p.major(0x148ec, 0x149d4, '')

p.major(0x149d4, 0x14a90, '')

p.major(0x14a90, 0x14a98, 'clear_cr0_lt')

p.major(0x14a98, 0x14af8, '')

p.major(0x14af8, 0x14bcc, '')

p.major(0x15140, 0x15144, 'panic_wrapper_0x15140')

p.major(0x15144, 0x151b0, 'index_init')
p.cmt('These are the first requests made of the pool!')
p.arg('r1', 'kdp')
p.indirect_str_lisori(0x1516c)
p.indirect_str_lisori(0x151a0)

p.major(0x151b0, 0x152f8, 'alloc_id')
p.arg('r1', 'kdp')
p.arg('r9', 'kind')

p.major(0x15380, 0x153e0, 'id_kind')
p.arg('r8', 'id')
p.ret('r8', 'something not sure what')
p.ret('r9', '0:inval, 1:proc, 2:task, 3:timer, 4:q, 5:sema, 6:cr, 7:cpu, 8:addrspc, 9:evtg, 10:cohg, 11:area, 12:not, 13:log')

p.major(0x154a0, 0x154dc, 'get_pih_addr')
p.cmt('ConfigInfo specifies a one-byte primary interrupt handler kind. Look up function address in this table.')
p.label(0x154a8, 'pih_tbl')
p.arg('r3', 'ConfigInfo')
p.ret('r12', 'clobbered')
p.ret('r7', 'pih_pa')

p.major(0x154e0, 0x15740, 'interrupt_blue')
p.arg('r1', 'kdp')
p.cmt('At least I think so.')

p.major(0x15740, 0x15794, 'NKPropogateExternalInterrupt')
p.arg('r1', 'kdp')

p.major(0x15800, 0x15840, 'machine_specific_lut')

p.major(0x15840, 0x158e4, 'pdm_pih_01')
p.arg('r1', 'kdp')
p.cmt('Piltdown Man = first ("G1") Power Macs. NuBus. Models 61xx, 71xx, 81xx.')
p.indirect_lisori(0x158cc)

p.major(0x15900, 0x159a8, 'pbx_pih_03')
p.arg('r1', 'kdp')
p.cmt('PBX = NuBus PowerBooks. Possibly not including the 5300?')

p.major(0x159c0, 0x15ad0, 'gazelle_pih_05')
p.arg('r1', 'kdp')
p.cmt('Gazelle = later low-end "G2" Power Macs. 603 series processors. PCI. Models 54xx-55xx, 64xx-65xx.')
p.cmt('The 54xx/64xx ROM actually identifies as Alchemy, not Gazelle, and SheepShaver considers this difference when patching the ROM Nanokernels. But, Wikipedia describes these machines as minor upgrades, EveryMac calls them Gazelle, and they use the same PIH type.')

p.major(0x15b00, 0x15be4, 'tnt_pih_02')
p.arg('r1', 'kdp')
p.cmt('TNT = High-end and mid-range "G2" Power Macs. PCI. 603 and 604 series processors. Models 7200-7600, 8500-8600, 9500-9600.')

p.major(0x15c00, 0x15d24, 'gossamer_pih_07')
p.arg('r1', 'kdp')
p.cmt('Gossamer = beige G3. PIH 07 also used for GRX = OldWorld PowerBook G3 Series.')

p.major(0x15d40, 0x15e20, 'nwpbg3_pih_0a')
p.arg('r1', 'kdp')
p.cmt("Only ever seen this on Mikey's (NewWorld) Lombard. So apparently the Trampoline can also change the ROM's default PIH.")

p.major(0x15e40, 0x15ef0, 'cordyceps_pih_04')
p.arg('r1', 'kdp')
p.cmt('Cordyceps = early low-end "G2" Power Macs. 603 series processors. PCI. Models 52xx-53xx, 62xx-63xx.')

p.major(0x15f00, 0x16160, 'newworld_pih_06')
p.arg('r1', 'kdp')
p.cmt('Trampoline leaves ConfigInfo value unchanged. PIH 06 also specified in Pippin ROM.')

p.major(0x16180, 0x163dc, 'unknown_pih_08')
p.arg('r1', 'kdp')

p.major(0x163e0, 0x16520, 'prints')
p.cmt('Print null-terminated string with a few special escapes. Not done figuring this out, with the serial and stuff.')
p.label(0x1643c, '*_skip_serial')
for i in range(0x1644c, 0x16494, 4):
    sem = p.semantic_list[i]
    if sem.mnem == 'cmpwi':
        p.indirect_str(i, 1)
p.label(0x16440, '*_next_char')
p.label(0x16470, '*_escape_code')
p.label(0x16494, '*_literal_backslash_or_caret')
p.label(0x1649c, '*_normal_char')
p.label(0x164c8, '*_newline')

p.major(0x16520, 0x165cc, 'print_common')

p.major(0x165cc, 0x165ec, 'print_return')
p.cmt('Restores registers from EWA and returns.')

p.major(0x165ec, 0x16710, 'printd')
p.cmt('print decimal')

p.major(0x16710, 0x16734, 'printw')
p.cmt('print word (hex) then a space')

p.major(0x16734, 0x1675c, 'printh')
p.cmt('print halfword (hex) then a space')

p.major(0x1675c, 0x16784, 'printb')
p.cmt('print byte (hex) then a space')

p.major(0x16784, 0x167ac, 'print_unknown')

p.major(0x167ac, 0x16880, 'print_digity_common')

p.major(0x16880, 0x168ec, 'getchar')

p.major(0x168ec, 0x16980, 'printc')
p.cmt('print char')

p.major(0x16980, 0x16ae8, 'serial_flush')
p.cmt('This and the following func are a bit speculative, but whatever.')

p.major(0x16ae8, 0x16b44, 'serial_io')
p.cmt('See disclaimer above.')

p.major(0x16b44, 0x16b70, 'serial_busywait')
p.cmt('See disclaimer above.')

p.major(0x172e0, 0x18040, 'panic')
p.cmt(0x17534, 'gets kdp from print!!!')
p.ptr(0x17534, 0x18040, 'r1', 'kdp')
p.ptr(0x17dc8, 0x18040, 'r17', 'ewa')
p.ptr(0x17ec8, 0x17fac, 'r18', 'task')
p.ptr(0x17fac, 0x18040, 'r18', 'addrspc')
p.label(0x17574, '*_prompt')
p.label(0x17678, '*_load_commands')
p.label(0x17698, 'load_*_tbl')
p.label(0x1769c, '*_tbl')
p.label(0x17c6c, '*_load_id_kind_strings')
p.label(0x17d50, '*_load_more_jumps')
p.label(0x17d8c, '*_load_id_args')
p.label(0x17660, '*_bad_command')
p.label(0x178d8, '*_missing_physical_addr')
p.label(0x17904, '*_bad_length_1')
p.label(0x179a8, '*_missing_logical_addr')
p.label(0x179d4, '*_bad_length_2')
p.label(0x17aa0, '*_bad_resume_address')
p.label(0x17bfc, '*_missing_opaque_id')
p.label(0x17c24, '*_bad_opaque_id')
for offset in (0x1767c, 0x17d90):
    while p.data[offset] != 0xff:
        next_offset = p.data.index(b'\x00', offset) + 1
        data = p.data[offset:next_offset]
        # print(hex(offset), repr(data))
        p._insert_semantic(da._SemanticString(offset, data))
        offset = next_offset
    p._insert_semantic(da._SemanticFixedSize(offset, p.data[offset:offset+1]))

for i in range(0x17c70, 0x17d50, 16):
    p._insert_semantic(da._SemanticString(i, p.data[i:i+16]))

p.major(0x18148, 0x18258, 'print_xpt_info')
p.indirect_lisori(0x18150, '(%d:$ - 0:^)' % len(p.data))

p.major(0x18258, 0x182f0, 'print_sprgs')
p.cmt('Goldmine. Tells me what the SPRGs do!')

p.major(0x182f0, 0x183e4, 'print_sprs')
p.cmt('Both user-mode and supervisor-only')

p.major(0x183e4, 0x18468, 'print_segment_registers')

p.major(0x18468, 0x18544, 'print_gprs')

p.major(0x18544, 0x1860c, 'print_memory')

p.major(0x1860c, 0x18738, 'print_memory_logical')

p.major(0x18738, 0x1879c, 'cmd_lookup')
p.arg('r16', 'command strings')
p.arg('r17', 'lut')
p.ret('cr0', 'found')
p.ret('r17', 'ptr to lut entry')

p.major(0x1879c, 0x187b0, 'next_cmd_word')
p.arg('r15', 'start')
p.ret('r15', 'ptr')
p.ret('r16', 'char')

p.major(0x18a00, 0x18a74, 'screenlog_init')
p.arg('r1', 'kdp')

p.major(0x18a74, 0x18a98, 'screenlog_putchar')
p.arg('r1', 'kdp')

p.major(0x18a98, 0x18bec, 'screenlog_redraw')
p.arg('r1', 'kdp')

p.major(0x18bec, 0x18c08, '')

p.major(0x18c08, 0x18c18, '')

p.major(0x18c18, 0x18d10, '')

p.major(0x18d5c, 0x18e24, '')

p.major(0x18e24, 0x18e54, '')

p.major(0x18e54, 0x18fd4, '')

p.major(0x18fd4, 0x19018, 'funny_thing')

p.major(0x19018, 0x190a0, '')

p.major(0x190a0, 0x19aa4, 'load_log_font')

p.major(0x19ab0, 0x19af4, '')

p.major(0x19b00, 0x19b14, '')

p.major(0x19b20, 0x19b2c, 'load_log_colours')
p.cmt('Each word is RGB with the high byte ignored. Background and text.')

p.label(len(p.data), 'nk_end', of_start=False)

# Rename syscalls with info from MPLibrary
for i, start in enumerate(syscall_majors):
    try:
        p.major_name_dict[start] = syscall_names[i]
    except KeyError:
        pass

#
# Do what I have come for.
#

if cmdline.disasm:
    with open(cmdline.disasm, 'w') as f:
        print(p, file=f)
else:
    print('You chose not to output an asm file. Probably a mistake.')


if cmdline.dump_constants:
    with open(cmdline.dump_constants, 'w') as f:
        for offset, data in p.lisoris(range(0, len(p.data))):
            as_int = int.from_bytes(data, byteorder='big')

            s = sum(32 <= ch < 127 for ch in data)

            # cand
            # try:
            #     ind = '' if any(p.semantic_list[offset]._imm_exprs) else '#cnd'
            # except AttributeError:
            #     ind = '*'
            #     print(repr(p.semantic_list[offset]))
            
            is_string = (s >= 3)
            try:
                indirected = any(p.semantic_list[offset]._imm_exprs)
            except AttributeError:
                indirected = False
            shares_target = ((as_int, True) in p.backref_dict) or ((as_int, False) in p.backref_dict)
            candidate = as_int <= len(p.data) and as_int % 4 == 0
            try:
                promising = isinstance(p.semantic_list[as_int-4], da._SemanticInsn) and not isinstance(p.semantic_list[as_int], da._SemanticInsn)
            except:
                promising = False

            things = zip('itcp', (indirected, shares_target, candidate, promising))
            s = ''.join((c if b else '-') for (c, b) in things)

            show_string = '    ' + repr(data)[1:] if is_string else ''
            
            print('    ' + hex(as_int).rjust(10) + ',    # %05x  ' % offset + s + show_string, file=f)
