#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import  time
import  urllib
import  urlparse

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"	# Путь к рабочей директории (библиотеке)
CONF_PATHNAME = r"/home/smirnov/MyTests/CGI/sys.ini"
sys.path.insert(0, LIBRARY_DIR)
request = {}
import	cglob
import	main_page

import	json

def     check ():
	try:
		request = cglob.get_theform ()
		
		CPYSESSID = ''
		# 'this': 'ajax', 'shstat': 'view_canvas'
		if os.environ.has_key('HTTP_REFERER') and os.environ['REQUEST_METHOD'] == 'POST':
			print '\n'
			referer = os.environ['HTTP_REFERER']
			shstat = request.get('shstat')
			import	recv_tools as rt
			print time.strftime("~last_time|%T", time.localtime(time.time()))

	#		if 'temp.html' in referer:	print "~eval| msg('shstat: %s')" % shstat
			if shstat == 'GET':
		#		print "~eval| msg('GET')"
				get_inn = request.get('get_inn').strip()
				if get_inn and get_inn.isdigit():
						rt.set_place(get_inn)
						print "~eval|document.myForm.org_inn.value=%s; $('#widget').html(''); set_shadow ('get_tansport');" % get_inn
				sys.exit()

			if shstat == 'submit':
				if '?' in referer:
					print "~eval|window.location.reload(true);"	# //window.open('%s')" % (referer, referer)
				else:	print "~eval|window.location.reload(false);"
			#	print referer
				sys.exit()

			if shstat == 'get_tansport':
				ts_list = rt.get_ts(request)
				if ts_list:
					print "~eval|out_data('%s');" % json.dumps(ts_list)
				else:	print "~eval|document.myForm.org_inn.value=0; alert('У организации ИНН: %s \\nНет АКТИВНЫХ транспортных средств!');" % request.get('org_inn')
			elif shstat == 'view_canvas':
				ts_list = rt.get_ts(request)
				if ts_list:
					print "~eval|out_data('%s');" % json.dumps(ts_list)
			#	else:	print "~eval|alert('У организации ИНН: %s \\nНет транспортных средств!');" % request.get('org_inn')
			elif shstat == 'set_region':
				rt.set_region(request)
			elif shstat == 'view_ts_list':
				ress = rt.view_ts_list(request)
				print '~widget|', ress
			elif shstat == 'view_ts_config':
				ress = rt.view_ts_config(request)
				print '~widget|', ress
			elif shstat == 'view_gosnum':
		#		print request
		#		if os.path.split(os.environ['HTTP_REFERER'])[-1] == 'temp.html':
					isview = request.get('view_gosnum')
					if not isview or isview != 'on':
						print "~eval|view_gosnumber(1);"
					else:	print "~eval|view_gosnumber(2);"
			elif shstat == 'view_gzones':
				ress = rt.view_gzones (request)
				print '~widget|', ress
			elif shstat == 'set_organizations':
				ress = rt.set_organizations (request)
				print '~widget|', ress
			elif shstat == 'update_ts_list':	# temp.html Get TS Обновление списка ТС
				print '~log|'	#, request
				rt.update_ts_list (request)
			elif shstat == 'update_recv_ts':
				print '~log|'
				rt.update_recv_ts(request)
			elif shstat == 'check_autos':
				print '~log|'
				print '~widget|', rt.check_autos (request)
			elif shstat == 'view_trace':		# in ['view_trace', 'set_opts']:
				print '~log|', request
				rt.view_trace (request)
			elif shstat == 'set_opts':
				print '~log|', request
				print "ZZZ"
				rt.view_streets(request)
			elif 'snow_' in shstat:
				print '~log|Snow: ', request
				rt.snow_opts (request)
			else:
				print '~log|shstat:', shstat, request
				print '<br>HTTP_REFERER:', referer , os.path.split(referer)[-1]
			'''
			if request.has_key('this'):
				if request['this'] == 'ajax':
					import  ajax
					ajax.main(os.environ['SCRIPT_NAME'], request, referer)
				sys.exit()
			elif os.environ.has_key('HTTP_COOKIE') and ('CPYSESSID' in os.environ['HTTP_COOKIE']):
				request['disp'] = '123'
				request['message'] = ""
			else:	pass
			'''
			sys.exit()
		else:	print '\n\n', request, os.environ['REQUEST_METHOD']
		'''
		elif request.has_key('this') and request['this'] == 'new_widow':
			print """Content-Type: text/html; charset=utf-8\n\n<!DOCTYPE HTML>\n<html>"""
	#		cglob.ppobj(dict(os.environ))
			conf = cglob.get_config(CONF_PATHNAME)
			main_page.new_widow  (request, conf)
			sys.exit()
		else:
		#	print """Content-Type: text/html; charset=utf-8\n\n<!DOCTYPE HTML>"""
			print """Content-Type: text/html; charset=utf-8\n%s\n\n<!DOCTYPE HTML>""" % CPYSESSID
			print '<html><pre>'
			print 'CPYSESSID', CPYSESSID
			for k in os.environ.keys():	print k, '=\t', os.environ
			print '<pre></html>'
		#	conf = cglob.get_config(CONF_PATHNAME)
		#	main_page.main(request, conf)
		#	print "CPYSESSID:", CPYSESSID
		#	cglob.ppobj(dict(os.environ))
		'''
	except SystemExit:	pass
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "check:", exc_type, exc_value

if __name__ == "__main__":
#	print "Content-Type: text/html; charset=utf-8\n"
#	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n'
#	print '<html>'
	try:
		check ()
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value

