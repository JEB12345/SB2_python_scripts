import signal
import sys  # exit command
import numpy as np
import csv
from os import system

######################## Setup Code ###################################

import hebi  # for the Hebi motors
from time import sleep
import scipy.io as sio

signal.signal(signal.SIGINT, lambda number, frame: sys.exit())

# Module Names on SUPERball V2
numModules = 24
SBModuleNames = (['M' + str(i + 1).zfill(2) for i in xrange(numModules)])

# Need to look into XML formatting for Hebi Gains
# sio.loadmat('defaultGains.mat')

lookup = hebi.Lookup()  # Get table of all Hebi motors
sleep(2)  # gives the Lookup process time to discover modules

# Displays the Hebi modules found on the network
print('Modules found on the network:')

for entry in lookup.entrylist:
    print('{0} | {1}'.format(entry.family, entry.name))

# print('\n')

var = raw_input('Were any modules found? [y/N]: \n')
if var == 'y':
    print('\nYay!\n')
elif var == 'Y':
    print('\nYay!\n')
else:
    print('\nNONE FOUND!\n')
    sys.exit()

GroupAll = lookup.get_group_from_family('*')
infoTableAll = GroupAll.request_info()

temp_SBModuleNames = []
print('All motors found:')
for module in xrange(len(infoTableAll.name)):
    print(infoTableAll.name[module])
    if infoTableAll.name[module] in SBModuleNames:
        temp_SBModuleNames.append(infoTableAll.name[module])

GroupSB = lookup.get_group_from_names('*', temp_SBModuleNames)
infoTableSB = GroupSB.request_info()

print('SUPERball Motors Found:')
for module in xrange(len(infoTableSB.name)):
    print(infoTableSB.name[module])

print('')

# Set command stuctures for All and SB motors
CmdAll = hebi.GroupCommand(GroupAll.size)
CmdSB = hebi.GroupCommand(GroupSB.size)

######################## Actual Code ###################################
GroupSB.command_lifetime = 0.0
CmdSB.position = np.ones(GroupSB.size) * 3.0
print(CmdSB.position)
GroupSB.send_command(CmdSB)

raw_input('Pause 1')

# Set Gains for the packing controller
CmdSB.position_kp = np.ones(GroupSB.size) * 1
CmdSB.effort_kp = np.ones(GroupSB.size) * 0.2
CmdSB.effort_ki = np.ones(GroupSB.size) * 0.01

CmdSB.effort_max_output = np.ones(GroupSB.size) * 3.0
CmdSB.effort_min_output = np.ones(GroupSB.size) * -3.0

CmdSB.position = np.ones(GroupSB.size) * 0.0

GroupSB.send_command(CmdSB)

raw_input('Pause 2')

# Setup the star packing set points
SBtransform = np.array([[19, 20, 21, 15, 8, 2, 14, 9, 4, 13, 7, 6, 1, 18, 12, 3, 17, 11, 5, 16, 10, 23, 24, 22],
                        [18, 3, 13, 22, 4, 15, 7, 14, 20, 9, 17, 1, 21, 2, 11, 8, 16, 24, 10, 19, 5, 12, 23, 6]])

slope = np.array(
    [-1.13272388059701, -1.14042158304600, -1.17338351598342, -1.06945782765140, -1.11349186621372, -1.14497930796643,
     -1.12547082818874, -1.08895423738307, -1.08169633323703, -1.12573961622541, -1.12234550720277, -1.12037814814265,
     -1.11246037551817, -1.11100024243662, -1.10440750557301, -1.13555410889649, -1.11643316697733, -1.09564556365700,
     -1.12041645665323, -1.13072891187365, -1.14080189055838, -1.17501817049112, -1.13024261777840, -1.10180013546606])
offset = np.array(
    [108.254000000000, 100.192000000000, 124.433000000000, 101.073000000000, 110.140000000000, 114.641000000000,
     108.872000000000, 109.739000000000, 104.905000000000, 111.072000000000, 113.721000000000, 106.830000000000,
     114.410000000000, 108.207000000000, 94.9220000000000, 114.409000000000, 109.408000000000, 110.794000000000,
     107.684000000000, 104.415000000000, 105.778000000000, 105.691000000000, 109.936000000000, 106.484000000000]) + 5
# offset = [x+5 for x in offset]

i = np.argsort(SBtransform[0])
test0 = SBtransform[0][i]
test1 = SBtransform[1][i]
SBtransformSort = np.array([test0, test1])

# As of now, you have to run the program with the CSV file open :-/
unpackingLenTen = []
with open('hex_pack_len_ten_prestress.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
        unpackingLenTen.append(row)

    print('Reay...\n')

steps = [len(unpackingLenTen) - 1] + range(len(unpackingLenTen) - 2, 100, -1)
for j in steps:
    current_lengths = unpackingLenTen[j][0:24]
    current_tensions = unpackingLenTen[j][24:]

    current_tensions = np.array([400.0 if i > 400.0 else i for i in current_tensions])
    current_moments = current_tensions * 0.006

    newRestLengths = np.array([current_lengths[i - 1] for i in SBtransformSort[1]])
    newMoments = np.array([current_moments[i - 1] for i in SBtransformSort[1]])

    cmdMotorPositions = (100 * newRestLengths) * slope + offset
    print(cmdMotorPositions)

    CmdSB.position = cmdMotorPositions
    CmdSB.effort = newMoments * 0.2

    GroupSB.send_command(CmdSB)
    sleep(0.025)

print('DOWN')

raw_input('Should bring back up')

CmdSB.position = np.ones(GroupSB.size) * 0.0
GroupSB.send_command(CmdSB)

sleep(1)

sys.exit()
