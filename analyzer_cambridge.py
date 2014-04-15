#!/usr/local/bin/python 

#Workload Analyzer for Disksim Traces
#This program was written by Yongseok Oh (ysoh@uos.ac.kr), University of Seoul

# Copyright 2012 Yongseok Oh
# This file is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details. 
# You should have received a copy of the GNU General Public License
# along with this file. If not, see http://www.gnu.org/licenses/. 

import sys 
from boomslang import *
from numpy import *
import numpy as np

def read_write_wss2(blkno, bcount, readflag, pagesize, readwrite_wss, write_wss, read_wss):
	for b in range(0, bcount, pagesize):

		pno = (blkno + b)/8  

		if readwrite_wss.has_key(pno) == True:
			readwrite_wss[pno] += 1
		else:
			if readflag == 0:
				if read_wss.has_key(pno) == True:
					del read_wss[pno]
					if readwrite_wss.has_key(pno) != True:
						readwrite_wss[pno] = 1 
					else:
						readwrite_wss[pno] += 1
						print "debug"
				else:
					if write_wss.has_key(pno) != True:
						write_wss[pno] = 1 
					else:
						write_wss[pno] += 1
			else: # read case
				if write_wss.has_key(pno) == True:
					del write_wss[pno]
					if readwrite_wss.has_key(pno) != True:
						readwrite_wss[pno] = 1 
					else:
						readwrite_wss[pno] += 1
						print "debug"
				else:

					if read_wss.has_key(pno) != True:
						read_wss[pno] = 1 
					else:
						read_wss[pno] += 1


def read_write_wss(blkno, bcount, readflag, pagesize, total_wss, write_wss, read_wss):
	for b in range(0, bcount, pagesize):

		pno = (blkno + b)/8  

		if total_wss.has_key(pno) != True:
			total_wss[pno] = 1 
		else:
			total_wss[pno] += 1

		if readflag == 0:

			if write_wss.has_key(pno) != True:
				write_wss[pno] = 1 
			else:
				write_wss[pno] += 1

		else:

			if read_wss.has_key(pno) != True:
				read_wss[pno] = 1 
			else:
				read_wss[pno] += 1

def read_trace(filename, outputname):

	disk_size = 1024*1024*1024*1024
	disk_size_sectors = disk_size / 512

	print " Scale Down blkno with disk size %dGB" % (disk_size/1024/1024/1024)


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

	all_req_size = 0
	all_req_count = 0
	
	max_req_size = 0

	total_wss = {}
	write_wss = {}
	read_wss = {}

	write_only_wss = {}
	read_only_wss = {}
	readwrite_wss = {}

	write_reqs = []
	read_reqs = []

	write_cur_count = 0
	read_cur_count = 0
	start_arrival_time = 0.0

	sector_size = 512
	page_size = 4096
	sector_per_page = page_size/sector_size
	time_unit = 10000
	start=0.0

	seq_start = 0
	seq_length = 0

	last_arrival_time = 0.0

	block_offset_total = 0.0
	block_offset_count = 0
	block_offset_last = 0

	try: 
		file = open(filename)
		for s in file:
		
			token=s.split(',')	
			if(start==0):
				start=float(token[0]) / time_unit	
			arrivetime = float(token[0]) / time_unit - start  #ms
			last_arrival_time = arrivetime
			devno =  0 #fix
			
			page_align = 0	
			if page_align == 1:
				pno = long(token[4])/page_size
				pcount = long(token[5])/page_size
				if(long(token[5])%page_size):
					pcount+=1

				blkno = pno*sector_per_page # sector(512byte)
				bcount = pcount*sector_per_page #sector count
			else:
				blkno = long(token[4])/sector_size
				bcount = long(token[5])/sector_size

			if (seq_length == 0) or (seq_start + seq_length != blkno):
				seq_start = blkno
				seq_length = bcount
			else:
				seq_length += bcount

#if seq_length >= 128*1024/sector_size:
#				continue

			#if int(token[4]) > int(4*1024*1024*1024):
			#	print "Greater than 4GB ", int(token[4])/(1024*1024*1024)
			readflag = 1 # read(1), write(0)
			if token[3]=="Write":
				readflag=0

			#print blkno
#			data = "%f\t%d\t%d\t%d\t%d\n" % (arrivetime, devno, blkno, bcount, readflag)
#			print data

#arrivetime = float(w[0])
			devno =  0

			if bcount > max_req_size:
				max_req_size = bcount 

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

			all_req_size += (bcount/pagesize)
			all_req_count += 1
	

			for b in range(0, bcount, pagesize):
				pno = (blkno + b)/8  
				total_count += 1
				if readflag == 0:
					write_count+=1
				else:
					read_count+=1

			block_offset_total += abs(blkno-block_offset_last)
			block_offset_count += 1
			block_offset_last = blkno

			read_write_wss(blkno, bcount, readflag, pagesize, total_wss, write_wss, read_wss)
			read_write_wss2(blkno, bcount, readflag, pagesize, readwrite_wss, write_only_wss, read_only_wss)

		file.close()

	except IOError:
		print >> sys.stderr, " Cannot open file "


