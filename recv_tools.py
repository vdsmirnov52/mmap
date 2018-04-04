#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import  time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import  dbtools


def	get_ts (request):
	data = [	# DEBUG
		[ 44.054517, 56.366000, '11.03.2018 16:22:22', 'В088КР152' ],
		[ 44.068579, 56.372314, 1520846572, 'В132ХА152' ], [ 44.095624, 56.369604, 1520846556, 'К155РР152' ], [ 44.101358, 56.341312, 1520846576, 'К241НХ152' ],
		[ 44.054419, 56.359042, 1520846152, 'К243НХ152' ], [ 44.885438, 55.566636, 1519914891, 'К259НХ152' ], [ 44.095282, 56.369533, 1520846564, 'К260НХ152' ],
		[ 44.114529, 56.341735, 1520846502, 'К289ОХ152' ], [ 44.081979, 56.352356, 1520846557, 'К290ОХ152' ], [ 44.095706, 56.369468, 1518531986, 'К297НХ152' ],
		[ 44.095849, 56.369503, 1520843830, 'К765КА152' ], [ 44.081248, 56.352368, 1520846469, 'К827СС152' ], [ 44.056917, 56.547167, 1520846580, 'К831СС152' ],
	]
# CREATE  VIEW vlast_pos AS SELECT p.*, t.idd AS code, t.inn AS tinn, gosnum, marka, t.rem, bname FROM last_pos p INNER JOIN recv_ts t ON p.ida = t.device_id INNER JOIN org_desc o ON t.inn = o.inn;
#	dbi = dbtools.dbtools('host=212.193.103.20 dbname=wialon port=5432 user=smirnov')
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
#	res = dbi.get_table('last_pos', 'inn >0 ORDER BY t DESC')
#	res = dbi.get_table('vlast_pos', 'x >0 ORDER BY t DESC')

	org_inn = request.get('org_inn')
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		res = dbi.get_table('vlast_pos', 'tinn = %s ORDER BY t DESC' % org_inn)
	else:	res = dbi.get_table('vlast_pos', 'tinn >0 ORDER BY t DESC')
	if not res:	return	# data
	d = res[0]
	ddd = []
	gosnum = '??? '
	jtm = int(time.time())
	for r in res[1]:
		tr = r[d.index('t')]
		if jtm - tr > 3600*24:
			icon = 'grey'
		elif jtm - tr > 3600:
			icon = 'blue'
		else:	icon = 'green'
		if r[d.index('gosnum')]:
			gosnum = '<b>%s</b>' % r[d.index('gosnum')]
		else:	gosnum = '<b>%s</b>' % r[d.index('nm')]
		if r[d.index('sp')] and r[d.index('sp')] > 0:
			gosnum += ' &nbsp; v:%dкм/ч' % r[d.index('sp')]
		else:	gosnum += ' <span class=bferr>Стоит</span>'
		if os.path.split(os.environ['HTTP_REFERER'])[-1] == 'temp.html':
			opts = {'icon': icon, 'gosnum': r[d.index('gosnum')], 'dt': '%s' % time.strftime('%T %d-%m-%Y', time.localtime(r[d.index('t')]))}
			if r[d.index('bname')] and r[d.index('bname')] != '':
				opts['sp'] = "%s" % r[d.index('bname')].replace('"', " ")
			ddd.append([[float(r[d.index('y')]), float(r[d.index('x')])], opts])	#icon': icon, 'gosnum': r[d.index('gosnum')], 'dt': '%s' % time.strftime('%T %d-%m-%Y', time.localtime(r[d.index('t')]))}])
		else:
			if r[d.index('bname')] and r[d.index('bname')] != '':
				gosnum += '<br><b>%s</b>' % r[d.index('bname')].replace('"', " ")
			if r[d.index('marka')]:	gosnum += '<br>' +r[d.index('marka')]
			ddd.append([float(r[d.index('x')]), float(r[d.index('y')]), '%s' % time.strftime('%T %d-%m-%Y', time.localtime(r[d.index('t')])), gosnum, icon])
	return	ddd

img_close = """<img onclick="$('#widget').html('')" src="../img/delt2.png" >"""	#<img src="../img/delt2.png" ><img src="../img/delt2.png" >"""
def	view_gzones (request):
	peg_nn = { 1: 'Автозаводский', 2: 'Канавинский', 3: 'Ленинский', 4: 'Московский', 5: 'Нижегородский', 6: 'Приокский', 7: 'Советский', 8: 'Сормовский', 9: 'Северний', }

	sout = ["""<div class="wffront" style="width: 510px; ">"""]
	sout.append ("""<table width="100%%" cellpadding="2" cellspacing="0">
		<tr class='mark'><td><span class='tit' onclick="$('#widget').html('');">Выбрать район города:</span></td><td align="right">%s</td></tr></table>""" % img_close)
	sout.append ('<ul>')
	for jr in peg_nn.keys():
		sout.append ("""<li class='line' > %s</li>""" % peg_nn[jr])
	sout.append ('</ul>')
	sout.append('</div>')
	return '\n'.join(sout)

