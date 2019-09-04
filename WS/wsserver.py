#!/usr/bin/python -u
# -*- coding: utf-8 -*-
""" WebSocket сервер:
	- читает данные от NimBus и навигационные данные 
	- отправляет данные http://212.193.103.21/tmp/atp.html

	nohup /home/smirnov/MyTests/WS/wsserver.py > /home/smirnov/MyTests/log/wsserver.log  &
"""
import	os, sys, time
import	urllib, json

import struct	# из него нам нужна функция pack() и unpack_from()
import array	# функция array()
import socket	# Сами сокеты
import threading		# По потоку для каждого подключения
from	hashlib import sha1	#Кодирование Access Key о котором будет дальше 
from	base64 import b64encode	#Кодирование Access Key о котором будет дальше

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import	dbtools
import	nimbus

mutex_directory = threading.Lock()	# .acquire() .release()	with mutex_
mitex_dtmcodes = threading.Lock()
mitex_stops = threading.Lock()

GLOB_DIRECTORY = {}	# Kei = Unut ID	(code)	- ID Машины
MAX_DTM = 360
DTM_CODES = []
INN_CODES = {}

for j in xrange(MAX_DTM):	DTM_CODES.append(None)

TOKEN = 'Token 30e04452062e435a9b48740f19d56f45'	# ПП МУП Борское ПАП
DEPOT = 128
STOPS = {}		# Kei = sid - ID Остановки

def	get_srop (sid, rid, rkey = 'n'):
	""" 	sid - ID Остановки, rid - ID маршрута	"""
	global	STOPS, GLOB_DIRECTORY
	stp_dct = STOPS.get(sid)
	if stp_dct:
	#	print "stp_dct", stp_dct
		return	stp_dct.get(rkey)
	cmnd = 'depot/%s/stop/%s' % (DEPOT, sid)
	try:
		res = nimbus.u8api_nimbus (cmnd, TOKEN)
		if res['n']:
			nstp =	res['n']
		else:	nstp =	res['d']
#		print sid, rid, nstp
		with mitex_stops:
			STOPS[sid] = {'n': nstp, 'p': res['p'][0]}
		return	STOPS[sid].get(rkey)
	except:	pexcept ('get_srop')
		
def	get_panels (sid):	#, rid):
	global	GLOB_DIRECTORY
	cmnd = 'depot/%s/stop/%s/panel' % (DEPOT, sid)
	try:
		no_actual = {}
		panel = nimbus.u8api_nimbus (cmnd, TOKEN)
		for k in xrange(len(panel['r'])):
		#	print '\t', k, panel['r'][k]['n'], panel['r'][k]['fs'], panel['r'][k]['id'],
			fstp = panel['r'][k]['fs']
			lstp = panel['r'][k]['ls']
			srn = "%s" % panel['r'][k]['n']
			srem = "%s - %s" % (fstp, lstp)
			for i in xrange(len(panel['r'][k]['tt'])):
				if panel['r'][k]['tt'][i]['uid']:
					sunit_id = '%s' % panel['r'][k]['tt'][i]['uid']
					cdct = GLOB_DIRECTORY.get(sunit_id)
					if cdct:	# GLOB_DIRECTORY.get(sunit_id):
						if cdct.has_key('rn') and cdct.has_key('rem') and cdct['rn'] == srn and cdct['rem'] == srem:	continue
					#	print	"UP\t", srn, sunit_id, fstp, lstp
						with mutex_directory:
							cdct['rn'] = srn	#GLOB_DIRECTORY[sunit_id]['rn'] = srn
							cdct['rem'] = srem	#GLOB_DIRECTORY[sunit_id]['rem'] = srem
					else:
					#	print "--\t", srn, sunit_id, fstp, lstp
						no_actual [sunit_id] = [srn, fstp, lstp ]
		if no_actual:
		#	print "Not actual data:"
			for k in no_actual.keys():
				print "\tuid:", k,
				for s in no_actual[k]:	print "\t", s,
				print
		'''
		'''
	except:
		pexcept ('get_panels')
		time.sleep(11)

def	calc_rnumber ():
	print	"calc_rnumber"

def	actual_nimbus ():
	print	"actual_nimbus"
	global	STOPS, GLOB_DIRECTORY
	rout_dcts = []
