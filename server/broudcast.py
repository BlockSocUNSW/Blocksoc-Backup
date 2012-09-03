#!/usr/bin/python

import os
import sys
screens = ['mc_fluid','mc_creative','mc_experiment','mc_tekkit_restricted','mc_tekkit_creative']

if len(sys.argv) != 2:
    print "Usage: broudcast.py [string to broudcast to servers]"
    sys.exit(0) 
print "Command: ", sys.argv[1]
for s in screens:
    print "Sending to: ", s
    cmd = "screen -S " + s + " -p 0  -X stuff \"\n" + sys.argv[1] + "\n\""
    os.system(cmd)
