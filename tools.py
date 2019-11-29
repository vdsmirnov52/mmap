#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import  time, getopt

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import  dbtools

DBASES = {
#	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'contracts': 'host=212.193.103.20 dbname=contracts port=5432 user=smirnov',
	'receiver': 'host=212.193.103.20 dbname=receiver port=5432 user=smirnov',
	'worktime': 'host=212.193.103.20 dbname=worktime port=5432 user=smirnov',
	'wialon': 'host=212.193.103.20 dbname=wialon port=5432 user=smirnov',
	}

def	get_org (inn = None):
	if not inn:
		rows = DBR.get_rows('select * FROM org_desc ORDER BY bname')
		for r in rows:
			for c in r:	print c, '\t',
			print
		print '#'*22, 'get_org'
		return DBR.desc, rows
	return	DBR.get_dict('select * FROM org_desc WHERE inn = %s' % inn)	

def	get_transports(orgrow):
	""" Принудитеьно Обновить транспорт организации.
	Поиск транспорта принадлежащего организации get_org (INN) 	"""
	res = DBC.get_table('wtransports', 'id_org = %s' % orgrow['id_org'], cols='id_ts, gosnum, marka, modele, device_id, bm_status')
#	res = DBC.get_table('transports t JOIN transporttype tt ON t.transporttype_id = tt.id', 'id_org = %s' % orgrow['id_org'], cols='id_ts, gosnum, marka, modele, device_id, tt.description AS ttd')
	d = res[0]
	for r in res[1]:
	#	for c in r:	print c, '\t',
	#	print 
		jr = DBR.get_row("select id_ts FROM recv_ts WHERE gosnum = '%s'" % r[d.index('gosnum')])
		if jr:
			if r[d.index('bm_status')] % 1024 == 1024:	# 1024 | Блокирована
				query = "DELETE FROM recv_ts WHERE id_ts = %d;" % jr[0]
				print query, DBR.qexecute(query)
			else: 
				query = "WHERE id_ts = %s" % jr[0]
		#		print query, jr
		else:
			query = "DELETE FROM recv_ts WHERE device_id = %d; INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, rem) VALUES ('idd%s', %s, '%s', '%s', %s, '%s')" % (
				r[d.index('device_id')], r[d.index('device_id')], orgrow['inn'], r[d.index('gosnum')], r[d.index('marka')], r[d.index('device_id')], orgrow['bname'])
			print query	#, DBR.qexecute(query)

def	get_organizations (bm_ssys = None, inn = None):
	""" Поиск организаций принадлежащих подсистеме bm_ssys или по ИНН	"""
	print 'Поиск организаций (bm_ssys = %s, inn = %s)' % (bm_ssys, inn)
	swhere = None
	if bm_ssys:	swhere = 'bm_ssys & %s = %s' % (bm_ssys, bm_ssys)
	if inn:
		if swhere:
			swhere += ' AND inn = %s' % inn
		else:	swhere = 'inn = %s' % inn
	if not swhere:	return

	res = DBC.get_table('organizations', swhere, cols='id_org, inn, bname')
	'''
#	res = DBC.get_table('organizations', 'bm_ssys & %s = %s' % (bm_ssys, bm_ssys), cols='id_org, inn, bname')
	for k in res[0]:	print '\t', k, '=\t', res[1][0][res[0].index(k)],
	return
	'''
	if not res:	return
	d = res[0]
	count_ts = 0
	for r in res[1]:
		jr = DBC.get_row("select count(*) FROM wtransports WHERE (bm_status & 7168) = 0 AND id_org = %s" % r[d.index('id_org')])
#		for c in r:	print c, '\t',
#		print jr, jor
		if jr[0] > 0:
			stat = 1
			count_ts += jr[0]
		else:	stat = 0
		jor = DBR.get_row("select * FROM org_desc WHERE id_org = %s" % r[d.index('id_org')])
		if jor:
			if jr[0] > 0:
				query = "UPDATE org_desc SET count_ts = %d, stat = 1 WHERE id_org = %s" % (jr[0], r[d.index('id_org')])
			else:
				query = "UPDATE org_desc SET count_ts = 0, stat = 0 WHERE id_org = %s" % r[d.index('id_org')]
		else:
			query = "INSERT INTO org_desc (id_org, inn, bname, bm_ssys, rem, stat, count_ts) VALUES (%s, %s, '%s', %s, '%s', %s, %d)" % (
				r[d.index('id_org')], r[d.index('inn')], r[d.index('bname')], bm_ssys, r[d.index('bname')], stat, jr[0])
		rex = DBR.qexecute(query)
		print query, rex
		if stat == 1:	get_transports (get_org (r[d.index('inn')]))
		
	print '#'*22, 'get_organizations \tcount_ts:', count_ts

def	tests():
	print '\tКонтроль соединений с БД'
	for key in DBASES:
		print '\t', key, "=\t", DBASES[key], '\t>',
		ddb = dbtools.dbtools (DBASES[key], 0)
		if not ddb.last_error:	print 'OK'
	sys.exit()

def	outhelp():
	print """\n Утилита для работы с БД
	-t	Контроль соединений с БД
	-d	Отладка (DEBUG = True)
	-s MSS	Поиск по bm_ssys. Ищем организации принадлежащин подсистеме и их транспортные средства.
	-o INN	Поиск по ИНН. Ищем организацию и ее транспортные средства.
	-h	Справка
	"""
	sys.exit()

DBC =	None
DBR =	None
DEBUG =	False
if __name__ == "__main__":
	org_inn = None
	bm_ssys = None
	comands = None
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'htdo:s:c:')
		for o in optlist:
			if o[0] == '-h':	outhelp()
			if o[0] == '-t':	tests()
			if o[0] == '-d':	DEBUG = True
			if o[0] == '-s':	bm_ssys = o[1]
			if o[0] == '-o':	org_inn = o[1]
			if o[0] == '-c':	comands = o[1]
		if not (org_inn or comands):
			DEBUG = True
		if comands:	print 'comands:', comands

		DBC = dbtools.dbtools(DBASES['contracts'])
		DBR = dbtools.dbtools(DBASES['receiver'])

	#	get_transports (get_org (5262021430))
	#	get_transports (get_org (5257072581))
	#	get_organizations (131072)
		get_organizations (bm_ssys, org_inn)
		get_org ()
	except SystemExit:	pass
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "\tEXCEPT:", exc_type, exc_value
