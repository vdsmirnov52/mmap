/**	\file	/js/atp/ws_functions.js
 *	\brief	Обеспечение обмена данными через tWebSocket
 */
//var wsUri = "ws://localhost:9999/"; var output; 
var wsUri = "ws://212.193.103.21:9998/"; var output; 
var websocket = null;

function start_ws () {
	clear_map_object (listTS);
	clear_map_object (list_tracks);
	if (websocket != null)	 websocket.close();

	websocket = new WebSocket(wsUri);
	websocket.onopen = function(evt) { websocket.send ('TEST=mmap&' + $('form').serialize());	}
	websocket.onmessage = function(evt) {
		$('#log').html('');
		var inc_message = evt.data;
		parse_message (inc_message);
	}
	websocket.onerror = function(evt) { $('#log').html('<span style="color: red; font-weight: bold;">WS ERROR:' +evt.data+ '</span>');	}
	websocket.onclose = function(evt) { $('#log').html('<span style="color: red; font-weight: bold;">DISCONNECTED</span>');   }
}
//function close_ws () {	if (websocket != null) { websocket.onclose = function(evt) { $('#log').html('<span style="color: red;">DISCONNECTED</span>');	}}}

function parse_message (data) {
	if  (data == 'submit') {
		document.mainForm.submit ();
	} else {
		var arr = data.split  ('~');
		for  (var j in arr) {
			var vall = arr [j].split  ('|');
			if ('eval' == vall [0]) {
				eval (vall [1]);
			} else if ((vall [0] != '') && (document.getElementById(vall [0]))) {
				document.getElementById(vall [0]).innerHTML = vall [1];
			}
		}
	}
}
//window.addEventListener("load", init, false);

var listTS = {}

function get_listTS (data) {
//	alert (data);
	var plist = eval(data);
//	alert ('plist.length: ' + plist.length);
	for (var i=0; i<=plist.length-1; i++) {
		var gosnum = plist[i]['gosnum'];
		var code = plist[i]['code'];
		var YX = plist[i]['r'][0];
		if (plist[i]['rnum']) 
			if (plist[i]['ex'] || plist[i]['ex'] == 'default')
				var rnum = '<span class="sz12 bferr">№' + plist[i]['rnum'] + '&nbsp;</span>';
			else	var rnum = '№<span class="tit">' + plist[i]['rnum'] + '&nbsp;</span>';
		else	var rnum = '<span class="sz12 bfligt">'+ gosnum +'</span>';
		if (listTS[code])	{	//.hasOwnProperty[code]) {
		//	listTS[code].setPosition(YX);
			listTS[code].remove();
			delete(listTS[code]);
		}
		var str_ppup = "<span class='bfinf'>"+ gosnum +"</span> " +plist[i]['opts'];
		if (document.myForm.view_gosnum.value == 'on')	//	str_html += rnum;	//gosnum;
//			var str_html = '<div class="btn-group bfinf"><span class="fa-stack fa-lg"><i class="fa fa-circle fa-stack-2x"></i><i class="fa fa-bus fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'+ rnum +'</div>';
			var str_html = '<div class="btn-group bfinf"><span class="fa-stack fa-lg"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.6"></i><i class="fa icon-041 fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'+ rnum +'</div>';
		//	var str_html = '<span class="fa-stack fa-lg"><i class="fa fa-circle fa-stack-2x"></i><i class="fa fa-bus fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'+ rnum ;
//		else	var str_html = '<span class="fa-stack fa-lg bfinf"><i class="fa fa-circle fa-stack-2x"></i><i class="fa fa-bus fa-stack-1x fa-inverse" aria-hidden="true"></i></span>';
		else	var str_html = '<span class="fa-stack fa-lg bfinf"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.6"></i><i class="fa icon-041 fa-stack-1x fa-inverse" aria-hidden="true"></i></span>';
		listTS[code] = L.marker(YX, {icon: L.divIcon({className: 'icon', iconAnchor: [14,14], html: str_html})}).addTo(mymap).bindPopup(str_ppup);

		// Показать трек
		if (document.myForm.view_trace.value == 'on') {
			var tr = plist[i]['r'];
			if (list_tracks[code]) {
				list_tracks[code].remove();
				delete (list_tracks[code]);
			}
			list_tracks[code] = new L.Polyline(tr, { color: 'blue', weight: 7, opacity: 0.3 }).addTo(mymap);
		}
	}
}
