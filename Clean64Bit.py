#!/usr/bin/python

from macholib import MachO
from macholib import mach_o
from macholib.ptypes import *
import os
import sys

def main(executableName):
    print
    print 'MachO Headers Eraser'
    print
    print 'This script may cause some unpredictable issues, try delete things in the safe list if your program doesn\'t work after patched.'
    print
    print '[+]Checking if patched'
    rawFile = open(executableName, 'r')
    rawFile.seek(-4, 2)
    if cmp(rawFile.read(),'BOOM') == 0:
        print '#Error: Executable has been patched'
        exit()
    
    print '[+]Making backup'
    os.system('cp %s %s_bak' % (executableName, executableName))
    print '[+]Reading raw executable'
    machoHeader = MachO.MachO(executableName)
    print '[+]%s readed' % machoHeader.filename
    
    for header in machoHeader.headers:
        eraseLoadCommandInHeader(header)

    print '[+]Generating new executable'
    spliceHeadersAndRawStuff(machoHeader, executableName)
    print '[+]New executable generated'

    print '[+]Overwriting raw executable'
    os.system('mv %s_tmp %s' % (executableName, executableName))

    print '[+]Giving execute permission to new executable'
    givex(executableName)

    print
    print '[+]All done.'

    return

def givex(str):
    os.system('chmod +x %s' % str)
    return

def spliceHeadersAndRawStuff(header, name):
    outputexecutable = open('%s_tmp' % name,'wb')
    header.write(outputexecutable)
    
    rawStuff = open(name, 'rb')
    
    offset = header.headers[len(header.headers)-1].low_offset
    
    rawStuff.seek(offset)
    outputexecutable.write(rawStuff.read())
    outputexecutable.write('BOOM')
    
    outputexecutable.close()
    rawStuff.close()
    
    return

def eraseLoadCommandInHeader(header):
    ##################################################################
    # Add confirmed removeable stuff to the following lists or       #
    # remove the stuff which cause problems from the following lists #
    ##################################################################
    safeRemoveList_segname = ['__PAGEZERO'
                              #, '__DATA'
                                      ]
    safeRemoveList_sectname = ['__text',
                               '__stubs',
                               '__stub_helper',
                               '__cstring',
                               '__cfstring',
                               '__unwind_info',
                               '__eh_frame',
                               '__nl_symbol_ptr',
                               '__la_symbol_ptr',
                               #'__objc_classlist',
                               '__objc_classrefs',
                               '__objc_superrefs',
                               #'__objc_protolist',
                               '__objc_msgrefs',
                               #'__objc_imageinfo',
                               '__objc_methname',
                               '__objc_classname',
                               '__objc_methtype',
                               '__gcc_except_tab',
                               '__got',
                               '__objc_const',
                              # '__objc_selrefs',
                               '__objc_data',
                               '__objc_ivar',
                                '__data'
                              ]

    print
    
    for idx in range(0,len(header.commands)):
        lc, cmd, data = header.commands[idx]
        
        if type(cmd) == mach_o.segment_command or type(cmd) == mach_o.segment_command_64:
            if checkStrInList(str(cmd.segname), safeRemoveList_segname):
                print '[+]Erasing segname', cmd.segname
                cmd.segname = '\0'

            for sect in data:
                if checkStrInList(str(sect.sectname), safeRemoveList_sectname):
                    print '[+]Erasing data for section', sect.sectname
                    sect.sectname = '\0'
                    sect.segname = '\0'
                    sect.addr = 0
                    sect.size = 4
                    sect.offset = os.path.getsize(sys.argv[1])
                    sect.align = 0
                    sect.reloff = 0
                    sect.nreloc = 0
                    sect.flags = 0
                    sect.reserved1 = 0
                    sect.reserved2 = 0

        if type(cmd) == mach_o.dyld_info_command:
            
            print '[+]Erasing part data for segment LC_LOAD_DYLINKER'
            cmd.weak_bind_off = 0
            cmd.weak_bind_size = 0
            cmd.export_off = 0
            cmd.export_size = 0
            

        if type(cmd) == mach_o.symtab_command:
            print '[+]Erasing data for segment LC_SYMTAB'
            
            cmd.symoff = 0
            cmd.nsyms = 0
            cmd.stroff = 0
            cmd.strsize = 0
            
        if type(cmd) == mach_o.dysymtab_command:
            print '[+]Erasing data for segment LC_DYSYMTAB'
            
            cmd.ilocalsym = 0
            cmd.nlocalsym = 0
            cmd.iextdefsym = 0
            cmd.nextdefsym = 0
            cmd.iundefsym = 0
            cmd.nundefsym = 0
            cmd.tocoff = 0
            cmd.ntoc = 0
            cmd.modtaboff = 0
            cmd.nmodtab = 0
            cmd.extrefsymoff = 0
            cmd.nextrefsyms = 0
            cmd.indirectsymoff = 0
            cmd.nindirectsyms = 0
            cmd.extreloff = 0
            cmd.nextrel = 0
            cmd.locreloff = 0
            cmd.nlocrel = 0
            
            
        if type(cmd) == mach_o.uuid_command:
            print '[+]Erasing data for segment LC_UUID'
            cmd.uuid = '\0'

        if type(cmd) == mach_o.linkedit_data_command:
            if lc.cmd == 0x26:
                
                print '[+]Erasing data for segment LC_FUNCTION_STARTS'
                cmd.dataoff = os.path.getsize(sys.argv[1])
                cmd.datassize = 4
                   
        #add more removeable load commands here

    print

    return

def checkStrInList(string,list):
    judge = 0
    for index in range(len(list)):
        if string.find(list[index]) == 0:
            judge += 1

    return judge

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Useage: python',sys.argv[0],'[executable path]'
        exit()
    
    if not os.path.exists(sys.argv[1]):
        print '#Error: File does not exist'
        exit()

    main(sys.argv[1])
    exit()
