#!/usr/bin/python -u
# -*- coding: utf-8 -*-
""" 	Инструменты для http://212.193.103.21/tmp/at_pp.html
	Пассажирские перевозки
"""
import	os, sys
import	time, json

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools

dbrecv = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
'''
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


def	get_vlast_pos (request):
	""" Читать транспорт по ИНН	"""
	print "~evant| alett('Читать транспорт по ИНН')"
	org_inn = request.get('org_inn')
	bm_ssys = '2'
	
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		res = dbrecv.get_table('vlast_pos', 'tinn = %s ORDER BY t DESC' % org_inn)
	elif bm_ssys and bm_ssys.isdigit():
		res = dbrecv.get_table('vlast_pos', 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s = %s) ORDER BY t DESC' % (bm_ssys, bm_ssys))
	else:	res = dbrecv.get_table('vlast_pos', 'tinn >0 ORDER BY t DESC')
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
		if res:
			opts = {'icon': icon, 'gosnum': "<b> %s </b>" % r[d.index('gosnum')], 'dt': '%s' % str_time (r[d.index('t')], jtm).replace("'", '')}
			if r[d.index('sp')] and r[d.index('sp')] > 0:
				opts['sp'] = ' &nbsp; v:%dкм/ч' % r[d.index('sp')]
			else:	opts['sp'] = ' &nbsp; <span class=bferr>Стоит</span>'
			ddd.append([[float(r[d.index('y')]), float(r[d.index('x')])], opts])
		else:
			if r[d.index('bname')] and r[d.index('bname')] != '':
				gosnum += '<br><b>%s</b>' % r[d.index('bname')].replace('"', " ")
			if r[d.index('marka')]:	gosnum += '<br>' +r[d.index('marka')]
			ddd.append([float(r[d.index('x')]), float(r[d.index('y')]), '%s' % str_time (r[d.index('t')], jtm).replace("'", ''), gosnum, icon])
	return	ddd
'''

def	get_srops (org_inn):
#	res = dbrecv.get_table ('first', "inn = %s LIMIT 55" % org_inn)
#	res = dbrecv.get_table ('first', "inn = %s AND ritm > 2100120610020020" % org_inn)
#	res = dbrecv.get_table ('first', "inn = %s AND stat < 0" % org_inn)
	res = dbrecv.get_table ('first', "inn = %s AND stat >= 0" % org_inn)
#	res = dbrecv.get_table ('first', "inn = %s " % org_inn)
	if not res:	return
	d = res[0]
	ddd = []
#	print	d
	for r in res[1]:
		opts = {}
		x,y = r[d.index('center')][1:-1].split(',')
		opts['tm'] = time.strftime("%T %d.%m.%Y", time.localtime (r[d.index('tm_mod')]))
		opts['r'] = '%6.2f' % float(r[d.index('r')])
		for c in ['jpt', 'jptmax', 'stat', 'nm']:
			opts[c] = r[d.index(c)] 
		ddd.append([[float(y), float(x)], opts])
#		print y, x, opts
#	for s in ddd:	print s
	return	ddd


def	view_stops (request):
#	print "~widget| view_stops", request
	list_stops = get_srops (request.get('org_inn'))
	print "~eval| out_stops('%s');" % json.dumps(list_stops)
	'''
	ts_list = get_vlast_pos (request)
	print "~eval| out_data('%s');" % json.dumps(ts_list)
	'''


def	get_orgs (inn = None):
	""" Читать список Организаций	"""
#	{'id_org': 401, 'inn': 5243019838, 'bname': 'МУП "АПАТ" Арзамас'},
#	{'id_org': 728, 'inn': 5246034418, 'bname': 'МУП "Борское ПАП"'}
	rows = dbrecv.get_rows ("SELECT * FROM org_desc WHERE bm_ssys = 2 ORDER BY bname")
	d = dbrecv.desc
	list_li = []
	if inn and inn.isdigit():
		iinn = int(inn)
	else:	iinn = 0
	format_li = """ <li class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" onclick="%s"> %s </li>"""
	for r in rows:
		inn = r[d.index('inn')]
		if r[d.index('place')]:
			x, y = r[d.index('place')][1:-1].split(',')
			if r[d.index('zoom')]:
				zoom = r[d.index('zoom')]
			else:	zoom = 9
			sonclick = "document.myForm.org_inn.value='%s'; $('#widget').html(''); mymap.setView([%s,%s], %s); start_ws();" % (inn, y, x, zoom)
		else:	sonclick = "document.myForm.org_inn.value='%s'; $('#widget').html(''); start_ws();" % inn
		if inn == iinn:
			list_li.append (format_li % (sonclick, "<span class='bfinf'>%s &nbsp; %s </span>" % (inn, r[d.index('bname')])))
		else:	list_li.append (format_li % (sonclick, "%s &nbsp; %s" % (inn, r[d.index('bname')])))
	return	"\n".join(list_li)


def	set_tspp (request):
	print """~widget|
	<div class="wffront" style="width: 560px; max-width: 90%%; max-height: 350px; left: 310px; ">
	<div class="list-group-item list-group-item-action active"><span class="tit">Список Организаций</span><span class="float-right"> org_inn: %s &nbsp;
		<i class="fa fa-times fa-lg" aria-hidden="true" onclick="$('#widget').html('')"></i>&nbsp;</span></div> 
	<ul class="list-group"> 
	""" % request.get('org_inn')
	print get_orgs(request.get('org_inn'))
	print "</ul></div>"

if __name__ == "__main__":
	view_stops ({'org_inn': '5243019838'})
#	set_tspp ([])