#	rides = []
	try:
		cmnd = 'depot/%s/routes' % DEPOT	# ПП МУП Борское ПАП 
		res = nimbus.u8api_nimbus (cmnd, TOKEN)
		routes = res.get ('routes')
	#	print routes[0].keys()
		for r in routes:
			dct = {'id': r['id'], 'n': r.get('n')}
		#	if not (r.has_key('u') and r['u']):	continue
			st = r.get('st')
			fs = get_srop (st[0]['id'], r['id'])
			ls = get_srop (st[-1]['id'], r['id'])
			u = r.get('u')
			if u:
				dct['u'] = u
			rout_dcts.append (dct)	#{'n': "%s" % r.get('n'), 'u': r['u'], 'st': r['st']})
		for j in xrange(len(rout_dcts)):
			ulist = rout_dcts[j].get('u')
			if not ulist:	continue
			print rout_dcts[j]
			for unit_id in ulist:
				sunit_id = str(unit_id)
				if GLOB_DIRECTORY.get(sunit_id):
					with mutex_directory:
						GLOB_DIRECTORY[sunit_id]['rn'] = str(rout_dcts[j].get('n'))
			'''
				for unit_id in u:
					sunit_id = '%s' % unit_id
				#	if GLOB_DIRECTORY.get(sunit_id):
					with mutex_directory:
						GLOB_DIRECTORY[sunit_id]['rn'] = "? %s" % r.get('n') 
			'''
		while not exit_request:
		#	print "Update GLOB_DIRECTORY"
		#	print STOPS.keys()
			for sid in STOPS.keys():
				if exit_request:	break
				rrr = get_panels (sid)	#, rid)
			if not exit_request:	time.sleep(133)
			#	if rrr:			print rrr
		return
	except:	pexcept ('actual_nimbus')
	finally:
		print "#"*22, "actual_nimbus"
	#	for j in xrange(len(rout_dcts)):	print rout_dcts[j]
	#	sys.exit()	#os._exit()

import	inpolygon
def	actual_directory ():
	print	"actual_directory"
	global	GLOB_DIRECTORY, DTM_CODES, MAX_DTM
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	last_id = 0
	bm_ssys = 2
	j = 0
	while not exit_request:
		# 5246034418 | МУП "Борское ПАП"
		# 5256128672 | ООО "Транс-НН"
		iss_tinn = "tinn IN (5246034418, 5256128672)"
		if last_id == 0:
			'''
			rid = dbi.get_row ("SELECT max(id_dp) FROM vdata_pos WHERE tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s > 0)" % bm_ssys)
			last_id = rid[0]
			swhere = 'tinn IN (SELECT inn FROM org_desc WHERE stat > 0 AND bm_ssys & %s = %s)' % (bm_ssys, bm_ssys)
		###
			rid = dbi.get_row ("SELECT max(id_dp) FROM vdata_pos WHERE tinn = %d" % 5246034418)
			last_id = rid[0]
			swhere = 'tinn = %d' % 5246034418
			res = dbi.get_table('vlast_pos', swhere)
			'''
			rid = dbi.get_row ("SELECT max(id_dp) FROM vdata_pos WHERE %s" % iss_tinn)
			last_id = rid[0]
			res = dbi.get_table('vlast_pos', iss_tinn)
		else:
		#	swhere = 'tinn IN (SELECT inn FROM org_desc WHERE stat > 0 AND bm_ssys & %s = %s) AND id_dp > %s AND x > 0.0 ORDER BY t' % (bm_ssys, bm_ssys, last_id)
			# 5246034418 | МУП "Борское ПАП"
		###	swhere = 'tinn = %d AND id_dp > %s AND x > 0.0 ORDER BY t' % (5246034418, last_id)
			swhere = iss_tinn +' AND id_dp > %s AND x > 0.0 ORDER BY t' % last_id
			res = dbi.get_table('vdata_pos', swhere)
	#	print	'\tswhere:', swhere
		tm = int(time.time())
		jtm = tm % MAX_DTM
		if not res:
			with mitex_dtmcodes:
				DTM_CODES[jtm] = None
			continue
		codes = [tm]
		d = res[0]
		for r in res[1]:
			if inpolygon.is_depo_bor (float(r[d.index('y')]),  float(r[d.index('x')])):	continue
			code = r[d.index('code')]
			if not code in codes:	codes.append(code)
			with mutex_directory:
				cdct = GLOB_DIRECTORY.get(code)
				if cdct:	# фиксировать текущие изменения
					if cdct['t'] > r[d.index('t')]:		continue
					if not cdct.get('gosnum'):	cdct['gosnum'] = r[d.index('gosnum')]
					cdct['r'].insert(0, [float(r[d.index('y')]),  float(r[d.index('x')])])
					if len (cdct['r']) > 10:	cdct['r'].pop(-1)
					cdct['t'] = r[d.index('t')]
					cdct['cr5'] = int((2.5 +r[d.index('cr')])/5)*5
					cdct['sp'] = r[d.index('sp')]
				else:
					gosnum = r[d.index('gosnum')]
					if 'bname' in d:
						bname = str(r[d.index('bname')])
					else:	bname = '???'
					GLOB_DIRECTORY[code] = {'r': [[float(r[d.index('y')]),  float(r[d.index('x')])]], 'gosnum': gosnum, 'bname': bname, 't': r[d.index('t')], 'sp': r[d.index('sp')] }

			if 'id_dp' in d:
				if last_id < r[d.index('id_dp')]:	last_id = r[d.index('id_dp')]

		tm = int(time.time())
		jtm = tm % MAX_DTM
		with mitex_dtmcodes:
			DTM_CODES[jtm] = codes
