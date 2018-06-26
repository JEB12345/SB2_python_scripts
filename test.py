import signal
import sys  # exit command
import numpy as np

import hebi  # for the Hebi motors
from time import sleep
import scipy.io as sio

signal.signal(signal.SIGINT, lambda number, frame: sys.exit())

# Module Names on SUPERball V2
numModules = 25
SBModuleNames = (['M' + str(i + 1) for i in xrange(numModules)])

# Need to look into XML formatting for Hebi Gains
# sio.loadmat('defaultGains.mat')

lookup = hebi.Lookup() # Get table of all Hebi motors
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

var = raw_input('SB Motors {1} or All motors {0}? [0]: ')

while (1):
    if var == '1':
        positions = np.ones(GroupSB.size) * 0
        CmdSB.position = positions
        GroupSB.send_command(CmdSB)
        sleep(2)
        positions = np.ones(GroupSB.size) * 3.14
        CmdSB.position = positions
        GroupSB.send_command(CmdSB)
        sleep(2)
    else:
        positions = np.ones(GroupAll.size) * 0
        CmdAll.position = positions
        GroupAll.send_command(CmdAll)
        sleep(2)
        positions = np.ones(GroupAll.size) * 3.14
        CmdAll.position = positions
        GroupAll.send_command(CmdAll)
        sleep(2)

