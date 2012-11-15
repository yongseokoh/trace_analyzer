#!/usr/bin/python 

import sys 
from boomslang import *
from numpy import *
import numpy as np

def read_trace(filename, outputname):

	prev_arrival = 0.0
	inter_arrival = 0.0
	inter_count = 0;

	write_count = 0
	read_count = 0
	total_count = 0
	pagesize = 8

	write_req_size = 0
	write_req_count = 0
	read_req_size = 0
	read_req_count = 0

	total_wss = {}
	write_wss = {}
	read_wss = {}

	write_reqs = []
	read_reqs = []
	write_cur_count = 0
	read_cur_count = 0
	start_arrival_time = 0.0

	try: 
		file = open(filename)
		for s in file:
		
			w = s.split()

			arrivetime = float(w[0])
			devno =  int(w[1])
			blkno = int(w[2])
			bcount = int(w[3])
			readflag = int(w[4])

			inter_arrival += (arrivetime-prev_arrival)
			prev_arrival = inter_arrival
			inter_count += 1

			# request rate 
			if readflag:
				read_cur_count+=1
			else:
				write_cur_count+=1

			if (arrivetime - start_arrival_time) >= 60000.0:
				start_arrival_time = arrivetime

				write_reqs.append(write_cur_count)
				read_reqs.append(read_cur_count)

				write_cur_count = 0
				read_cur_count = 0

				
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

				pno = (blkno + b)/8  

				if total_wss.has_key(pno) != True:
					total_wss[pno] = 1 
				else:
					total_wss[pno] += 1

				if readflag == 0:

					write_count+=1
					if write_wss.has_key(pno) != True:
						write_wss[pno] = 1 
					else:
						write_wss[pno] += 1

				else:

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


#print write_reqs
#	print read_reqs

	total_wss_size = len(total_wss)
	read_wss_size = len(read_wss)
	write_wss_size = len(write_wss)
	giga = (1024*256)

	str = " I/O Statistics \n" 
	str += " Total Working Set\t %d,\t %.2f GB\n" %(total_wss_size, double(total_wss_size)/giga) 
	str += " Read Working Set\t %d,\t %.2f GB\n" %(read_wss_size, double(read_wss_size)/giga) 
	str += " Write Working Set\t %d,\t %.2f GB\n" %(write_wss_size, double(write_wss_size)/giga) 
	str += "\n"

	str += " Total Pages\t %d,\t %.2f GB\n" % (total_count, double(total_count)/giga)
	str += " Read Pages\t %d,\t %.2f GB\n" %(read_count, double(read_count)/giga) 
	str += " Write Pages\t %d,\t %.2f GB\n" %(write_count, double(write_count)/giga)
	str += " Read Ratio\t %.2f\n" %(double(read_count)/double(total_count))
	str += "\n"

	str += " Average Read Req Size\t %.2f KB\n" %(double(read_req_size)/read_req_count*4)
	str += " Average Write Req Size\t %.2f KB\n" %(double(write_req_size)/write_req_count*4)
	str += "\n"

	str += " Inter Arrival Time\t %f ms\n" %(double(inter_arrival)/inter_count)

	print str 

	try:
		file = open(outputname, 'w')
		file.write(str)
		file.close()
	except IOError:
		print >> sys.stderr, " cannot open file "


	freqlist_write = write_wss.values()
	freqlist_read = read_wss.values()
	
	return freqlist_write, freqlist_read, write_reqs, read_reqs


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

def draw_linegraph2(xaxis, yaxis, xlabel, ylabel, label,  xlogscale, ylogscale, graphname):

	linestyle = [ "-", "--"]
	color = ["red", "blue"]

	plot = Plot()

	for i in range(0, len(xaxis)):
		line = Line()
		line.xValues = xaxis[i]
		line.yValues = yaxis[i]
		line.lineStyle = linestyle[i]
		line.color = color[i]
		line.label = label[i]
		plot.add(line)

	plot.xLabel = xlabel
	plot.yLabel = ylabel 
	plot.logx = xlogscale
	plot.logy = ylogscale
	plot.hasLegend()
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


freqlist_write, freqlist_read, write_reqs, read_reqs  = read_trace(filename, graphname + "_iostat.txt")
print "Complete read trace", filename

xaxis, yaxis = make_x_y_blkno(freqlist_write, 1)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Cumulative Write Frequency", False, False,  graphname + "_cdf" + ".pdf")

xaxis, yaxis = make_x_y_blkno(freqlist_write, 0)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Write Frequency", False, False,  graphname + "_frequency" + ".pdf")

xaxis = []
xaxis.append([i for i in range(0, len(write_reqs))])
xaxis.append([i for i in range(0, len(write_reqs))])
yaxis = []
yaxis.append(write_reqs)
yaxis.append(read_reqs)
label = ["Write", "Read"]
draw_linegraph2(xaxis, yaxis, "Time (Min.)", "Request Rate", label, False, False,  graphname + "_req_rate" + ".pdf")

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
