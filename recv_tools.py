#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import  time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import  dbtools

ACTIV_ROUTES = []
def	get_route (idd):
	global	ACTIV_ROUTES
	
	if type(idd) == str:
		if not idd.isdigit():	return "ZZZ %s" % idd
		idd = int(idd)

	if ACTIV_ROUTES:
		for r in ACTIV_ROUTES:
			for u in r['u']:
				if u == idd:
					return	r['m']
		return "Неизвестен"	# % idd
	import	nimbus
	try:
		token = 'Token 30e04452062e435a9b48740f19d56f45'
		cmnd = 'depot/128/routes'
		res = nimbus.u8api_nimbus (cmnd, token)
		routes = res.get ('routes')
		for r in routes:
			if not (r.has_key('u') and r['u']):	continue
		#	d = {'m': "%s %s %s" % (r['id'], r['n'], r['d']), 'u': r['u']}
		#	ACTIV_ROUTES.append ({'m': "%s %s %s" % (r['id'], r['n'], r['d']), 'u': r['u']})
		#	ACTIV_ROUTES.append ({'m': "%s %s" % (r['n'], r['d']), 'u': r['u']})
			ACTIV_ROUTES.append ({'m': "%s" % r['n'], 'u': r['u'], 'st': r['st']})
	#	print len(routes)
		return	get_route (idd)
	except:	return "except"
	

def	get_ts (request):
	""" Читать транспорт по ИНН	"""
	HTTP_REFERER = os.environ.get('HTTP_REFERER')
	if 'atp.html' in HTTP_REFERER:
		check_route = True
	#	print HTTP_REFERER
	else:	check_route = False
#	print	get_route (679)

	# CREATE  VIEW vlast_pos AS SELECT p.*, t.idd AS code, t.inn AS tinn, gosnum, marka, t.rem, bname FROM last_pos p INNER JOIN recv_ts t ON p.ida = t.device_id INNER JOIN org_desc o ON t.inn = o.inn;
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')

	org_inn = request.get('org_inn')
	bm_ssys = request.get('bm_ssys')
	
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		res = dbi.get_table('vlast_pos', 'tinn = %s ORDER BY t DESC' % org_inn)
	elif bm_ssys and bm_ssys.isdigit():
		res = dbi.get_table('vlast_pos', 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s = %s) ORDER BY t DESC' % (bm_ssys, bm_ssys))
	else:	res = dbi.get_table('vlast_pos', 'tinn >0 ORDER BY t DESC')
	if not res:	return	# data
	d = res[0]
#	print 'org_inn', org_inn, len(res[1]), 'bm_ssys:', bm_ssys
	ddd = []
	gosnum = '??? '
	jtm = int(time.time())
	for r in res[1]:
		tr = r[d.index('t')]
		if jtm - tr > 3600*24:
			icon = 'grey'
			continue	### DEBUG
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
				if check_route:
					opts['bn'] = "№<span class=tit>&nbsp;%s </span>" % get_route(r[d.index('code')])	#HTTP_REFERER
				else:	opts['bn'] = "<span class=bfligt>%s </span><br />" % r[d.index('bname')].replace('"', " ")
			if r[d.index('sp')] and r[d.index('sp')] > 0:
				opts['sp'] = ' &nbsp; v:%dкм/ч' % r[d.index('sp')]
			else:	opts['sp'] = ' &nbsp; <span class=bferr>Стоит</span>'
			ddd.append([[float(r[d.index('y')]), float(r[d.index('x')])], opts])
		else:
			if check_route:
				get_route(r[d.index('idd')])
			if r[d.index('bname')] and r[d.index('bname')] != '':
				gosnum += '<br><b>%s</b>' % r[d.index('bname')].replace('"', " ")
			if r[d.index('marka')]:	gosnum += '<br>' +r[d.index('marka')]
		#	ddd.append([float(r[d.index('x')]), float(r[d.index('y')]), '%s' % time.strftime('%T %d-%m-%Y', time.localtime(r[d.index('t')])), gosnum, icon])
			ddd.append([float(r[d.index('x')]), float(r[d.index('y')]), '%s' % str_time (r[d.index('t')], jtm).replace("'", ''), gosnum, icon])
	return	ddd

#img_close = """<img onclick="$('#widget').html('')" src="../img/delt2.png" >"""	#<img src="../img/delt2.png" ><img src="../img/delt2.png" >"""
#img_close = """<i class="fa fa-refresh" aria-hidden="true" onclick="$('#widget').html('')"></i>"""
#img_close = """<i class="fa fa-window-close" aria-hidden="true" onclick="$('#widget').html('')"></i>&nbsp;"""
img_close = """<i class="fa fa-times fa-lg" aria-hidden="true" onclick="$('#widget').html('')"></i>&nbsp;"""

def	view_gzones (request):
	peg_nn = { 1: 'Автозаводский', 2: 'Канавинский', 3: 'Ленинский', 4: 'Московский', 5: 'Нижегородский', 6: 'Приокский', 7: 'Советский', 8: 'Сормовский', 9: 'Северний', }

	cod_region = request.get('cod_region')
	sout = ["""<div class="wffront" style="width: 510px; max-width: 90% ">"""]
	sout.append ('')
	if cod_region and cod_region.isdigit() and int(cod_region) > 0:
		sout.append("""<div class='list-group-item list-group-item-action'><span onclick="document.myForm.cod_region.value=''; $('#widget').html(''); mymap.setView([56.32, 43.95], 11); set_shadow ('set_region');">
					<span class="tit">Вернутся в Центр города </span>
					</span>
					<span class="float-right">%s</span>
					</div>""" % img_close)
	else:
		sout.append ("""<div class='list-group-item list-group-item-action active'><span class='tit' onclick="$('#widget').html('');">&nbsp;Выбрать район города:</span><span class="float-right">%s</span></div>""" % img_close)
	
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	res = dbi.get_table ('mp_region', 'cpoint IS NOT NULL ORDER BY cod')
	if res:	# os.path.split(os.environ['HTTP_REFERER'])[-1] == 'temp.html':
		d = res[0]
		sout.append("""<ul class="list-group">""")
		for r in res[1]:
			if cod_region and cod_region.isdigit() and int(cod_region) == r[d.index('cod')]:
				sout.append("""<li class='list-group-item list-group-item-action active'>%s</li>""" % r[d.index('name')])	#, r[d.index('cpoint')]))
			else:
				lll = r[d.index('cpoint')][1:-1].split(',')
				sout.append("""<li class='line list-group-item list-group-item-action' onclick="document.myForm.cod_region.value=%d; $('#widget').html('');
					mymap.setView([%s,%s], 12);
					set_shadow ('set_region');"><span>%s</span></li>""" % (
					r[d.index('cod')], lll[1], lll[0], r[d.index('name')]))	#, r[d.index('cpoint')]))
		sout.append ('</div>')
		
	elif res == False:
		sout.append ('<ul>')
		for jr in peg_nn.keys():
			sout.append ("""<li class='line' > %s</li>""" % peg_nn[jr])
		sout.append ('</ul>')
	else:
		sout.append ('<span class="bferr"> нет Зоны обслуживания </span>')
	sout.append('</div>')
	return '\n'.join(sout)

