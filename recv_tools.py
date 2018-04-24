#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import  time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import  dbtools


def	get_ts (request):
	""" Читать транспорт по ИНН	"""
# CREATE  VIEW vlast_pos AS SELECT p.*, t.idd AS code, t.inn AS tinn, gosnum, marka, t.rem, bname FROM last_pos p INNER JOIN recv_ts t ON p.ida = t.device_id INNER JOIN org_desc o ON t.inn = o.inn;
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
#	res = dbi.get_table('last_pos', 'inn >0 ORDER BY t DESC')
#	res = dbi.get_table('vlast_pos', 'x >0 ORDER BY t DESC')

	org_inn = request.get('org_inn')
	bm_ssys = request.get('bm_ssys')
	
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		res = dbi.get_table('vlast_pos', 'tinn = %s ORDER BY t DESC' % org_inn)
	elif bm_ssys and bm_ssys.isdigit():
		res = dbi.get_table('vlast_pos', 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s = %s) ORDER BY t DESC' % (bm_ssys, bm_ssys))
	else:	res = dbi.get_table('vlast_pos', 'tinn >0 ORDER BY t DESC')
	if not res:	return	# data
	d = res[0]
	print 'org_inn', org_inn, len(res[1]), 'org_inn:', org_inn, 'bm_ssys:', bm_ssys
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
		if res:	# os.path.split(os.environ['HTTP_REFERER'])[-1] == 'temp.html':
		#	opts = {'icon': icon, 'gosnum': "<b> %s </b>" % r[d.index('gosnum')], 'dt': '%s' % time.strftime('%T %d-%m-%Y', time.localtime(r[d.index('t')]))}
			opts = {'icon': icon, 'gosnum': "<b> %s </b>" % r[d.index('gosnum')], 'dt': '%s' % str_time (r[d.index('t')], jtm).replace("'", '')}
			if r[d.index('bname')] and r[d.index('bname')] != '':
				opts['bn'] = "<span class=bfligt>%s </span><br />" % r[d.index('bname')].replace('"', " ")
			if r[d.index('sp')] and r[d.index('sp')] > 0:
				opts['sp'] = ' &nbsp; v:%dкм/ч' % r[d.index('sp')]
			else:	opts['sp'] = ' &nbsp; <span class=bferr>Стоит</span>'
			ddd.append([[float(r[d.index('y')]), float(r[d.index('x')])], opts])
		else:
			if r[d.index('bname')] and r[d.index('bname')] != '':
				gosnum += '<br><b>%s</b>' % r[d.index('bname')].replace('"', " ")
			if r[d.index('marka')]:	gosnum += '<br>' +r[d.index('marka')]
		#	ddd.append([float(r[d.index('x')]), float(r[d.index('y')]), '%s' % time.strftime('%T %d-%m-%Y', time.localtime(r[d.index('t')])), gosnum, icon])
			ddd.append([float(r[d.index('x')]), float(r[d.index('y')]), '%s' % str_time (r[d.index('t')], jtm).replace("'", ''), gosnum, icon])
	return	ddd

