#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time
import	geo_tools

def	get_houselist (fname):
	print 'get_houselist', fname
	f = open (fname, 'r')
	streets = {}
	sd = 'Start'
	while sd:
		sd = f.readline()
		ssd = sd.strip()
		if not ssd:	continue
		dd = ssd.split('\t')
	#	print ssd
		street = dd[0][1:-1]
	#	print dd[0][1:-1], dd[1]
		hh = dd[1].split("'")
		house = hh[1][:-1]
	#	print street, house
		if not streets.has_key(street):
			streets[street] = [house]
		else:
		#	print street, streets, house
			if not house in streets[street]:	streets[street].append(house)
	f.close()
	print '#'*44
	isid = 4321
	for k in streets.keys():
		for h in streets[k]:
			print k, h,	#streets[k]
			res = geo_tools.get_03_uhouse (street=k, house=h, geocoder = 'Yandex')
		#	print type(res)
			if type(res) == tuple:
		#		for c in res:	print c,
		#		print
				x = res[0][1]
				y = res[0][0]
				query = "INSERT INTO oo_house (gx, gy, house_num) VALUES (%s, %s, '%s', %d)" % (x, y, h, isid)
				print '\t', query
			else:	print res
			

fname = "03_uhouse.list"
if __name__ == "__main__":
	get_houselist (fname)
