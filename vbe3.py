#!/usr/bin/python3
'''Script retrieves some of the informations from vbe3 document and
interprets these as C language headers, which are printed to stdout.'''

# good enough script, some of the headers must be created by hand
# author: Jan Doležal <dolezj21 at fel.cvut.cz>
#         2014

from math import ceil
import sys
import os.path
from subprocess import call
import subprocess
debug = 0

# ## convert pdf to plain text ##
CONVERT_TOOL = 'pdf2txt' # pdf2txt is from PDFMiner pack
PDF_CONV_LOCATION = 'text/'
PDF_CONV_FILE = 'vbecore3.pdf'
TXT_OUT_FILE = 'vbecore3.txt'

# check that converting tool is installed
if call(['which', CONVERT_TOOL], stdout=subprocess.DEVNULL):
    sys.stderr.write("please, install pdf2txt tool from PDFMiner pack\n")
    sys.stderr.write("exiting...\n")
    sys.exit(0)

# if the pdf file was already converted to plain text, don't do it again
if os.path.isfile(PDF_CONV_LOCATION + '/' + TXT_OUT_FILE) != True:
    # retrieve all text - for gaining structures and function numbers
#    sys.stderr.write("converting " + PDF_CONV_FILE + ' ........')
#    sys.stderr.flush()
    command = CONVERT_TOOL + ' -o ' + PDF_CONV_LOCATION + '/' + TXT_OUT_FILE + ' -M 25 ' + PDF_CONV_LOCATION + '/' + PDF_CONV_FILE
    call(command.split())
#    sys.stderr.write(" DONE\n")

defineprefix = 'VBE_'
structprefix = 'VBE_'

def ceilColors(token):
    '''Ceils string number and returns ceiled number'''
    pos = token.find('.')
    if pos == -1:
        return token
    return str(ceil(float(token[:token.find('.')+2]))) + token[token.find('.')+2:]

def hTOx(hexh):
    '''Converts hexa number string from postfix h to prefix 0x'''
    return '0x'+hexh[:-1]

print('''/** 
 * @file 
 * 
 * @ingroup i386_pc386 
 * 
 * @brief VESA Bios Extension definitions. 
 */ 
 
 /* 
 * vbe3.h  - This file contains definitions for constants related to VBE. 
 *          More information can be found at 
 *      <http://http://www.vesa.org/vesa-standards/free-standards/> 
 *          VBE Core Function Standard V.3 may be found at 
 *      <http://www.vesa.org/wp-content/uploads/2010/12/thankspublic.htm> 
 * 
 * Copyright (C) 2014  Jan Doležal (dolezj21@fel.cvut.cz) 
 *                     CTU in Prague. 
 * 
 *  The license and distribution terms for this file may be 
 *  found in the file LICENSE in this distribution or at 
 *  http://www.rtems.org/license/LICENSE. 
 */''', sep = '') 
                    
print('\n#ifndef _VBE_H')
print('#define _VBE_H\n')

print('#include <stdint.h>\n')
print('#ifdef __cplusplus')
print('extern "C" {')
print('#endif /* __cplusplus */\n')

print('/* VBE RETURN STATUS */')


print('/* VBE Mode Numbers */')


textfile = open('text/vbecore3.txt', 'r') # later add input file as parameter

# ## find and prepare modes to be processed ##
modIdentifier = 'GRAPHICS TEXT'
grapModLines = []
textModLines = []
eatLines = 3
modesFound = 0
for line in textfile:
    if modesFound == 1 and eatLines != 0:
        eatLines -= 1
        continue
    if modesFound == 1:
        if ''.join(line.split()) == '':
            break
        # divide graphics from text modes
        tokens = line.split()
        if len(tokens) > 7: # contains graphic and text mode in one line
            grapModLines.append(' '.join(tokens[:int(len(tokens)/2)]))
            textModLines.append(' '.join(tokens[int(len(tokens)/2):]))
        else:
            grapModLines.append(' '.join(tokens))
    # find location of graphics modes according to modIdentifier
    line = ' '.join(line.split()) # replace multiple white spaces with single space
    if line == modIdentifier:
        modesFound = 1

print('\n/* Graphics modes */')
# ## create graphics modes headers ##
for line in grapModLines:
    tokens = line.split()
    # handle Special Mode
    nameSize = 18
    if tokens[0] == '81FFh':
        name = 'SpecialMode'
        print('#define ', defineprefix, name, (nameSize-len(name))*' ', hTOx(tokens[0]), sep='')
        break
    name = 'R' + tokens[2] + 'C' + ceilColors(tokens[3])
    print('#define ', defineprefix, name, (nameSize-len(name))*' ', hTOx(tokens[0]), sep='', end='')
    print((8-len(tokens[0]))*' ', '/* 15-bit mode, Resolution: ', tokens[2],
    ', Colors: ', tokens[3], ' ', tokens[4] if len(tokens)>4 else '', ' */', sep='')
    if tokens[1] != '-':
        name = 'b7R' + tokens[2] + 'C' + ceilColors(tokens[3])
        print('#define ', defineprefix, name, (nameSize-len(name))*' ', hTOx(tokens[1]), sep='', end='')
        print((8-len(tokens[1]))*' ', '/* 7-bit mode, Resolution: ', tokens[2],
        ', Colors: ', tokens[3], ' ', tokens[4] if len(tokens)>4 else '', ' */', sep='')

