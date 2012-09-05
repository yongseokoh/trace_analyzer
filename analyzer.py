#!/usr/bin/python 

import sys 
from boomslang import *
from numpy import *
import numpy as np

def read_trace(filename):

#blklist_write = []
#	blklist_read = []
#lifelist = []

	write_count = 0
	read_count = 0
	total_count = 0
	pagesize = 8

	write_req_size = 0
	write_req_count = 0
	read_req_size = 0
	read_req_count = 0

	write_wss ={}
	read_wss = {}

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

			if readflag == 0:
				write_req_size += (bcount/pagesize)
				write_req_count += 1
			else:
				read_req_size += (bcount/pagesize)
				read_req_count += 1

			for b in range(0, bcount, pagesize):

				if readflag == 0:
					pno = (blkno + b)/8  
#blklist_write.append(pno)
#lifelist.append(arrivetime)
					write_count+=1

					if write_wss.has_key(pno) != True:
						write_wss[pno] = 1 
					else:
						write_wss[pno] += 1

#print write_wss[pno]
				else:
#blklist_read.append(pno)
					read_count+=1

					if read_wss.has_key(pno) != True:
						read_wss[pno] = 1 
					else:
						read_wss[pno] += 1

				total_count += 1

		#print "list len = ", len(blklist)

		file.close()

	except IOError:
		print >> sys.stderr, " Cannot open file "

#blklist_write.sort()
	print " I/O Statistics " 
	print " Total Read Pages %d, %.2f MB" %(read_count, double(read_count)/256) 
	print " Total Write Pages %d, %.2f MB " %(write_count, double(write_count)/256)
	print " Total Pages %d, %.2f MB" % (total_count, double(total_count)/256)
	print " Read Ratio %.2f" %(double(read_count)/double(total_count))
	print ""

#freq_list_write = make_freq_list(blklist_write)
#	freq_list_read = make_freq_list(blklist_read)
	read_wss_size = len(read_wss)
	write_wss_size = len(write_wss)

	print " Write Working Set %d, %.2f MB" %(write_wss_size, double(write_wss_size)/256) 
	print " Read Working Set %d, %.2f MB" %(read_wss_size, double(read_wss_size)/256) 

	print " Average Read Req Size %.2f KB" %(double(read_req_size)/read_req_count*4)
	print " Average Write Req Size %.2f KB" %(double(write_req_size)/write_req_count*4)
	print ""


	freqlist_write = write_wss.values()
	freqlist_read = read_wss.values()
	
	return freqlist_write, freqlist_read


def make_x_y_blkno(freqlist, cumulative):

	freqlist = np.array(freqlist)
	freqlist = np.sort(freqlist, axis = 0)
	freqlist = freqlist[::-1]

	if cumulative:
		sum = np.sum(freqlist)
		freqlist = freqlist.cumsum() * float(100) / sum
	else:
		freqlist = freqlist

	if len(freqlist) > 10000:
		width = len(freqlist)/100
	else:
		width = 1

	xaxis = []
	yaxis = []
	for i in range(0, len(freqlist), width):
		xaxis.append(float(i)/256)
		yaxis.append(freqlist[i])

	return xaxis, yaxis

def draw_linegraph(xaxis, yaxis, xlabel, ylabel, xlogscale, ylogscale, graphname):

	plot = Plot()

	line = Line()
	line.xValues = xaxis
	line.yValues = yaxis 
	line.lineStyle = "-"
	line.color = "red"

	plot.add(line)
	plot.xLabel = xlabel
	plot.yLabel = ylabel 
	plot.logx = xlogscale
	plot.logy = ylogscale
	plot.setDimensions(8, 6, 100)
	plot.save(graphname)

	print " Save " + graphname



# main program 
if len(sys.argv) != 3 :
	print sys.stderr, " Invalid args "  
	exit(1)

print sys.argv[1]


filename = sys.argv[1] 
graphname = sys.argv[2]


freqlist_write, freqlist_read = read_trace(filename)
print "Complete read trace", filename

xaxis, yaxis = make_x_y_blkno(freqlist_write, 1)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Cumulative Write Frequency", False, False,  graphname + "_cdf" + ".pdf")

xaxis, yaxis = make_x_y_blkno(freqlist_write, 0)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Write Frequency", False, False,  graphname + "_frequency" + ".pdf")



print " EOP " 

""""
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
"""

"""
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
"""
