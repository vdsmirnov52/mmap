#!/usr/bin/python -u
# -*- coding: utf-8 -*-
""" WebSocket сервер:
	- Готовит данные о движении ТС для подстстемы АнтиСнег
	- Отправляет на http://212.193.103.21/tmp/mmap.html

	nohup /home/smirnov/MyTests/WS/ws_receiver.py > /home/smirnov/MyTests/log/ws_receiver.log  &
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

mutex_directory = threading.Lock()      # .acquire() .release() with mutex_
mitex_dtmcodes = threading.Lock()
mitex_inncodes = threading.Lock()

GLOB_DIRECTORY = {}		# Kei = Unut ID (code)  - ID Машины
MAX_DTM =	60
DTM_CODES =	[]
for j in xrange(MAX_DTM):	DTM_CODES.append(None)

INN_CODES =	{}
IDS_bm_ssys =	0

def	actual_directory ():
	print	"actual_directory"
	global	GLOB_DIRECTORY, DTM_CODES, MAX_DTM
	global	INN_CODES, IDS_bm_ssys

	dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	last_id = 0
	bm_ssys = 2
	j = 0
	while not exit_request:
		if IDS_bm_ssys == 0:
			time.sleep(11)
			continue
		if last_id == 0:
			swhere = 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s > 0) LIMIT 100' % IDS_bm_ssys
		else:	swhere = 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s > 0) AND id_lp > %s' % (IDS_bm_ssys, last_id)
	#	print	'\tswhere:', swhere
		res = dbi.get_table('vlast_pos', swhere)
		tm = int(time.time())
		jtm = tm % MAX_DTM
		if not res:
			with mitex_dtmcodes:
				DTM_CODES[jtm] = None
			continue
		codes = [tm]
		d = res[0]
		for r in res[1]:
			code = r[d.index('code')]
			if not code in codes:	codes.append(code)
			with mutex_directory:
				cdct = GLOB_DIRECTORY.get(code)
				if cdct:
				#	if not cdct.get('gosnum'):	gosnum = r[d.index('gosnum')]
				#	cdct['r'] = [float(r[d.index('y')]),  float(r[d.index('x')])]	#, r[d.index('t')]]
					cdct['r'].insert(0, [float(r[d.index('y')]),  float(r[d.index('x')])])
					if len (cdct['r']) > 10:	cdct['r'].pop(-1)
					cdct['t'] = r[d.index('t')]
					cdct['sp'] = r[d.index('sp')]
				else:
					gosnum = r[d.index('gosnum')]
					if r[d.index('marka')]:
						rem = "%s<br>%s" % (r[d.index('marka')], r[d.index('bname')])
					else:	rem = "%s" % r[d.index('bname')]
				#	GLOB_DIRECTORY[code] = {'r': [float(r[d.index('y')]),  float(r[d.index('x')])], 'gosnum': gosnum, 't': r[d.index('t')], 'sp': r[d.index('sp')], 'rem': rem }
					GLOB_DIRECTORY[code] = {'r': [[float(r[d.index('y')]),  float(r[d.index('x')])]], 'gosnum': gosnum, 't': r[d.index('t')], 'sp': r[d.index('sp')], 'rem': rem }

			if INN_CODES.has_key(r[d.index('tinn')]):
				if not code in INN_CODES[r[d.index('tinn')]]:
					with mitex_inncodes:
						INN_CODES[r[d.index('tinn')]].append (code)
			else:
				with mitex_inncodes:
					INN_CODES[r[d.index('tinn')]] = [code]

		with mitex_dtmcodes:
			DTM_CODES[jtm] = codes
		last_id = r[d.index('id_lp')]
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

def	get_poss (tm, tm_old, request):
	global	GLOB_DIRECTORY, DTM_CODES, MAX_DTM
	global	INN_CODES, IDS_bm_ssys
#	print 'DTM_CODES', DTM_CODES
	if (tm-tm_old) > 1:
		print	"\t", tm, "\t(tm-tm_old)", (tm-tm_old)
	jtm = tm % MAX_DTM
	if not DTM_CODES[jtm]:	return
	sinn = request.get('org_inn')
	if sinn.isdigit() and int(sinn) > 1000000000:
		inn = int(sinn)
		if not inn in INN_CODES.keys():		return
	else:	inn = None
#	inn = 5263133747	# 5250039673	5259120142

	list_data = []
#	with mitex_dtmcodes:
	codes = DTM_CODES[jtm]
	if tm != codes[0]:	#DTM_CODES[jtm][0]:
		time.sleep(0.04)
		codes = DTM_CODES[jtm]
		if tm != codes[0]:
			print "ERR tm:", tm, jtm, codes
			return
	for jcode in codes[1:]:	#DTM_CODES[jtm][1:]:
		if inn and not jcode in INN_CODES[inn]:	continue
		dcode = None
		with mutex_directory:
			dcode = GLOB_DIRECTORY[jcode].copy()
	#	dcode = GLOB_DIRECTORY.get(jcode)
		if dcode:
			dcode['code'] = jcode
		#	dcode['opts'] = "<br>%s %s" % (str_time(dcode['t']), str_speed(dcode['sp']))
		#	dcode['opts'] = "%s %s" % (str_speed(dcode['sp']), str_time(dcode['t']))
			if dcode.has_key('rn'):
				dcode['rnum'] = dcode.get('rn')
				if dcode.get('rem'):
					dcode['opts'] = "%s %s<br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (tm)), str_speed(dcode['sp']), dcode.get('rem'))
				else:
					dcode['opts'] = "%s %s<br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (tm)), str_speed(dcode['sp']), 'МУП "Борское ПАП"')
					dcode['ex'] = 'default'
			else:	dcode['opts'] = "%s %s <br>%s" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (tm)), str_speed(dcode['sp']), dcode.get('rem'))
		#	dcode['gosnum'] = "<span class='bfinf'> %s </span>" % dcode['gosnum']
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

HOST = '212.193.103.21'	#'10.10.2.241'
PORT = 9998

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
	global	INN_CODES, IDS_bm_ssys
	try:
		data = s.recv(1024)
#		print data
		ans = create_handshake(data)
		if type(ans) == int:
			s.send(pack_frame("%s\r\n" % ans, 0x8))
			return
		s.send(ans)	#create_handshake(data))
		tm_old = intm = int(time.time())
		request = None
		while True:
			data = s.recv(1024)
			if not data:	break
		#	for c in data:	print ord(c),
		#	print "data"
			unpdata = unpack_frame (data)
		#	print "unpdata", unpdata, time.strftime("\t%T", time.localtime (time.time ()))
			if unpdata['opcode'] == 0x8:	break
			if request == None:
				request = parse_sform (unpdata['payload'])
				print '\trequest', request
				jbm_ssys = request.get('bm_ssys')
				if jbm_ssys and jbm_ssys.isdigit():	IDS_bm_ssys |= int(jbm_ssys)
 
			if (intm-tm_old) > 1:
				ddata = get_poss (intm-1, tm_old, request)
				if ddata:
					pdata = pack_frame("~eval| get_listTS(%s)" % json.dumps(ddata), 0x1)
					dataln = len(pdata)
					sendln = 0
					while sendln < dataln:
						sln = s.send (pdata[sendln:])
						if sln == 0:	raise RuntimeError("socket connection broken")
						sendln += sln
			ddata = get_poss (intm, tm_old, request)
			if ddata:
					pdata = pack_frame("~eval| get_listTS(%s)" % json.dumps(ddata), 0x1)
					dataln = len(pdata)
					sendln = 0
					while sendln < dataln:
						sln = s.send (pdata[sendln:])
						if sln == 0:	raise RuntimeError("socket connection broken")
						sendln += sln
			tm_old = intm
			intm = int(time.time())
			time.sleep(1)
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
		print 'Connected by', addr
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
		start_server()
	except	KeyboardInterrupt:
		mutex_exit.acquire()
		exit_request = True
		mutex_exit.release()
	#	pass
	except:	pexcept('MAIN')