def	str_time (tm, currtm = None):
	if not tm:	return	"<span class='bferr sz12'>Нет данных!</span>"
	if not currtm:	currtm = int(time.time())
	dtm = currtm - tm
	if dtm < 60:	return	"<span class='finf sz12'> &nbsp; <b>%s</b> сек назад</span>" % dtm
	if dtm < 3600:	return	"<span class='fgrey sz12'> &nbsp; <b>%s</b> мин назад</span>" % int(dtm/60)
	if dtm < 36000:	return	time.strftime("<span class='fligt sz12'> &nbsp; в %T </span>", time.localtime (tm))
	return	time.strftime("<span class='ferr sz12'> &nbsp; от %T %d.%m.%Y</span>", time.localtime (tm))
	
def	str_speed (sp):
	if sp:	return	" &nbsp; <span class='fligt sz12'> v:<b>%s</b>км/ч" % sp
	return 	" &nbsp; <span class='bferr sz12'>Стоит</span>"

def	view_ts_list (request):
	""" Показать Список транспорта организации	"""
	print '~log|view_ts_list <br>'
	sout = ["""<div class="wffront" style="width: 510px; max-width: 90%">""",
		"""<div class='list-group-item list-group-item-action active'><span class='tit'> Список транспорта </span><span class="float-right">%s</span></div>""" % img_close,
	#	"""<table width="100%%" cellpadding="2" cellspacing="0"><tr class='bgmark'><td><span class='tit'> Список транспорта </span></td><td align="right">%s</td></tr></table>""" % img_close,
		]
	sinn = request.get('org_inn')
	if sinn and sinn.isdigit():
		intm = int(time.time())
		dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	#	SELECT a.*, x, y, t, sp FROM recv_ts a LEFT JOIN vlast_pos AS p ON a.device_id = p.ida WHERE a.inn=
	#	res = dbi.get_table ('recv_ts a LEFT JOIN vlast_pos AS p ON a.device_id = p.ida', 'a.inn = %s ORDER BY gosnum' % sinn, cols='a.id_ts, a.gosnum, x, y, t')
		res = dbi.get_table ('recv_ts a JOIN vlast_pos AS p ON a.device_id = p.ida', 'a.inn = %s ORDER BY gosnum' % sinn, cols='a.id_ts, a.gosnum, x, y, t, sp')
		if res:
			d = res[0]
		#	sout.append(str(d))
		#	sout.append('<table>')
			for r in res[1]:
				jtm = r[d.index('t')]
				if len(r[d.index('gosnum')]) < 14:	gosnum = r[d.index('gosnum')] + '&nbsp;' * (14 - len(r[d.index('gosnum')]))
				if jtm:
					stm = str_time(jtm, intm)
					gosnum = "<span class='bfinf'> %s </span>" % gosnum	#r[d.index('gosnum')]
				#	trclass = """class='line' onclick="$('#widget').html(''); mymap.setView([%s,%s]); set_shadow('get_transport');" """ % (r[d.index('y')], r[d.index('x')])
					onclick = """ onclick="$('#widget').html(''); mymap.setView([%s,%s]); set_shadow('get_transport');" """ % (r[d.index('y')], r[d.index('x')])
				else:
					stm = ''
					gosnum = "<span class='bferr'> %s </span>" % gosnum	#r[d.index('gosnum')]
					onclick = ""
				'''
					trclass = ""
				tr = """<tr %s><td> %s </td><td> %s </td><td> %s </td></tr>""" % (
						trclass, gosnum, str_speed(r[d.index('sp')]), stm)
				sout.append(tr)
			sout.append('</table>')
				'''
				if r[d.index('sp')] == 0:
					speed = "<span style='font-weight: bold; color: #fd4;'>Стоит</span>"
				else:	speed = '%s км' % r[d.index('sp')]
				sout.append("""<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center' %s >
					<span> %s %s </span> <span class="badge badge-primary badge-pill">%s</span></li>""" % (
					onclick, gosnum, stm, speed))
				
	else:	sout.append (str(request))
	sout.append('</div>')
	return '\n'.join(sout)

def	view_ts_config (request):
	""" Параметры ТС организации	"""
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	dorg = dbi.get_dict ('SELECT * FROM org_desc WHERE inn = %s' % request['org_inn'])
	sout = ["""<div class="wffront" style="width: 510px; max-width: 90%">""",
		"""<div class='list-group-item list-group-item-action active'><span class='tit'>ZZZ %s </span><span class="float-right">%s</span></div>""" % (dorg['bname'], img_close) ,
		str(request)
		]
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
		#	print """~eval|$('#head_AA').html('<div class=asbutton><i class="fa fa-list" aria-hidden="true"></i><span class="button-text"> %s </span></div>')""" % dorg['bname']
			print """~eval|$('#head_AA').html('<div class=asbutton onclick="config_ts();"><i class="fa fa-list" aria-hidden="true"></i><span class="button-text"> %s </span></div>')""" % dorg['bname']
			print """~eval|$('#head_BB').html('<div class=asbutton onclick="list_ts();"><i class="fa fa-bus" aria-hidden="true"></i><span class="button-text"> Список трансрорта </span></div>')"""