img_close = """<img onclick="$('#widget').html('')" src="../img/delt2.png" >"""	#<img src="../img/delt2.png" ><img src="../img/delt2.png" >"""
def	view_gzones (request):
	peg_nn = { 1: 'Автозаводский', 2: 'Канавинский', 3: 'Ленинский', 4: 'Московский', 5: 'Нижегородский', 6: 'Приокский', 7: 'Советский', 8: 'Сормовский', 9: 'Северний', }

	cod_region = request.get('cod_region')
	sout = ["""<div class="wffront" style="width: 510px; ">"""]
	sout.append ('<table width="100%%" cellpadding="2" cellspacing="0">')
	if cod_region and cod_region.isdigit() and int(cod_region) > 0:
		sout.append("""<tr class='line'><td onclick="document.myForm.cod_region.value=''; $('#widget').html(''); mymap.setView([56.32, 43.95], 11); set_shadow ('set_region');"><span class='tit'>
			Вернутся в Центр города </span></td><td align="right">%s</td></tr></table>""" % img_close)
	else:
		sout.append ("""<tr class='mark'><td><span class='tit' onclick="$('#widget').html('');">Выбрать район города:</span></td><td align="right">%s</td></tr></table>""" % img_close)
	
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	res = dbi.get_table ('mp_region', 'cpoint IS NOT NULL ORDER BY cod')
	if res:	# os.path.split(os.environ['HTTP_REFERER'])[-1] == 'temp.html':
		d = res[0]
		sout.append("""<br /><table width="99%" cellpadding="2" cellspacing="0">""")
		for r in res[1]:
			if cod_region and cod_region.isdigit() and int(cod_region) == r[d.index('cod')]:
				sout.append("""<tr class='mark'><td>&nbsp;&nbsp;&bull; %s</td><td align=right> &nbsp;&nbsp;</td></tr>""" % r[d.index('name')])	#, r[d.index('cpoint')]))
			else:
				lll = r[d.index('cpoint')][1:-1].split(',')
				sout.append("""<tr class='line' onclick="document.myForm.cod_region.value=%d; $('#widget').html('');
					mymap.setView([%s,%s], 12);
					set_shadow ('set_region');"><td>&nbsp;&nbsp;&bull; %s</td><td align=right> &nbsp;&nbsp;</td></tr>""" % (
					r[d.index('cod')], lll[1], lll[0], r[d.index('name')]))	#, r[d.index('cpoint')]))
		sout.append ('</table><br />')
		
	elif res == False:
		sout.append ('<ul>')
		for jr in peg_nn.keys():
			sout.append ("""<li class='line' > %s</li>""" % peg_nn[jr])
		sout.append ('</ul>')
	else:
		sout.append ('<span class="bferr"> нет Зоны обслуживания </span>')
	sout.append('</div>')
	return '\n'.join(sout)

def	str_time (tm, cerrtm = None):
	if not cerrtm:	cerrtm = int(time.time())
	dtm = cerrtm - tm
	if dtm < 60:	return	"<span class='finf sz12'> &nbsp; <b>%s</b> сек назад</span>" % dtm
	if dtm < 3600:	return	"<span class='fgrey sz12'> &nbsp; <b>%s</b> мин назад</span>" % int(dtm/60)
	if dtm < 36000:	return	time.strftime("<span class='fligt sz12'> &nbsp; в %T </span>", time.localtime (tm))
	return	time.strftime("<span class='ferr sz12'> &nbsp; от %T %d.%m.%Y</span>", time.localtime (tm))
	
def	str_speed (sp):
	if sp:	return	" &nbsp; <span class='fligt sz12'> v:<b>%s</b>км/ч" % sp
	return 	" &nbsp; <span class='bferr sz12'>Стоит</span>"

def	view_ts_list (request):
	print '~log|view_ts_list <br>'
	sout = ["""<div class="wffront" style="width: 510px; ">""",
		"""<table width="100%%" cellpadding="2" cellspacing="0"><tr class='mark'><td><span class='tit'> Список транспорта </span></td><td align="right">%s</td></tr></table>""" % img_close]
	sinn = request.get('org_inn')
	if sinn and sinn.isdigit():
		intm = int(time.time())
		dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	#	SELECT a.*, x, y, t, sp FROM recv_ts a LEFT JOIN vlast_pos AS p ON a.device_id = p.ida WHERE a.inn=
	#	res = dbi.get_table ('recv_ts a LEFT JOIN vlast_pos AS p ON a.device_id = p.ida', 'a.inn = %s ORDER BY gosnum' % sinn, cols='a.id_ts, a.gosnum, x, y, t')
		res = dbi.get_table ('recv_ts a JOIN vlast_pos AS p ON a.device_id = p.ida', 'a.inn = %s ORDER BY gosnum' % sinn, cols='a.id_ts, a.gosnum, x, y, t, sp')
		if res:
			d = res[0]
			sout.append(str(d))
			sout.append('<table>')
			for r in res[1]:
				jtm = r[d.index('t')]
				if jtm:
					stm = str_time(jtm, intm)
					gosnum = "<span class='bfinf'> %s </span>" % r[d.index('gosnum')]
					trclass = """class='line' onclick="$('#widget').html(''); mymap.setView([%s,%s]); set_shadow('get_tansport');" """ % (r[d.index('y')], r[d.index('x')])
				else:
					stm = ''
					gosnum = "<span class='bferr'> %s </span>" % r[d.index('gosnum')]
					trclass = ""
				tr = """<tr %s><td> %s </td><td> %s </td><td> %s </td></tr>""" % (
						trclass, gosnum, str_speed(r[d.index('sp')]), stm)
				sout.append(tr)
			sout.append('</table>')
	else:	sout.append (str(request))
	sout.append('</div>')
	return '\n'.join(sout)