#		print "len(codes):", len(codes), jtm, time.strftime("\t%T", time.localtime(tm))
		time.sleep(1)
		'''
		print "%4d" % j, len(res[1]) 
		if j > 3600:	break
		j += 1
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
	if sp:	return	"<span class='fligt sz12'> v:<b>%s</b>км/ч" % sp
	return 	"<span class='bferr sz12'>Стоит</span>"

def	get_poss (tm, tm_old):
	global	GLOB_DIRECTORY, DTM_CODES, MAX_DTM
#	print 'DTM_CODES', DTM_CODES
	if (tm-tm_old) > 1:
		print	"\t", tm, "\t(tm-tm_old)", (tm-tm_old)
	jtm = tm % MAX_DTM
	if not DTM_CODES[jtm]:	return

	list_data = []
#	with mitex_dtmcodes:
	codes = DTM_CODES[jtm]
	if tm != codes[0]:	#DTM_CODES[jtm][0]:
	#	time.sleep(0.04)
	#	codes = DTM_CODES[jtm]
	#	if tm != codes[0]:
		with mitex_dtmcodes:
			DTM_CODES[jtm] = None
#			print "ERR tm:", tm, jtm, codes
			return
	for jcode in codes[1:]:	#DTM_CODES[jtm][1:]:
	#	dcode = GLOB_DIRECTORY.get(jcode)
		dcode = None
		with mutex_directory:
			dcode = GLOB_DIRECTORY[jcode].copy()
		if dcode:
			dcode['code'] = jcode
			t = dcode.get('t')
			if dcode.has_key('rn'):
				dcode['rnum'] = dcode.get('rn')
				if dcode.get('rem'):
					dcode['opts'] = "%s %s<br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (t)), str_speed(dcode['sp']), dcode.get('rem'))
				#	dcode['ex'] = 'actual'
				#	if dcode.has_key('ex'):		del dcode['ex']
				else:
					dcode['opts'] = "%s %s<br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (t)), str_speed(dcode['sp']), dcode['bname'])	#'МУП "Борское ПАП"')
					dcode['ex'] = 'default'
			else:	dcode['opts'] = "%s %s<br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (t)), str_speed(dcode['sp']), dcode['bname'])
			list_data.append(dcode)
		else:
			print "NOT jcode:", jcode, dcode
#	print "\tget_poss:", len(list_data), jtm, time.strftime("\t%T", time.localtime (tm))
	return	list_data

def	get_all_poss (tm, request):
	""" Подгоро	"""
	global  GLOB_DIRECTORY, INN_CODES
	sinn = request.get('org_inn')
	if sinn and sinn.isdigit() and int(sinn) > 1000000000:
		inn = int(sinn)
		if not inn in INN_CODES.keys():		return
	else:	inn = None

	list_data = []
	for jcode in GLOB_DIRECTORY.keys():
		if inn and not jcode in INN_CODES[inn]:	continue
		dcode = None
		with mutex_directory:
			dcode = GLOB_DIRECTORY[jcode].copy()
	#	dcode = GLOB_DIRECTORY.get(jcode)
		if dcode:
			dcode['code'] = jcode
			dcode['rnum'] = dcode.get('rn')
			t = dcode.get('t')
			if dcode.get('rem'):
				dcode['opts'] = "%s %s<br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (t)), str_speed(dcode['sp']), dcode.get('rem'))
			else:	dcode['opts'] = "%s %s<br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (t)), str_speed(dcode['sp']), dcode['bname'])
			if (tm - dcode['t']) > 3600:	dcode['style'] = "color: #77a"
			list_data.append(dcode)
		else:
			print "NOT jcode:", jcode, dcode
	return	list_data


def parse_sform (sdate = ''):	# 'TEST=atp&view_gosnum=off&view_trace=off&view_routes=off&cod_region=&org_inn=0&bm_ssys=2&snow_stat=&snow_flag=&leaflet-base-layers=on'):
	res = {}
	for sopt in sdate.split('&'):
		try:
			k, v = sopt.split('=', 1)
			if v:	res[k] = v
		except:	pass
	return	res 

'''
def get_vlast_pos (tm, bm_ssys = 2):
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	if bm_ssys:
		res = dbi.get_table('vlast_pos', 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s = %s) AND t >= %s' % (bm_ssys, bm_ssys, tm))
	else:	res = dbi.get_table('vlast_pos', 'tinn >0 AND t >= %s' % tm)
	if not res:	return
	print "get_vlast_pos" 
