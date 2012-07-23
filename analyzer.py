#!/usr/bin/python 

import sys 
from boomslang import *
from numpy import *
import numpy as np

if len(sys.argv) is 3 :
	print sys.stderr, " Invalid args "  
	exit(1)

print sys.argv[1]


filename = sys.argv[1] 


blklist = []

try: 
	file = open(filename)
	for s in file:
	
		w = s.split()

		arrivetime =float(w[0])
		devno =  int(w[1])
		blkno = int(w[2])
		bcount = int(w[3])
		readflag = int(w[4])
			
		if readflag == 1:
			continue
#print  w 
		for b in range(0, bcount, 8):
			blklist.append(blkno+b)
#print blkno + b

	print "list len = ", len(blklist)
	file.close()

except IOError:
	print >> sys.stderr, " Cannot open file "

#blklist = np.sort(blklist, axis = 0)

blklist = np.bincount(blklist)
blklist = np.sort(blklist, axis = 0)
blklist = blklist[::-1]

lastindex = 0
for i in range(len(blklist)):
	if blklist[i] == 0:
		lastindex = i
		break
	
blklist = blklist[0:lastindex-1]

print blklist

sum = np.sum(blklist)
blklist = blklist.cumsum() * float(100) / sum
print blklist
print blklist[0:100]

xaxis = []
yaxis = []
for i in range(len(blklist)):
	xaxis.append(float(i)/256)
	yaxis.append(blklist[i])

print len(xaxis), len(yaxis)
print len(blklist), " Pages "
print len(blklist) / 256 / 1024, " GB "
#print xaxis
#print yaxis


plot = Plot()
line = Line()
line.xValues = xaxis
line.yValues = yaxis 
plot.add(line)
plot.xLabel = "MB"
plot.yLabel = "Pecent"
plot.save("line.png")