def	set_place(inn):
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	dorg = dbi.get_dict ('SELECT * FROM org_desc WHERE inn = %s' % inn)
	if dorg['place']:
		print ""
		if dorg['zoom']:
			zoom = dorg['zoom']
		else:	zoom = 11
		x,y = str(dorg['place'])[1:-1].split(',')
		print "~eval|mymap.setView([%s,%s], %s);" % (y, x, zoom)
		print "~eval|L.marker([%s,%s]).bindPopup('%s').addTo(mymap).openPopup()" % (y, x, dorg['bname'])
		if dorg['bm_ssys'] == 2:	# Пассажирские перевозки
			print """~eval|$('#head_AA').html('<div class=asbutton> %s </div>')""" % dorg['bname']
			print """~eval|$('#head_BB').html('<div class=asbutton onclick="list_ts();"> Список трансрорта </div>')"""

def	set_region(request):
	print 'set_region', request
	cod_region = request.get('cod_region')
	if cod_region and cod_region.isdigit() and int(cod_region) > 0:
		dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
		row = dbi.get_row ('SELECT plgn FROM mp_region WHERE cod = %s' % cod_region)
		print "~log|", type(row[0])
		plist = []
		for p in row[0][1:-1].replace('),(', '):(').split(':'):
			xy = p[1:-1].split(',')
			plist.append(xy[1] +','+ xy[0])
		print "~eval|if (! list_regionn.hasOwnProperty(%s)) { list_regionn[%s] = L.polygon([[%s]], {color: 'red'}).addTo(mymap); }" % (cod_region, cod_region, '],['.join(plist))	#, cod_region)
	else:
		print "~eval| clear_map_object (list_regionn);"

def	get_olist (bm_ssys = None):
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	olist = {}
	if not bm_ssys:	bm_ssys = 131072
#	res = dbi.get_table ('org_desc', 'inn > 0 ORDER BY bname')
#	res = dbi.get_table ('org_desc', 'inn > 0 AND stat & 1 = 1 ORDER BY bname')
	res = dbi.get_table ('org_desc', 'inn > 0 AND stat & 1 = 1 AND bm_ssys & %s = %s ORDER BY bname' % (bm_ssys, bm_ssys))
	if res:
		d = res[0]
		for r in res[1]:	olist[r[d.index('inn')]] = (r[d.index('bname')], r[d.index('count_ts')])
	return	olist

def	set_organizations (request):
	sout = ["""<div class="wffront" style="width: 550px; ">"""]
	
	bm_ssys = request.get('bm_ssys')
	orgs_list = get_olist (bm_ssys)
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

	referer = os.environ.get('HTTP_REFERER')
	if referer:	print referer, os.path.split(referer), '<hr>'
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	res = dbi.get_table ('org_desc')
	if not res:
		print 'update_ts_list', request
		return
	d = res[0]
	for r in res[1]:
	#	for k in d:	print r[d.index(k)],
	#	print '<br>'
		tsbyorg = get_tsbyorg (r[d.index('id_org')], r[d.index('inn')])
		if not tsbyorg:	continue
		for gn in tsbyorg.keys():
			if dbi.get_row ("SELECT * FROM recv_ts WHERE gosnum = '%s'" % gn):
				query = "UPDATE recv_ts SET device_id = %d, inn = %d, rem = '%s', marka = '%s' WHERE gosnum = '%s'" % (tsbyorg[gn][0], r[d.index('inn')], r[d.index('bname')], tsbyorg[gn][1], gn)
			else:
				query = "INSERT INTO recv_ts (idd, device_id, inn, rem, gosnum) VALUES ('idd%d', %d, %d, '%s', '%s')" % (tsbyorg[gn][0], tsbyorg[gn][0], r[d.index('inn')], r[d.index('bname')], gn)
			'''
				print query, '<br>'
			'''
			if not dbi.qexecute(query):
				print query, '<br>'
				return

if __name__ == "__main__":
	request = {'this': 'ajax', 'org_inn': '0', 'shstat': 'update_ts_list', 'leaflet-base-layers': 'on'} 
	print update_ts_list (request)
	print get_olist()
