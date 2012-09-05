#!/usr/bin/python 

import sys 
from boomslang import *
from numpy import *
import numpy as np

def read_trace(filename):

	blklist_write = []
	blklist_read = []
	lifelist = []

	write_count = 0
	read_count = 0
	total_count = 0
	pagesize = 8

	try: 
		file = open(filename)
		for s in file:
		
			w = s.split()

			arrivetime =float(w[0])
			devno =  int(w[1])
			blkno = int(w[2])
			bcount = int(w[3])
			readflag = int(w[4])
				
			if bcount % pagesize:
				bcount -= (bcount % pagesize)
				bcount += pagesize

			for b in range(0, bcount, pagesize):


				if readflag == 0:
					pno = (blkno + b)/8  
					blklist_write.append(pno)
					lifelist.append(arrivetime)
					write_count+=1
				else:
					blklist_read.append(pno)
					read_count+=1

				total_count += 1

		#print "list len = ", len(blklist)

		file.close()

	except IOError:
		print >> sys.stderr, " Cannot open file "

	blklist_write.sort()
	print " I/O Statistics " 
	print " Total Read Pages %d, %.2f MB" %(read_count, double(read_count)/256) 
	print " Total Write Pages %d, %.2f MB " %(write_count, double(write_count)/256)
	print " Total Pages %d, %.2f MB" % (total_count, double(total_count)/256)
	print " Read Ratio %.2f" %(double(read_count)/double(total_count))
	print ""

	freq_list_write = make_freq_list(blklist_write)
	freq_list_read = make_freq_list(blklist_read)
	print " Write Working Set %d, %.2f MB" %(len(freq_list_write), double(len(freq_list_write))/256) 
	print " Read Working Set %d, %.2f MB" %(len(freq_list_read), double(len(freq_list_read))/256) 


#print "sort" 
	return blklist_write, lifelist

def make_x_y_lifefreq(blklist, lifelist):

	dict = {}
	freq = []
	for i in range(len(blklist)):
		dict.setdefault(blklist[i], []).append(lifelist[i])

	avg_time = []
	for key in dict.iterkeys():
		timelist = dict[key]
		avg_time.append(np.average(timelist)/1000)
		freq.append(len(timelist))

	
	avg_time = np.array(avg_time)
	xarg = np.argsort(avg_time)
	freq = np.array(freq)
	freq = np.take(freq, xarg)
	avg_time = np.sort(avg_time)

#	print avg_time.tolist()

#	sum = np.sum(freq)
#	freq = freq.cumsum() * float(100) / float(sum)

#print freq

	if len(lifelist) > 100000:
		width = len(lifelist)/1000
	else:
		width = 1

	yaxis = []
	xaxis = []
	for i in range(0, len(freq), width):
		xaxis.append(avg_time[i])
		yaxis.append(freq[i])

	return xaxis, yaxis

def make_x_y_life(blklist, lifelist):

	dict = {}
	for i in range(len(blklist)):
		dict.setdefault(blklist[i], []).append(lifelist[i])

	avg_time = []
	for key in dict.iterkeys():
		timelist = dict[key]
		avg_time.append(np.average(timelist)/1000)

	lifelist_sort = np.sort(avg_time, axis = 0)

	print avg_time[0], avg_time[len(avg_time)-1]

#sum = np.sum(lifelist_sort)
#	lifelist = lifelist_sort.cumsum() * float(100) / sum

	if len(lifelist) > 10000:
		width = len(lifelist)/100
	else:
		width = 1

	yaxis = []
	xaxis = []
	for i in range(0, len(lifelist_sort), width):
		xaxis.append(lifelist_sort[i])
		yaxis.append(float(i)*100/len(lifelist_sort))

	return xaxis, yaxis


def make_freq_list(blklist):
	blklist_bincount = np.bincount(blklist)
#	del blklist

	blklist_sort = np.sort(blklist_bincount, axis = 0)
#	print " sort "
#	del blklist_bincount
	blklist = blklist_sort[::-1]
#	print " reverse "

#	del blklist_sort

	lastindex = 0
	for i in range(len(blklist)):
		if blklist[i] == 0:
			lastindex = i
			break
		
	blklist = blklist[0:lastindex-1]

	return blklist

def make_x_y_blkno(blklist, cumulative):

	blklist = make_freq_list(blklist)
#	print "find last "

	if cumulative:
		sum = np.sum(blklist)
		blklist = blklist.cumsum() * float(100) / sum
	else:
		blklist = blklist

	if len(blklist) > 10000:
		width = len(blklist)/100
	else:
		width = 1

	xaxis = []
	yaxis = []
	for i in range(0, len(blklist), width):
		xaxis.append(float(i)/256)
		yaxis.append(blklist[i])

	return xaxis, yaxis

def draw_linegraph(xaxis, yaxis, xlabel, ylabel, xlogscale, ylogscale, graphname):

	plot = Plot()

	line = Line()
	line.xValues = xaxis
	line.yValues = yaxis 

	plot.add(line)
	plot.xLabel = xlabel
	plot.yLabel = ylabel 
	plot.logx = xlogscale
	plot.logy = ylogscale
	plot.save(graphname)

	print " Save " + graphname



# main program 
if len(sys.argv) != 3 :
	print sys.stderr, " Invalid args "  
	exit(1)

print sys.argv[1]


filename = sys.argv[1] 
graphname = sys.argv[2]


blklist, lifelist = read_trace(filename)
print "Complete read trace", filename

xaxis, yaxis = make_x_y_blkno(blklist, 1)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Cumulative Write Frequency", False, False,  graphname + "_cdf" + ".png")

xaxis, yaxis = make_x_y_blkno(blklist, 0)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Cumulative Write Frequency", False, False,  graphname + "_frequency" + ".png")

#xaxis, yaxis = make_x_y_life(blklist, lifelist)
#draw_linegraph(xaxis, yaxis, "Block Life Time (sec)", "Pecent Blocks", False, False, graphname + "_lifetime" + ".png")

#xaxis, yaxis = make_x_y_lifefreq(blklist, lifelist)
#draw_linegraph(xaxis, yaxis, "Block Life Time (sec)", "Update Count", False, False, graphname + "_lifefreq" + ".png")


print " EOP " 

