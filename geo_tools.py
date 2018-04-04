#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	geopy

def	get_location (city = None, street = None, house = None, geocoder = None):
	pref_addr = ['РФ']	#, 'Нижний Новгород']
	if city:	pref_addr.append(city)
	else:		pref_addr.append('Нижний Новгород')
	if street:	pref_addr.append(street)
	if house:	pref_addr.append(str(house))
	print ', '.join(pref_addr)
	if len (pref_addr) < 2:		return 10

	if geocoder == 'Yandex':
		from geopy.geocoders import Yandex
		geolocator = Yandex()
	else:
		from geopy.geocoders import Nominatim
		geolocator = Nominatim()
	try:
		location = geolocator.geocode(', '.join(pref_addr))	#, exactly_one = False)
		if location == None:	return None
		if type(location) == list:
			print 'len location list:', len(location)
			for l in location:
				print '\t', l.address
				print '\t', (l.latitude, l.longitude)
		else:
		#	print 'type(location)', type(location)
			print '\t', location.address
			print '\t', (location.latitude, location.longitude)
			if location.raw:
			#	out_dict (location.raw, 'location.raw')
				print '\tname', location.raw['name']

	except geopy.exc.GeocoderServiceError:
		return	11

def	get_03_uhouse (city = None, street = None, house = None, geocoder = None):
	pref_addr = ['РФ']	#, 'Нижний Новгород']
	if city:	pref_addr.append(city)
	else:		pref_addr.append('Нижний Новгород')
	if street:	pref_addr.append(street)
	if house:	pref_addr.append(str(house))
#	print ', '.join(pref_addr)
	if len (pref_addr) < 2:		return 10

	if geocoder == 'Yandex':
		from geopy.geocoders import Yandex
		geolocator = Yandex()
	else:
		from geopy.geocoders import Nominatim
		geolocator = Nominatim()
	try:
		location = geolocator.geocode(', '.join(pref_addr))	#, exactly_one = False)
		if location == None:	return None
		address = location.address
		pos = (location.latitude, location.longitude)
		if location.raw:
			return pos, address, location.raw['name']
		else:	return pos, address

	except geopy.exc.GeocoderServiceError:
		return	11

def	out_dict (d, nm, l = 1):
	print '\t'*l, '%16s:' % nm
	l += 1
	for k in d.keys():
		if type(d[k]) == dict:
			out_dict (d[k], k, l)
		elif type(d[k]) == list:
			print '\t'*l, '%16s:' % k
			for c in d[k]:
				print '\t'*(1+l),
				if type(c) == dict:
					for j in c.keys():
						print '%s:' % j, c[j], 
					print
				#	out_dict (c, '*', l+1)
				else:	print c
		else:	print '\t'*l, '%16s:' % k, d[k]

if __name__ == "__main__":
#	print	get_location(street='Карла Маркса', house=24, geocoder = 'Yandex')
#	print	get_location(street='проспект Ленина', house=33)
#	print	get_location(street='ЛЕНИНА', house='8а', geocoder = 'Yandex')
#	print	get_location(street='ЯСНАЯ', house='4а', geocoder = 'Yandex')
	print	get_location(street='М/П РЕЧНОГО ВОКЗАЛА', geocoder = 'Yandex')
	print	get_location(street='АВТОМЕХАНИЧЕСКАЯ', house='11Б', geocoder = 'Yandex')
	print	get_03_uhouse(street='АВТОМЕХАНИЧЕСКАЯ', house='11Б', geocoder = 'Yandex')
	print '#'*22, '\n'