# ## create text modes headers ##
print('\n/* Text modes */')
for line in textModLines:
    tokens = line.split()
    name = 'C' + tokens[2] + 'R' + ceilColors(tokens[3])
    nameSize = 18
    print('#define ', defineprefix, name, (nameSize-len(name))*' ', hTOx(tokens[0]), sep='', end='')
    print((8-len(tokens[0]))*' ', '/* 15-bit mode, Columns: ', tokens[2],
    ', Rows: ', tokens[3], ' ', tokens[4] if len(tokens)>4 else '', ' */', sep='')
    if tokens[1] != '-':
        name = 'b7R' + tokens[2] + 'C' + ceilColors(tokens[3])
        print('#define ', defineprefix, name, (nameSize-len(name))*' ', hTOx(tokens[1]), sep='', end='')
        print((8-len(tokens[1]))*' ', '/* 7-bit mode, Columns: ', tokens[2],
        ', Rows: ', tokens[3], ' ', tokens[4] if len(tokens)>4 else '', ' */', sep='')


print('\n/* VBE function numbers */')

for line in textfile:
    line = ' '.join(line.split())
    try:
        if line.find('Function ') == 0 and line[11] == 'h' and line[13] == '-' and int(line[-3:-1]):
            pass
    except ValueError:
        shortcut = ''
        newLine = line
        slash = newLine.find('/')
        while slash != -1:
            newLine = newLine[:slash] + ' ' + newLine[slash+1:]
            slash = newLine.find('/')
        for i in range(3, len(newLine.split())):
            char3 = newLine.split()[i][:3]
            shortcut += char3 if char3[0] != '(' else ''
        print('#define ', defineprefix, shortcut, (19-len(shortcut))*' ', hTOx(newLine.split()[1]), sep='', end='  ')
        print('/*', line[line.find('-')+2:], '*/')

print('\n/* VBE subfunction numbers */')


print('\n/* *** Structures *** */')
# load file content for processing
textfile = open('text/vbecore3.txt', 'r') # later add input file as parameter
lines = textfile.readlines() # don't read huge files as whole!

# ## struc extraction ##
strucIdentifier = ' struc\n'
linenumber = 0
# list of potential lines
strucLines = []
for line in lines:
    if line[-7:] == strucIdentifier:
        strucLines.append(linenumber)
    linenumber += 1

# process potential strucs
for i in range(0, len(strucLines)):
    strucLine = strucLines[i]
    tokenizedLine = lines[strucLine].split()
    if len(tokenizedLine) != 2:
        continue
    endLine = strucLines[i+1] if i+1 < len(strucLines) else len(lines)
    linenumber = strucLine
    endString = tokenizedLine[0]+' ends\n'
    for j in range(strucLine+1, endLine):
        # replace multiple whitespaces with single space
        if ' '.join(lines[j].split())+'\n' != endString:
            continue
        else:
            strucLineEnds = j
            break
    else:
        continue
    # struc beginning is in variable strucLine and the end in var strucLineEnds
#    print(strucLine, ' ', strucLineEnds)
#    continue
    print('struct ', structprefix, lines[strucLine].split()[0], ' {', sep='')
#    reservedNumber = 0
    for j in range(strucLine+1, strucLineEnds):
        # requiring every line in struc has a comment -> semicolon
        if lines[j].find(';') == -1:
            continue
        tokens = lines[j].split()
        indentNameSize = 22
        print('    ', end='') # indent
#        reservedAddNum = 0
#        if tokens[0].find('Reserved') != -1:
#            reservedAddNum = 1
        if tokens[1] == 'db':
            print('uint8_t   ', tokens[0], sep='', end='')
#            (reservedNumber+=reservedNumber) if reservedAddNum else ''
            if tokens[2][len(tokens[2])-1] == '\'' and tokens[2][0] == '\'':
                print('[', len(tokens[2])-2, ']', ';', (indentNameSize-len(tokens[0])-2-len(str(len(tokens[2])-2)))*' ', sep='', end='')
            elif tokens[3] == 'dup':
                print('[', tokens[2], ']', ';', (indentNameSize-len(tokens[0])-2-len(str(tokens[2])))*' ', sep='', end='')
            else:
                print(';', (indentNameSize-len(tokens[0]))*' ', sep='' , end='')
        elif tokens[1] == 'dw':
            print('uint16_t  ', tokens[0], ';', (indentNameSize-len(tokens[0]))*' ', sep='', end='')
        elif tokens[1] == 'dd':
            if tokens[0].find('Ptr') != -1:
                if lines[j].find('String') != -1:
                    print('uint8_t  ', sep='', end='')
                else:
                    print('uint32_t ', sep='', end='')
                print('*', sep='', end='')
            else:
                print('uint32_t  ', sep='', end='')
            print(tokens[0], ';', (indentNameSize-len(tokens[0]))*' ', sep='', end='')
        else:
            if debug:
                print('REMOVE:', lines[j], '\n', end='')
            #print('    ', end='')
            #print((14+indentNameSize)*' ', sep='', end='')
        print('/*', lines[j][lines[j].find(';')+1:-1], '*/', end='')
        print()
    print('}', '__attribute__((__packed__))', ';', '\n')

print('\n/* VbeInfoBlock Capabilities */')
print('\n/* ModeInfoBlock ModeAttributes */')
print('\n/* ModeInfoBlock WinXAttributes */')
print('\n/* ModeInfoBlock MemoryModel */')
print('\n/* ModeInfoBlock DirectColorModeInfo */')
print('\n/* CRTCInfoBlock Flags */')

print('\n#ifdef __cplusplus')
print('}')
print('#endif /* __cplusplus */')

print('\n#endif /* _VBE_H */')

textfile.close()
