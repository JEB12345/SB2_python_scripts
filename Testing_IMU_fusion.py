import scipy.io as scio
import sys
import numpy as np
import timeit
import hebi
from time import sleep
import math as m

# IMU Fusion import
rate = 5 #Hz
sys.path.append('/usr/local/home/jebruce/Projects/Python/micropython-fusion/')
from fusion import Fusion

def timeDiff(end, start):
	 return end - start

fuse = Fusion(timeDiff)

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
motorCount = 0
print('All motors found:')
for module in xrange(len(infoTableAll.name)):
    print(infoTableAll.name[module])
    if infoTableAll.name[module] in SBModuleNames:
        temp_SBModuleNames.append(infoTableAll.name[module])
        motorCount = motorCount + 1

GroupSB = lookup.get_group_from_names('*', temp_SBModuleNames)
infoTableSB = GroupSB.request_info()

print('SUPERball Motors Found:')
for module in xrange(len(infoTableSB.name)):
    print(infoTableSB.name[module])

print('Number of SB Motors:')
print(motorCount)
print('')

# Set command stuctures for SB motors
CmdSB = hebi.GroupCommand(GroupSB.size)



var = raw_input('Press y to continue, q to exit: \n')
if var == 'y':
        print('\nYay!\n')
elif var == 'Y':
        print('\nYay!\n')
else:
        print('\nBye!\n')
        sys.exit()

## Feedback Setup
fbk = hebi.GroupFeedback(GroupSB.size)
GroupSB.feedback_frequency = 200.0

#x = -cos(yaw)sin(pitch)sin(roll)-sin(yaw)cos(roll)
#y = -sin(yaw)sin(pitch)sin(roll)+cos(yaw)cos(roll)
#z =  cos(pitch)sin(roll)

tStart = 0
tStop = 0
count = 0
while(1):
	fbk = GroupSB.get_next_feedback(reuse_fbk=fbk)
	tStop = timeit.default_timer()
	#ts = tStop - tStart
	fuse.update_nomag(fbk.accelerometer[0],fbk.gyro[0],tStop)
	tStart = timeit.default_timer()

	x = -m.cos(fuse.heading)*m.sin(fuse.pitch) - m.sin(fuse.heading)*m.cos(fuse.roll)
	y = -m.sin(fuse.heading)*m.sin(fuse.pitch) + m.cos(fuse.heading)*m.cos(fuse.roll)
	z = m.cos(fuse.pitch)*m.sin(fuse.roll)

	if count % 50 == 0:
		print("ts: {:7.3f}".format(tStop))
		print("Heading, Pitch, Roll: {:7.3f} {:7.3f} {:7.3f}".format(fuse.heading, fuse.pitch, fuse.roll))
		print("X, Y, Z: {:7.3f} {:7.3f} {:7.3f}".format(x, y, z))
		print("Accel: {:7.3f} {:7.3f} {:7.3f}".format(fbk.accelerometer[0][0], fbk.accelerometer[0][1], fbk.accelerometer[0][2]))
		print("Gyro: {:7.3f} {:7.3f} {:7.3f}".format(fbk.gyro[0][0], fbk.gyro[0][1], fbk.gyro[0][2]))
	sleep(1/rate)
	count += 1