orgs_list = {	### DEBUG
	5263004131: '"Дорожник" г. Нижний Новгород',
	5259120142: 'ООО «НижДорСервис»',
	5263133747: 'ООО "ЭксАвтоДор"',
	5256021545: 'МП РЭД Автозаводского района',
	1234567890: 'ООО Навигационные технологии',
	}
def	get_olist (bm_ssys = None):
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	olist = {}
#	res = dbi.get_table ('org_desc', 'inn > 0 ORDER BY bname')
	res = dbi.get_table ('org_desc', 'inn > 0 AND stat & 1 = 1 ORDER BY bname')
	if res:
		d = res[0]
		for r in res[1]:	olist[r[d.index('inn')]] = (r[d.index('bname')], r[d.index('count_ts')])
	return	olist

def	set_organizations (request):
	sout = ["""<div class="wffront" style="width: 510px; ">"""]
	
	orgs_list = get_olist ()
	org_inn = request.get('org_inn')
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		int_inn = int(org_inn)
		sout.append ("""<table width="100%%" cellpadding="2" cellspacing="0">
			<tr><td><span class='line tit' onclick="document.myForm.org_inn.value=0; $('#widget').html(''); set_shadow ('get_tansport');">Выбрать ВСЕ организации</span></td><td align="right">%s</td></tr></table>""" % img_close)
	else:
		int_inn = 0
		sout.append ("""<table width="100%%" cellpadding="2" cellspacing="0"><tr class='mark'><td class='tit'>Выбрать организацию:</td><td align="right">%s</td></tr></table>""" % img_close)
	
	sout.append("""<table width="99%" cellpadding="2" cellspacing="0"><tr><td></td><td  align=right><b>Машин</b></td></tr>""")
	for inn in orgs_list.keys():
		if int_inn and int_inn == inn:
			sout.append("""<tr class='mark'><td>&nbsp;&nbsp;&bull; %s</td><td align=right>%s &nbsp;&nbsp;</td></tr>""" % (orgs_list[inn][0], orgs_list[inn][1]))
		else:	
			sout.append("""<tr class='line' onclick="document.myForm.org_inn.value=%d; $('#widget').html(''); set_shadow ('get_tansport');"><td>&nbsp;&nbsp;&bull; %s</td><td align=right>%s &nbsp;&nbsp;</td></tr>""" % (
				inn, orgs_list[inn][0], orgs_list[inn][1]))
	sout.append("</table><br>")
	sout.append('</div>')
	return	'\n'.join(sout)

#	if os.path.split(os.environ['HTTP_REFERER'])[-1] == 'temp.html':
	'''
#	sout.append (str (request))
	sout.append ('<ul>')
	for inn in orgs_list.keys():
		if int_inn and int_inn == inn:
			sout.append ("""<li class='mark' > %s</li>""" % orgs_list[inn][0]) 
		else:	sout.append ("""<li class='line' onclick="document.myForm.org_inn.value=%d; $('#widget').html(''); set_shadow ('get_tansport');" >%s</li>""" % (inn, orgs_list[inn][0]))
	sout.append ('</ul>')
	sout.append('</div>')
	return '\n'.join(sout)
	'''

def	get_tsbyorg (id_org, inn):
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=contracts port=5432 user=smirnov')

	res = dbi.get_table ('transports', 'id_org = %d AND device_id > 0' % id_org)
	if not res:	return
	d = res[0]
#	print d
	out = {}
	for r in res[1]:
		out[r[d.index('gosnum')]] = (r[d.index('device_id')], r[d.index('marka')])
	#	print r[d.index('gosnum')], r[d.index('device_id')], '<br>'
	return	out
	
def	update_ts_list (request):

	referer = os.environ['HTTP_REFERER']
	print referer, os.path.split(referer), '<hr>'
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	res = dbi.get_table ('org_desc')
	if not res:
		print 'update_ts_list', request
		return
	d = res[0]
	for r in res[1]:
		for k in d:
			print r[d.index(k)],
		print '<br>'
		tsbyorg = get_tsbyorg (r[d.index('id_org')], r[d.index('inn')])
		if not tsbyorg:	continue
		for gn in tsbyorg.keys():
			if dbi.get_row ("SELECT * FROM recv_ts WHERE gosnum = '%s'" % gn):
				query = "UPDATE recv_ts SET device_id = %d, inn = %d, rem = '%s', marka = '%s' WHERE gosnum = '%s'" % (tsbyorg[gn][0], r[d.index('inn')], r[d.index('bname')], tsbyorg[gn][1], gn)
			else:	query = "INSERT INTO recv_ts (idd, device_id, inn, rem, gosnum) VALUES ('idd%d', %d, %d, '%s', '%s')" % (tsbyorg[gn], tsbyorg[gn], r[d.index('inn')], r[d.index('bname')], gn)
			if not dbi.qexecute(query):
				print query, '<br>'
				return

if __name__ == "__main__":
	request = {'this': 'ajax', 'org_inn': '0', 'shstat': 'update_ts_list', 'leaflet-base-layers': 'on'} 
#	print update_ts_list (request)
	print get_olist()