#	UPDATE polygons SET region = (SELECT region FROM plabel WHERE polygons.id_lab = plabel.id_lab) WHERE polygons.region IS NULL;
#	UPDATE polygons SET categ = (SELECT categ FROM plabel WHERE polygons.id_lab = plabel.id_lab) WHERE polygons.categ IS NULL;

def	set_region(request):
	""" Выбор района города	"""
#	print 'set_region', request
	cod_region = request.get('cod_region')
	if cod_region and cod_region.isdigit() and int(cod_region) > 0:
		dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
		row = dbi.get_row ('SELECT plgn FROM mp_region WHERE cod = %s' % cod_region)
		print "~log|", type(row[0])
		plist = []
		for p in row[0][1:-1].replace('),(', '):(').split(':'):
			xy = p[1:-1].split(',')
			plist.append(xy[1] +','+ xy[0])
		print "~eval|if (! list_regionn.hasOwnProperty(%s)) { list_regionn[%s] = L.polygon([[%s]], {color: 'red', opacity: 0.2}).addTo(mymap); }" % (cod_region, cod_region, '],['.join(plist))	#, cod_region)
		### Anti Snow
		print "~log| Anti Snow cod_region:", cod_region
	#	return
		out_streets (request)
	else:	print "~eval| clear_map_object (list_regionn);"

def	out_streets (request, scateg = 'AB'):
	""" Показать территории уборки снега	"""
	cod_region = request.get('cod_region')
	try:
		asnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
	#	query = "SELECT plgn, idp, porder, tcreate, v.categ FROM polygons p, vplabel v WHERE p.id_lab = v.id_lab AND v.region = %s ORDER BY idp, porder;" % cod_region	### Все Дороги
		if scateg == 'AB':
			query = "SELECT plgn, idp, porder, tcreate, categ FROM polygons WHERE region = %s AND categ < 3 ORDER BY idp, porder" % cod_region	### Дороги категории А, Б ТОЛЬКО
		else:	query = "SELECT plgn, idp, porder, tcreate, categ FROM polygons WHERE region = %s ORDER BY idp, porder" % cod_region			### Все Дороги
		print query
		rows = asnow.get_rows (query)
		if rows:
			for r in rows:
				plgn, idp, porder, tcreate, categ = r
				if not porder:	porder = 0
				ind = 10*idp +porder
				plist = []
				for p in plgn[1:-1].replace('),(', '):(').split(':'):
					xy = p[1:-1].split(',')
					plist.append(xy[1] +','+ xy[0])
			#	print idp, porder, ind, plist
				print "~eval|if (! list_regionn.hasOwnProperty(%s)) { list_regionn[%s] = L.polygon([[%s]], {color: '#aa00bb', opacity: 0.2}).addTo(mymap); }" % (ind, ind, '],['.join(plist))
	except:	print "~log|except: out_streets"

def	get_olist (bm_ssys = None):
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	olist = {}
	if not bm_ssys:	bm_ssys = 131072	# ДТ-НН АнтиСнег
#	res = dbi.get_table ('org_desc', 'inn > 0 ORDER BY bname')
#	res = dbi.get_table ('org_desc', 'inn > 0 AND stat & 1 = 1 ORDER BY bname')
	res = dbi.get_table ('org_desc', 'inn > 0 AND stat & 1 = 1 AND bm_ssys & %s = %s ORDER BY bname' % (bm_ssys, bm_ssys))
	if res:
		d = res[0]
		for r in res[1]:	olist[r[d.index('inn')]] = (r[d.index('bname')], r[d.index('count_ts')])
	return	olist

def	set_organizations (request):
	sout = ["""<div class="wffront" style="width: 550px; max-width: 90%">"""]
	
	bm_ssys = request.get('bm_ssys')
	orgs_list = get_olist (bm_ssys)
	org_inn = request.get('org_inn')
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		int_inn = int(org_inn)
		sout.append ("""
		<div class='list-group-item list-group-item-action'>
			<span class='line tit' onclick="document.myForm.org_inn.value=0; $('#widget').html(''); set_shadow ('get_transport');">Выбрать ВСЕ организации</span>
			<span class="float-right">%s</span>
		</div>""" % img_close)
	else:
		int_inn = 0
		sout.append ("""<div class='list-group-item list-group-item-action active'><span class='tit'>Выбрать организацию:</span><span class="float-right">%s</span></div>""" % img_close)
	
	sout.append("""<ul class='list-group'>""")
	for inn in orgs_list.keys():
		if int_inn and int_inn == inn:
			sout.append("""<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center active'>%s<span class="badge badge-light badge-pill">%s</span></li>""" % (
				orgs_list[inn][0], orgs_list[inn][1]))
		else:	
			sout.append("""<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'
				onclick="document.myForm.org_inn.value=%d; $('#widget').html(''); set_shadow ('get_transport');">%s<span class="badge badge-primary badge-pill">%s</span></li>""" % (
				inn, orgs_list[inn][0], orgs_list[inn][1]))
	sout.append("</ul>")
	sout.append('</div>')
	return	'\n'.join(sout)

def	update_recv_ts (request):
	dbcntr = dbtools.dbtools('host=212.193.103.20 dbname=contracts port=5432 user=smirnov')
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	org_inn = request.get('org_inn')
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		swhere = "inn = %s" % org_inn
	else:
		bm_ssys = request.get('bm_ssys')
		swhere = "o.bm_ssys=131072"
		if bm_ssys and bm_ssys.isdigit() and int(bm_ssys) > 0:
			rs = dbi.get_rows ("SELECT inn FROM org_desc WHERE bm_ssys = %s;" % bm_ssys)
			if rs:
				inns = []
				for r in rs:	inns.append(str(r[0]))
				swhere = "inn IN (%s)" % ', '.join(inns)