#	print  res
	d = res[0]
	list_data = []
	for r in res[1]:
		if r[d.index('gosnum')]:
			gosnum = r[d.index('gosnum')]
		else:	gosnum = r[d.index('nm')]
		list_data.append ({'code': r[d.index('code')], 'r': [float(r[d.index('y')]),  float(r[d.index('x')])], 'gosnum': gosnum})	#'%s' % r[d.index('gosnum')]})
	return	list_data
'''

HOST = '212.193.103.21'	#'10.10.2.241'
PORT = 9999

def unpack_frame (data):
	""" Эта функция возвращает словарь типа: {'opcode':1, 'length':15, 'fin':1, 'masked':1, 'payload': 'WebSocket rocks' }
	И для обращения к самому сообщению надо просто будет обращаться к data['payload']
	"""
	frame = {}
	byte1, byte2 = struct.unpack_from('!BB', data)
	frame['fin'] = (byte1 >> 7) & 1
	frame['opcode'] = byte1 & 0xf
	masked = (byte2 >> 7) & 1
	frame['masked'] = masked
	mask_offset = 4 if masked else 0
	payload_hint = byte2 & 0x7f
	if payload_hint < 126:
		payload_offset = 2
		payload_length = payload_hint
	elif payload_hint == 126:
		payload_offset = 4
		payload_length = struct.unpack_from('!H',data,2)[0]
	elif payload_hint == 127:
		payload_offset = 8
		payload_length = struct.unpack_from('!Q',data,2)[0]
	frame['length'] = payload_length
	payload = array.array('B')
	payload.fromstring(data[payload_offset + mask_offset:])
	if masked:
		mask_bytes = struct.unpack_from('!BBBB',data,payload_offset)
		for i in range(len(payload)):
			payload[i] ^= mask_bytes[i % 4]
	frame['payload'] = payload.tostring()
	return frame

def pack_frame (buf, opcode, base64=False):
		 
	if base64:	buf = b64encode(buf)
		 
	b1 = 0x80 | (opcode & 0x0f)	# FIN + opcode
	payload_len = len(buf)
	if payload_len <= 125:
		header = struct.pack('>BB', b1, payload_len)
	elif payload_len > 125 and payload_len < 65536:
		header = struct.pack('>BBH', b1, 126, payload_len)
	elif payload_len >= 65536:
		header = struct.pack('>BBQ', b1, 127, payload_len)
	'''
	fout = open (r'/tmp/pack_frame', 'a+')
	fout.write(header)
	fout.close()