#print write_reqs
#	print read_reqs

	total_wss_size = len(total_wss)
	read_wss_size = len(read_wss)
	write_wss_size = len(write_wss)
	giga = (1024*256)

	readonly_wss_size = len(read_only_wss)
	writeonly_wss_size = len(write_only_wss)
	readwrite_wss_size = len(readwrite_wss)

	str = " I/O Statistics \n" 
	str += " Total Working Set\t %8d,\t %.3f GB\n" %(total_wss_size, double(total_wss_size)/giga) 
	str += "  Read Working Set\t %8d,\t %.3f GB\n" %(read_wss_size, double(read_wss_size)/giga) 
	str += " Write Working Set\t %8d,\t %.3f GB\n" %(write_wss_size, double(write_wss_size)/giga) 
	str += "\n"

	str += " Total Pages\t %8d,\t %.3f GB\n" % (total_count, double(total_count)/giga)
	str += "  Read Pages\t %8d,\t %.3f GB\n" %(read_count, double(read_count)/giga) 
	str += " Write Pages\t %8d,\t %.3f GB\n" %(write_count, double(write_count)/giga)
	str += "\n"

	str += " Read Ratio\t %.3f\n" %(double(read_count)/double(total_count))
	str += "\n"
	str += " Read  Only Working Set\t %8d,\t %.3f GB\n" %(readonly_wss_size, double(readonly_wss_size)/giga) 
	str += " RW   Mixed Working Set\t %8d,\t %.3f GB\n" %(readwrite_wss_size, double(readwrite_wss_size)/giga) 
	str += " Write Only Working Set\t %8d,\t %.3f GB\n" %(writeonly_wss_size, double(writeonly_wss_size)/giga) 
	str += "\n"

	ronly_list = np.array(read_only_wss.values())
	wonly_list = np.array(write_only_wss.values())
	rw_list = np.array(readwrite_wss.values())


	str += " Read  Only Pages\t %8d,\t %.3f GB\n" %(ronly_list.sum(), 
			double(ronly_list.sum())/giga) 
	str += " RW   Mixed Pages\t %8d,\t %.3f GB\n" %(rw_list.sum(), 
			double(rw_list.sum())/giga) 
	str += " Write Only Pages\t %8d,\t %.3f GB\n" %(wonly_list.sum(), 
			double(wonly_list.sum())/giga) 


	str += "\n"
	str += " Average Read Req Size\t %.3f KB\n" %(double(read_req_size)/read_req_count*4)
	str += " Average Write Req Size\t %.3f KB\n" %(double(write_req_size)/write_req_count*4)
	str += " Average All Req Size\t %.3f KB\n" %(double(all_req_size)/all_req_count*4)
	str += "\n"

	str += " Inter Arrival Time\t %f ms\n" %(double(inter_arrival)/inter_count)

	str += " Max Req Size %f MB \n" %(double(max_req_size)/2/1024)
	str += " Avg Block Offset %f (sectors) \n" %(double(block_offset_total)/block_offset_count)
	str += " Duration %f Hour (%f Day)\n" %(double(last_arrival_time)/1000/3600, double(last_arrival_time)/1000/3600/24)

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

def save_rawdata(xaxis, yaxis, xlabel, ylabel, graphname):

	print " Save " + graphname

	data = "#%s\t\%s\n" %( xlabel, ylabel )

	for i in range(len(xaxis)):
		data +=  "%s\t%s\n" %( xaxis[i], yaxis[i] )

	try:
		wf = open(graphname, 'w')
		wf.write(data)
		wf.close()
	except IOError:
		print >> sys.stderr, " Cannot open file "


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
	plot.setDimensions(4, 3, 100)
	plot.save(graphname)

	print " Save " + graphname


def draw_linegraph2(xaxis, yaxis, xlabel, ylabel, label,  xlogscale, ylogscale, graphname, xsize, ysize):

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
	plot.setDimensions(xsize, ysize, 100)
	plot.save(graphname)

	print " Save " + graphname



# main program 
if len(sys.argv) != 3 :
	print sys.stderr, " Invalid args "  
	exit(1)

print "Trace File = ", sys.argv[1]


filename = sys.argv[1] 
graphname = sys.argv[2]


freqlist_write, freqlist_read, write_reqs, read_reqs  = read_trace(filename, graphname + "_iostat.txt")
print "Complete read trace", filename

xaxis, yaxis = make_x_y_blkno(freqlist_write, 1)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Cumulative Write Frequency", False, False,  graphname + "_write_cdf" + ".pdf")
save_rawdata(np.array(xaxis)/1024, yaxis, "Block Ragnes (GB)", "Cumulative Write Frequency", graphname + "_wfreq_rawdata.txt" )

xaxis, yaxis = make_x_y_blkno(freqlist_write, 0)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Write Frequency", False, False,  graphname + "_write_frequency" + ".pdf")

xaxis, yaxis = make_x_y_blkno(freqlist_read, 1)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Cumulative Read Frequency", False, False,  graphname + "_read_cdf" + ".pdf")

xaxis, yaxis = make_x_y_blkno(freqlist_read, 0)
draw_linegraph(xaxis, yaxis, "Block Ranges (MB)", "Read Frequency", False, False,  graphname + "_read_frequency" + ".pdf")


# rw cdf
xaxis = []
yaxis = []
xax, yax = make_x_y_blkno(freqlist_write, 1)
xax = np.array(xax)/1024
xaxis.append(xax)
yaxis.append(yax)
xax, yax = make_x_y_blkno(freqlist_read, 1)
xax = np.array(xax)/1024
xaxis.append(xax)
yaxis.append(yax)
label = ["Write", "Read"]
draw_linegraph2(xaxis, yaxis, "Block Range (GB)", "Cumulative Frequency", label, False, False,  graphname + "_cdf" + ".pdf", 4, 3);

xaxis = []
xaxis.append([float(i)/60 for i in range(0, len(write_reqs))])
xaxis.append([float(i)/60 for i in range(0, len(read_reqs))])
yaxis = []
yaxis.append(write_reqs)
yaxis.append(read_reqs)
label = ["Write", "Read"]
draw_linegraph2(xaxis, yaxis, "Time (Hour)", "Request Rate", label, False, False,  graphname + "_req_rate" + ".pdf", 8, 2)

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