#	query = "SELECT id_ts, gosnum, marka, a.device_id, inn, uin FROM transports t, organizations o, atts a WHERE %s AND t.id_org = o.id_org AND id_ts = autos AND a.last_date > '%s' ORDER BY o.id_org;" % (
#		swhere, time.strftime("%Y-%m-%d 00:00:00", time.localtime (time.time ())))
	query = "SELECT id_ts, gosnum, marka, a.device_id, inn, uin FROM transports t, organizations o, atts a WHERE %s AND t.id_org = o.id_org AND id_ts = autos ORDER BY o.id_org;" % swhere
#	print query
	'''
	return
	'''
	gnum_list = []
	rows = dbcntr.get_rows (query)
	if not rows:
		print query
		return
	for r in rows:
		id_ts, gosnum, marka, device_id, inn, uin = r
		gnum_list.append(gosnum)
		if marka:
			marka = "'%s'" % marka
		else:	marka = "NULL"
		if device_id < 0:
#			print "WWW\t", id_ts, gosnum, marka, device_id, inn
			rw = dbi.get_row ("SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, uin))
			if rw:
				g, d, i = rw
				if gosnum == g and uin == d and inn == i:
					print "Wialon\t", id_ts, gosnum, marka, device_id, inn
			else:
				query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('idd%s', %s, '%s', %s, %s, 0)" % (uin, inn, gosnum, marka, uin)
				print "Wialon\t", query, dbi.qexecute (query)
			continue
		rr = dbi.get_row ("SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id))
		if rr:
			g, d, i = rr
			if device_id < 0 and gosnum == g :		continue 
			if gosnum == g and device_id == d and inn == i:	continue
	#		print g, d, i, '!=\t'
			query = "DELETE FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id)
	#		print query, dbi.qexecute (query)
			dbi.qexecute (query)
		query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('idd%s', %s, '%s', %s, %s, 0)" % (device_id, inn, gosnum, marka, device_id)
	#	print query, dbi.qexecute (query)
		dbi.qexecute (query)
#	print "UPDATE org_desc SET count_ts",
	dbi.qexecute ("UPDATE org_desc SET count_ts = (SELECT count(*) FROM recv_ts WHERE org_desc.inn = recv_ts.inn);")
#	print	"gnum_list:", "', '".join(gnum_list)

def	check_autos (request):
	# wffront
	currtm = int(time.time())
	print	request.get('bm_ssys'), request.get('org_inn')
	sout = ["""<div class="wffront" style="width: 560px; max-width: 90%%; min-height: 550px; left: 800px; ">
	<div class='list-group-item list-group-item-action active'><span class='tit'>Транспорт</span><span class="float-right">%s</span></div> """ % img_close]
	sout.append("""<ul class='list-group'>""")
	sout.append("<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>")
	sout.append("""<input type='button' class='butt' onclick="set_shadow ('update_recv_ts');" value='Обновить списки ТС' />	""")
	categ_ts = request.get('categ_ts')
	sout.append ("""<span>Категория ТС:<select class='select' name='categ_ts' onchange="if (document.myForm.org_inn.value != '') set_shadow('check_autos');">""")
	if categ_ts == '1':
		sout.append("""<option value=''> </option><option value='1' selected> 1 </option><option value='2'> 2 </option><option value='X'> X </option></select></span>""")
	elif categ_ts == '2':
		sout.append("""<option value=''> </option><option value='1'> 1 </option><option value='2' selected> 2 </option><option value='X'> X </option></select></span>""")
	elif categ_ts == 'X':
		sout.append("""<option value=''> </option><option value='1'> 1 </option><option value='2'> 2 </option><option value='X' selected> X </option></select></span>""")
	else:	sout.append("""<option value=''> </option><option value='1'> 1 </option><option value='2'> 2 </option><option value='X'> X </option></select></span>""")
#	sout.append ("#"*22 +'<br>')

	sout.append("</li>")
	sout.append("<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>")
	bm_ssys = request.get('bm_ssys')
	org_inn = request.get('org_inn')
#	print bm_ssys
	sout.append (""" Организация:
	<select class='select' name='set_inn' onchange="document.myForm.org_inn.value=document.myForm.set_inn.value; set_shadow('check_autos');" > <option value=0>  </option>
	""")
	orgs_list = get_olist (bm_ssys)
	for inn in orgs_list.keys():
		if str(inn) == org_inn:
			sout.append ("<option value=%s selected > %s </option>" % (inn, orgs_list[inn][0]))
		else:	sout.append ("<option value=%s> %s </option>" % (inn, orgs_list[inn][0]))
	sout.append ("</select>")
	sout.append("</li>")
	sout.append("""<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>
	<div style='width: 100%; min-height: 500px; max-height: 700px; overflow: auto;'>
	<table style='width: 100%;'>""")
	ts_list = []
	if org_inn.isdigit() and int(org_inn) > 0:
		dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
		if categ_ts == '1':
			query = "SELECT gosnum, marka, device_id, stat_ts FROM recv_ts WHERE inn = %s AND stat_ts = %s" % (org_inn, categ_ts)
		elif categ_ts == '2':
			query = "SELECT gosnum, marka, device_id, stat_ts FROM recv_ts WHERE inn = %s AND stat_ts = %s" % (org_inn, categ_ts)
		elif categ_ts == 'X':
			query = "SELECT gosnum, marka, device_id, stat_ts FROM recv_ts WHERE inn = %s AND stat_ts > 0" % org_inn
		else:	query = "SELECT gosnum, marka, device_id, stat_ts FROM recv_ts WHERE inn = %s" % org_inn
		print query
		ts_list = dbi.get_rows (query)
		for r in ts_list:
			gosnum, marka, device_id, stat_ts = r
			rlp = dbi.get_row ("SELECT t FROM last_pos WHERE idd = '%s';" % device_id)
			if not rlp:
				srlp = "<span class='bferr'>Нет данных</span>"
			else:
				if currtm - rlp[0] > 86400:
					srlp = time.strftime("<span class='bfligt'>%d.%m.%Y </span>", time.localtime(rlp[0]))
				else:	srlp = time.strftime("<span class='bfinf'>%H:%M:%S </span>", time.localtime(rlp[0]))
			sout.append ("<tr><td> %s </td><td>%s<td><td> %s </td><td> %s </td></tr>" % (gosnum, marka, srlp, stat_ts))	#(r[3], r[4]))
	#		print r, '<br>'
	sout.append("</table></div></li>")
	if len(ts_list) > 0:
		sout.append("<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'><span class='finf sz12'>Найдено %s машин.</span></li>" % len(ts_list))
	sout.append("</ul>")
	sout.append('</div>')
	return	'\n'.join(sout)

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
	""" Обновить информацию о транспорте организаций РНИС	"""
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
	
def	view_routes (request):
	global	ACTIV_ROUTES
	'''
	print "view_routes", request
	'''
	HTTP_REFERER = os.environ.get('HTTP_REFERER')
	if 'atp.html' in HTTP_REFERER:
		import	polylineutility as pline
		check_route = True
		get_route ('987654321')
		j = 0
		if request.has_key('view_routes') and request['view_routes'] == 'on':
			print "~eval| clear_map_object (list_routes); document.myForm.view_routes.value = 'off';"
			return
		else:	print "~eval| clear_map_object (list_routes); document.myForm.view_routes.value = 'on';"
	#	return
		k = 0
		for r in ACTIV_ROUTES:
			j += 1
	#		print	r.keys()
			for l in r['st']:
				if not l['p']:	continue
				k += 1
				'''
				Jm = 100*j +l['i']
				print l['id'], ['i'], l['p'],
				'''
				ps = pline.decode (l['p'], 'list')
			#	print 	Jm, ps
			#	print "list_routes[%d] = new L.Polyline(%s, { color: 'red', weight: 5, opacity: 0.2 }).addTo(mymap);" % (l['id'], str(ps))
				print "list_routes[%d] = new L.Polyline(%s, { color: 'red', weight: 5, opacity: 0.2 }).addTo(mymap);" % (k, str(ps))
		return

def	view_trace (request, dtime = None):
#	print 'view_trace', request.get('set')
	if request.get('set')  != 'on' and request['view_trace'] == 'on':
		print "~eval| clear_map_object (list_tracks); document.myForm.view_trace.value = 'off';"
	else:	print "~eval| document.myForm.view_trace.value = 'on';"
	return
	points = []	# '56.5,44', '57,44', '57,43.5', '56.5, 43.5' ]
#	print "~eval| clear_map_object(list_tracks); list_tracks[%s] = new L.Polyline([[%s]], { color: 'blue', weight: 3, opacity: 0.5 }).addTo(mymap); mymap.fitBounds(list_tracks['blue'].getBounds());" % (j, "],[".join(points) )
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	bm_ssys = request.get('bm_ssys')
	if bm_ssys and bm_ssys.isdigit():
		and_bm_ssys = "AND tinn IN (SELECT inn FROM org_desc WHERE bm_ssys = %s)" % bm_ssys
	else:	and_bm_ssys = ""
#	print "and_bm_ssys", and_bm_ssys
	if not dtime:
		HTTP_REFERER = os.environ.get('HTTP_REFERER')
		if 'atp.html' in HTTP_REFERER:
			dtime = 90
		else:	dtime = 3600
	elif type(dtime) == str:
		dtime = int(dtime)
	res = dbi.get_table ('vdata_pos', "t > %d AND x > 0 %s ORDER BY ida, t " % (int(time.time()) - dtime, and_bm_ssys))
	if not res:
#		print "view_trace: Нет данных!"
		return
	d = res[0]
	gosnum = ''
	j = 0
	print "~eval| clear_map_object (list_tracks); document.myForm.view_trace.value = 'on';"
	for r in res[1]:
		if gosnum and gosnum != r[d.index('gosnum')]:
			if not points:	continue
			j += 1
			print "list_tracks[%s] = new L.Polyline([[%s]], { color: 'blue', weight: 7, opacity: 0.3 }).addTo(mymap);" % ( j, "],[".join(points) )
			points = [ "%s, %s" % (float(r[d.index('y')]), float(r[d.index('x')])) ]
			gosnum = r[d.index('gosnum')]
		elif gosnum == "":
			gosnum = r[d.index('gosnum')]
		else:
			points.append ("%s, %s" % (float(r[d.index('y')]), float(r[d.index('x')])))
	if points:
		j += 1
		print "list_tracks[%s] = new L.Polyline([[%s]], { color: 'blue', weight: 7, opacity: 0.3 }).addTo(mymap);" % (j, "],[".join(points) )
#	print "~eval| set_shadow ('get_transport');"

def	snow_zone (request):
	znames = ['autozavod.json', 'kanavino.json', 'lenin.json', 'moskva.json', 'nijegorod.json', 'priofski.json', 'sovetski.json', 'sormovo.json']
	zn = request.get('zone_name')
#	print "QQQ=", zn, 1+znames.index(zn)
	request['cod_region'] = 1+znames.index(zn)
	print request
	return	out_streets (request, scateg = 'ALL')

def	table_mask ():
	dbasnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
#	select * FROM pmask WHERE lon > 2550 AND lon < 4000 AND lat > 1050 AND lat < 1500 AND tlife >=0;
	import p4_test as p4
	mask = p4.pmask()
	step = 500
	print "<table cellpadding=4 cellspacing=0 >"
	for k in xrange (mask.des / step, 0, -1):
		print "<tr>",
		for j in xrange (mask.des / step):
		#	print "<td>", j,k, "</td>",
			row = dbasnow.get_row ("select count(*) FROM pmask WHERE lon > %d AND lon < %d AND lat > %d AND lat < %d" % (j*step, (1+j)*step, (k-1)*step, (k)*step))
			if row[0]:
				print """<td><img src='../img/pix_gw.gif' width='22' height='22' onclick="alert('[%d,%d]');"></td>""" % (j,k),
			else:
				print "<td><img src='../img/pix_gr.gif' width='22' height='22'></td>",
		print "</tr>"
	print "<table>"
	print	""" <img src='../img/pixel_g.gif' width='22' height='22'> <img src='../img/pixel_r.gif' width='22' height='22'> <img src='../img/pix_gr.gif' width='22' height='22'>
		<img src='../img/pix_gw.gif' width='22' height='22'> <img src='../img/pix_mg.gif' width='22' height='22'> <img src='../img/pix_y.gif' width='22' height='22'>
		"""		
	
def	snow_opts (request):
	import p4_test as p4
	mask = p4.pmask()
	if request['shstat'] == 'snow_info':
		step = 500
		print 'mask.des', mask.des
		jlines = []
		for j in xrange (1 + mask.des / step):
			gxu, gyu = mask.xy2point((j*step, 0))
			gxd, gyd = mask.xy2point((j*step, mask.des))
			jlines.append ("[%s,%s],[%s,%s]" % (gyu, gxu, gyd, gxd))
	#		print "X:", j*step
		for j in xrange (1 + mask.des / step):
			gxu, gyu = mask.xy2point((0, j*step))
			gxd, gyd = mask.xy2point((mask.des, j*step))
			jlines.append ("[%s,%s],[%s,%s]" % (gyu, gxu, gyd, gxd))
	#		print "Y:", j*step
		print "~eval| clear_map_object(list_tracks); list_tracks[%s] = new L.Polyline([[%s]], { color: 'red', weight: 3, opacity: 0.1 }).addTo(mymap); mymap.fitBounds(list_tracks['blue'].getBounds());" % (1, "],[".join(jlines) )
		'''
		'''
		points = [ '56.325687, 43.992991', '56.325687, 44.013162', '56.330910, 44.013162', '56.330909840829506, 43.99299144744873' ]
	#	points = [ '56.325687, 43.992991', '56.392561, 43.742758', '56.392561, 44.171311', '56.159955, 44.171311', '56.159955, 43.742758', '56.392561, 44.171311' ]
		print "~eval| clear_map_object(list_tracks); list_tracks[%s] = new L.Polyline([[%s]], { color: 'red', weight: 3, opacity: 0.5 }).addTo(mymap); mymap.fitBounds(list_tracks['blue'].getBounds());" % (11, "],[".join(points) )
	elif request['shstat'] == 'snow_to_send':
		print "~log|snow_to_send"
		dbasnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
	#	rid | tevent | gosnum | quality | slines
		rows = dbasnow.get_rows ("select * FROM to_send ORDER BY tevent DESC")	# LIMIT 100")	# WHERE id < 1111"):
		print dbasnow.desc, len (rows)
		print "~eval| clear_map_object(list_tracks);"
		for r in rows:
			rid, tevent, gosnum, quality, slines = r
			jlines = eval(slines)
			if jlines:
				olines = []
			#	print gosnum, quality, len(jlines)
			#	print jlines
				for l in jlines:
				#	print l, len(l)
					ol = []
					for p in l:	ol.append ([p[1], p[0]])
				#	print ol, len(ol)
					olines.append(ol)
			#	print len (olines)
			#	print olines
				if r[dbasnow.desc.index('quality')][0] == '1':
					color = '#ca0'
				elif r[dbasnow.desc.index('quality')][0] == '2':
					color = '#4a0'
				elif r[dbasnow.desc.index('quality')][0] == '3':
					color = '#085'
				else:	color = '#a0a'
				print "~eval| list_tracks['%s'] = new L.Polyline(%s, { color: '%s', weight: 10, opacity: 0.2 }).addTo(mymap);" % (r[dbasnow.desc.index('gosnum')], str(olines), color)

	elif request['shstat'] == 'snow_zone':
		'''
		print	"""<div class="wffront" style="width: 510px; max-width: 90% ">"""
		print	"""<div class='list-group-item list-group-item-action active'><span class='tit' onclick="$('#widget').html('');">&nbsp;Выбрать район города:</span><span class="float-right">%s</span></div>""" % img_close
		print	"</div>"
		'''
		snow_zone (request)
	elif request['shstat'] == 'snow_test':
		if request.has_key('region_id') and request['region_id'].isdigit() and int(request['region_id']) > 0:
			region_id = request['region_id']
		else:	region_id = 5
		if request.has_key('set_snow_stat') and request['set_snow_stat']:
			sand = request['set_snow_stat']
		else:	sand =  "AND curs > 0"
	#	select count(*) FROM pmask WHERE idp IN (select idp FROM polygons WHERE id_lab IN (select id_lab FROM plabel WHERE region = 1)) AND curs > 0;	
		rows = mask.get_pmask ('region = %s %s' % (region_id, sand))	#AND curs > 0' % region_id)
	###	rows = mask.get_pmask ('idp IN (select idp FROM polygons WHERE id_lab IN (select id_lab FROM plabel WHERE region = %s)) %s' % (region_id, sand))	#AND curs > 0' % region_id)
	#	rows = mask.get_pmask ('idp IN (select idp FROM polygons WHERE id_lab IN (select id_lab FROM plabel WHERE region = %s))' % region_id)			# ALL
	#	rows = mask.get_pmask ()
		dx = mask.lnx/mask.des	#0.428553
		dy = mask.lny/mask.des	#0.232606
		colors = ['red', 'green', 'blue', '#aaaa00', '#00aaaa', '#888888', '#666666', '#444444']
		lpoint = []
		j = 0
		jc_old = 0
		for r in rows:		# lon  | lat  | idp | curs |  tcreate   | tlife | stat | rem | idp 
			x = mask.x0+r[0]*dx
			y = mask.y0+r[1]*dy
			if r[3] > 0:
				jc = 1 + int(r[3]/90)
			elif r[3] == None:
				jc = 5
			else:	jc = 0
			if jc != jc_old:
				if lpoint:
					print "~eval| new L.polygon([[%s]], { color: '%s', opacity: 0.3 }).addTo(mymap);" % ("],[".join(lpoint), colors[jc_old])
				lpoint = []
				jc_old = jc
		#	print r, mask.x0+x, mask.y0+y
		#	print "[%f,%f], [%f,%f], [%f,%f], [%f,%f],[%f,%f]" % (y,x, y,x+dx, y+dy,x+dx, y+dy,x, y,x)
			lpoint.append("[%f,%f], [%f,%f], [%f,%f], [%f,%f],[%f,%f]" % (y,x, y,x-dx, y-dy,x-dx, y-dy,x, y,x))
			j += 1

	#	print "~eval| new L.polygon([[%s]], { color: 'red', opacity: 0.2 }).addTo(mymap);" % "],[".join(lpoint)
	#	print "~eval| new L.polygon([[[44.0, 57.0], [41.0, 57.0], [41.0, 56.0], [44.0, 56.0], [44.0, 57.0]], [[57.0, 44.0],[56.0,41.0],[56.0,44.0],[57.0, 44.0]]], { color: 'red', opacity: 0.5 }).addTo(mymap);"

	elif request['shstat'] == 'snow_opts':
		dbasnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
		conf = mask.get_config()
		print "~widget|<div class='wffront' style='width:540px; max-width: 90%; left: 900px;'>"
		print """<div class='list-group-item list-group-item-action active'><span class='tit'>Параметры:</span><span class="float-right">%s</span></div>""" % img_close
	
		print """<ul class='list-group'>"""
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>Идет снег:
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_to_send');">
			Как идет уборка</span><span class="badge badge-light badge-pill">
			<select name='set_snow_flag' class='ssel' onchange="set_shadow('snow_opts');">
			<option value='0'> Нет </option><option value='1'> Да </option><option value='2'> Сильный </option></select> </span></li>"""

		''' ####
		if not os.environ['REMOTE_ADDR'] in ['10.10.2.40']:
			print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'><pre>"""
			print	"%20s:" % 'REMOTE_ADDR', os.environ['REMOTE_ADDR']
			for k in request.keys():	print	"%20s:" % k, request[k]
			print	"</pre></li></ul></div>"
			return
		###	
	#	print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>%s<span class="badge badge-light badge-pill">%s</span></li>""" % ('123456', 654321)
		for k in os.environ.keys():	print k	, os.environ[k]
		if not os.environ['REMOTE_ADDR'] in ['10.10.2.40']:
		'''
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'><pre style='font-size: 80%'>"""
		print	'%8s:' % 'zone', conf.get('zone')
		print	'%8s:' % 'ln_xy', conf.get('ln_xy')
		print	'%8s:' % 'stp_xy', conf.get('stp_xy')
		for k in ['des', 'max_speed', 'd_curs', 'debug']:	print	'%8s:' %k, conf.get(k),
		print "</pre></li>"

		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>Статус маски<span class="badge badge-light badge-pill">
			<select name='set_snow_stat' class='ssel' onchange="document.myForm.snow_stat.value = document.myForm.set_snow_stat.value;">
			<option value=''> None </option> <option value='AND stat = 0'> stat = 0 </option> <option value='AND stat >= 0'> stat >= 0 </option>
			<option value='AND stat > 0'> stat > 0 </option>
			<option value='AND stat IS NULL'> stat IS NULL </option>
			<option value='AND categ = 1'> categ = A </option>
			<option value='AND categ = 2'> categ = B </option>
			<option value='AND categ > 2'> categ Прочие </option>
			<option value='AND categ IS NULL'> categ IS NULL </option>
			</select></span></li>"""

		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center active'>Выбор района города
			<span class="badge badge-light badge-pill" onclick="clear_map_object (list_streets);">Очистить</span></li>"""
		if os.environ['REMOTE_ADDR'] in ['10.10.2.40']:
			print """
			<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'> <ul>
			<li><span onclick="set_shadow ('snow_zone&zone_name=autozavod.json');">Автозаводский</span> </li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=kanavino.json');">Канавинский</span> </li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=lenin.json');">Ленинский</span> </li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=moskva.json');">Московский</span> </li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=nijegorod.json');">Нижегородский</span> </li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=priofski.json');">Приокский</span> </li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=sovetski.json');">Советский</span> </li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=sormovo.json');">Сормовский</span> </li>
			</ul></li>
			"""	
		else:
			print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'> <ul>
			<li><span onclick="set_shadow ('snow_zone&zone_name=autozavod.json');">Автозаводский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=1');">Сетка</li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=kanavino.json');">Канавинский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=2');">Сетка</li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=lenin.json');">Ленинский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=3');">Сетка</li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=moskva.json');">Московский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=4');">Сетка</li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=nijegorod.json');">Нижегородский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=5');">Сетка</li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=priofski.json');">Приокский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=6');">Сетка</li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=sovetski.json');">Советский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=7');">Сетка</li>
			<li><span onclick="set_shadow ('snow_zone&zone_name=sormovo.json');">Сормовский</span>
			<span class="badge badge-light badge-pill" onclick="set_shadow('snow_test&region_id=8');">Сетка</li>
			</ul></li>"""
		
		print	"</div></div>"
		return	####
#		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center active' onclick="document.myForm.org_inn.value=%d; $('#widget').html(''); set_shadow ('get_transport');">%s<span class="badge badge-primary badge-pill">%s</span></li>""" % (987654, 'qwer', 'QWERT')
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center active'>Карта<span class="badge badge-primary badge-pill">QWER</span></li>"""
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-cente'>"""
		table_mask ()
		print "</li>"
		print "</ul>"
		print "</div>"
		print "</div>"
		snow_flag = request.get('set_snow_flag')
		if snow_flag == None:
			drow = dbasnow.get_dict("SELECT * FROM snow_opts WHERE oname = 'snow_flag'")
			if drow['ival']:
				snow_flag = drow['ival']
			else:	snow_flag = 0
		else:
			if snow_flag and snow_flag.isdigit():
				snow_flag  = int (snow_flag)
			else:	snow_flag = 0
			drow = dbasnow.get_dict("SELECT * FROM snow_opts WHERE oname = 'snow_flag'")
			if snow_flag != drow['ival']:
				query = "UPDATE snow_opts SET ival = %s, change_tm = %s WHERE oname = 'snow_flag'" % (snow_flag, int(time.time()))
				print '~log|', query, dbasnow.qexecute(query)
			else:	snow_flag = drow['ival']
		print "~eval|document.myForm.set_snow_flag.value='%s';" % snow_flag
	else:	return
	return
###
def	select_org (org_inn, bm_ssys, sshadow):
	sout = []
	sout.append (""" Организация:
	<select class='select' name='set_inn' onchange="document.myForm.org_inn.value=document.myForm.set_inn.value; set_shadow('%s');" > <option value=0>  </option>
	""" % sshadow)
	orgs_list = get_olist (bm_ssys)
	for inn in orgs_list.keys():
		if str(inn) == org_inn:
			sout.append ("<option value=%s selected > %s </option>" % (inn, orgs_list[inn][0]))
		else:	sout.append ("<option value=%s> %s </option>" % (inn, orgs_list[inn][0]))
	sout.append ("</select>")
	return	sout


def	view_streets (request):
	#	select id_dp, gosnum, max(st) FROM vdata_pos GROUP BY id_dp;
	#	receiver=# select gosnum, max(st) FROM vdata_pos GROUP BY gosnum;
	import	rnic_wtranport as rwt

#	dbc = dbtools.dbtools('host=212.193.103.20 dbname=contracts port=5432 user=smirnov')
	
	org_inn = request.get('org_inn')
	bm_ssys = request.get('bm_ssys')
	sel_org  = select_org (org_inn, bm_ssys, 'set_opts')
	and_opts = [
		('AND last_date IS NOT NULL','Передавали данные'), ('AND last_date IS NULL','Нет данных'),
		('AND last_date IS NOT NULL AND bm_wtime & 7 = 0','Нет сегодня'), ('AND last_date IS NOT NULL AND bm_wtime = 0','Нет 10 дней'),
		('quality', 'Сомнительное качество'),
		]
	sel_and	= [
		""" AND:<select class='select' name='set_and' onchange="document.myForm.org_inn.value=document.myForm.set_inn.value; set_shadow('set_opts');" > <option value=''>  </option>""",
	]
	jand = request.get('set_and')
	if not jand:	jand = ''
	for v,t in and_opts:
		if jand == v:
			sel_and.append ("<option value='%s' selected> %s </option>" % (v,t))
		else:	sel_and.append ("<option value='%s'> %s </option>" % (v,t))
	sel_and.append ("</select>")
	xls = """<a href='http://212.193.103.21/tmp/example.xls'><i class='fa fa-table fa-lg' aria-hidden='true' style='color: #fff;' title='XLS'></i></a>"""

	print "~widget|<div class='wffront' style='width:90%; max-width: 99%; left: 120px;'>"
	print """<div class='list-group-item list-group-item-action active'><span class='tit'>%s &nbsp;&nbsp;&nbsp; </span><span class="float-center"> %s &nbsp; %s </span><span class="float-right"> %s &nbsp; %s </span></div>""" % (
		"Состояние транспорта", '\n'.join(sel_org), '\n'.join(sel_and), xls, img_close)

	rwt.view_wtranport (org_inn, bm_ssys, sel_org, jand)
	print "</div>"
	return

	'''
	fdata = r"/home/smirnov/MyTests/Wialon/data/roads.json"		# EPSG:3857
#	fdata = r"/home/smirnov/MyTests/Wialon/data/EPSG.json"		# EPSG:3857 London
#	fdata = r"/home/smirnov/MyTests/Wialon/data/exampls.json"	# WGS84
	f = open (fdata, 'r')
	data = f.read()
#	print eval(data)
#	print "~eval| geoLayer = new L.Proj.geoJson(%s).addTo(mymap);" % data	# EPSG:3857
	print "~eval| clear_map_object (list_streets);	list_streets [1]= new L.Proj.geoJson(%s).addTo(mymap);" % data	# EPSG:3857
#	print '~eval| geoLayer.addData (%s); ' % data				# WGS84
	'''

bus_wialon = [
	(353218079413564, 644), (351555060040902, 711), (863591026155659, 1015), (353218079413051, 679), (351555060044862, 677), (351555060041124, 714), (351555060045182, 821),
	(351555060041157, 698), (351555060041033, 652), (351555060045455, 893), (355217047495263, 754), (353218079412475, 817), (863591026159974, 1013), (351555060031117, 820),
	(351555060045406, 822), (351555060045158, 696), (351555060040811, 674), (351555060044565, 818), (353218079118122, 782), (351555060044201, 1048), (863591026169668, 1068),
	(353218079422672, 643), (351555060025960, 705), (353218079117678, 675), (863591026147730, 1070), (91395, 702), (351555060030994, 755), (351555060038559, 703),
	(355217047488664, 710), (351555060044656, 650), (863591026088173, 1016), (351555060044623, 651), (351555060045380, 667), (863591026080808, 1014), (351555060043815, 692),
	(351555060041538, 783), (351555060044284, 656), (353218079413804, 676), (351555060045018, 695), (863591026087829, 1069), (355217047500740, 671), (351555060040985, 713),
	(351555060045372, 683), (355217047496220, 678), (351555060045281, 709), (351555060043591, 670), (351555060045265, 655), (351555060045331, 751), (351555060041199, 697),
	(351555060044896, 694), (351555060040894, 780), (351555060043831, 666), (351555060041702, 686), (355217047498275, 706), (351555060045208, 707), (351555060040977, 642),
	(355217047495628, 681), (351555060044532, 654), (355217047501177, 748), (351555060044276, 781), (355217047495487, 757), (351555060045463, 645), (351555060035696, 699),
	(351555060040852, 669), (110225, 689), (351555060044722, 693), (351555060043559, 664), (109615, 715), (355217047501540, 749), (355217047495719, 673),
	(353218079118221, 688), (353218079412459, 665), (351555060044144, 752), (351555060044763, 685), (351555060043310, 646), (355217047497046, 680), (351555060044268, 649),
	(351555060044540, 647), (355217047486338, 753), (351555060044813, 653), (351555060041231, 701), (351555060045083, 648), (353218079413549, 690), (351555060041587, 756),
	(351555060043740, 712),
	]

if __name__ == "__main__":
	request = {'this': 'ajax', 'org_inn': '0', 'shstat': 'update_ts_list', 'leaflet-base-layers': 'on'} 
	print update_ts_list (request)
	print get_olist()
	'''
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	for uin, did in bus_wialon:
	#	print "SELECT * FROM recv_ts WHERE device_id = %s AND inn = 5246034418;" % uin	#, did
		query = "UPDATE recv_ts SET idd = '%s' WHERE device_id = %s AND inn = 5246034418;" % (did, uin)
		print query, dbi.qexecute(query)
	'''