#	print	"payload_len", payload_len, "header", header
	'''
	return header+buf

def create_handshake (handshake):
	"""Подробная информация о Sec-WebSocket-Key
	Для Sec-WebSocket-Accept: x3JJHMbDL1EzLkh9GBhXDw == 258EAFA5-E914-47DA-95CA-C5AB0DC85B11, хэшированние SHA-1,
		дает значение x1d29ab734b0c9585240069a6e4e3e91b61da1969 в шестнадцатеричном формате. 
	Кодирование хэша SHA-1 с помощью Base64 дает HSmrc0sMlYUkAGmm5OPpG2HaGWk =, 
		которое является значением Sec-WebSocket-Accept
	"""
	try:
		lines = handshake.splitlines()	# Делим построчно
		for line in lines:		# Итерируемся по строкам
			parts = line.partition(": ")	# Делим по ':'
		#	print parts
			if parts[0] == "Sec-WebSocket-Key":
				key = parts[2]	# Находим необходимый ключ
		key += "258EAFA5-E914-47DA-95CA-C5AB0DC85B11" 
	#	print key
		Acckey=b64encode((sha1(key)).digest())
		return ("\r\n".join ([
			"HTTP/1.1 101 Switching Protocols",
			"Upgrade: websocket",
			"Connection: Upgrade",
			"Sec-WebSocket-Accept: %s" % Acckey, "\r\n"]))
	except:
		print "except: create_handshake", handshake
		return	1002

def handle (s, addr):
	""" И будем в функции handle получать сообщение открывать его, закрывать и посылать обратно	"""
	try:
		data = s.recv(1024)
#		print data
		ans = create_handshake(data)
		if type(ans) == int:
			s.send(pack_frame("%s\r\n" % ans, 0x8))
			return
		s.send(ans)	#create_handshake(data))
		intm = int(time.time())
		tm_old = intm -1	#MAX_DTM
		request = None
		while True:
			s.settimeout(15)
			data = s.recv(1024)
			if not data:	break
			unpdata = unpack_frame (data)
		#	print "unpdata", unpdata, time.strftime("\t%T", time.localtime (time.time ()))
			if unpdata['opcode'] == 0x8:	break
			if request == None:
				request = parse_sform (unpdata['payload'])
				print '\trequest', request
				'''
				ddata = get_all_poss (intm, request)
				print "get_all_poss\t", len(ddata), time.strftime("\t%T", time.localtime (time.time ()))
				if ddata:	s.send(pack_frame("~eval| get_listTS(%s)" % json.dumps(ddata), 0x1))
				'''
				ald = pack_frame("~eval| get_listTS(%s)" % json.dumps (get_all_poss (intm, request)), 0x1)
				print "get_all_poss\t", len(ald), time.strftime("\t%T", time.localtime (time.time ()))
				sendln = 0
				while sendln < len(ald):
					sln = s.send (ald[sendln:])
					if sln == 0:	raise RuntimeError("socket connection broken")
					sendln += sln

		#	ddata = get_vlast_pos (intm -5)
			ddata = None
			for jt in xrange((intm-tm_old), 0, -1):
				ddata = get_poss (intm-jt, tm_old)
				if ddata:
					ddd = pack_frame("~eval| get_listTS(%s)" % json.dumps(ddata), 0x1)
					sendln = 0
					while sendln < len(ddd):
						sln = s.send (ddd[sendln:])
						if sln == 0:	raise RuntimeError("socket connection broken")
						sendln += sln
		
			if not ddata:	time.sleep(1)
			tm_old = intm
			time.sleep(1)
			intm = int(time.time())
			if s.send (pack_frame('PING',0x9)) == 0:	break
			if exit_request:	break
	except:	pexcept ('handle')
	finally:
		s.close()
		print 'Close', addr

def start_server ():
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#	s.bind(('', 9999))
	s.bind((HOST, PORT))
	s.listen(1)
	while 1:
		conn, addr = s.accept()
		print 'Connected by', addr, time.strftime("\t%d.%m.%Y %T", time.localtime (time.time ()))
		threading.Thread(target = handle, args = (conn, addr)).start()

HEADS = """
Accept: text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip, deflate
Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3
Cache-Control: no-cache
Connection: keep-alive, Upgrade
Host: 212.193.103.20:9999
Origin: http://212.193.103.21
Pragma: no-cache
Sec-WebSocket-Extensions: permessage-deflate
Sec-WebSocket-Key: BN1cjfSLyFjHesK9xe5AAQ==
Sec-WebSocket-Version: 13
Upgrade: websocket
User-Agent: Mozilla/5.0 (X11; Linux x86_64…) Gecko/20100101 Firefox/60.0
"""
def	pexcept (mark = None, exit = False):
	exc_type, exc_value = sys.exc_info()[:2]
	print "EXCEPT %s:\t" % mark, exc_type, exc_value
	if exit:	os._exit(exit)

def	test():
	print "TEST"
	actual_nimbus ()

mutex_exit =  threading.Lock()
exit_request =	False

if __name__ == "__main__": 
	'''
	test ()
	actual_directory ()
	print HEADS
	print create_handshake (HEADS)
	'''
	try:
		threading.Thread(target = actual_directory, args = ()).start()
		time.sleep(2)
		threading.Thread(target = actual_nimbus, args = ()).start()
		start_server()
	except	KeyboardInterrupt:
		mutex_exit.acquire()
		exit_request = True
		mutex_exit.release()
	#	pass
	except:	pexcept('MAIN')

