/**	\file	/js/atp/ws_functions.js
 *	\brief	Обеспечение обмена данными через WebSocket
 */
//var wsUri = "ws://localhost:9999/"; var output; 
var wsUri = "ws://212.193.103.21:9996/"; var output; 
var websocket = null;

function start_ws () {
	clear_map_object (listTS);
	clear_map_object (list_tracks);
	if (websocket != null)	 websocket.close();

	websocket = new WebSocket(wsUri);
	websocket.onopen = function(evt) { websocket.send ('TEST=atp&' + $('form').serialize());	}
	websocket.onmessage = function(evt) {
		$('#log').html('');
		var inc_message = evt.data;
		parse_message (inc_message);
	}
	websocket.onerror = function(evt) {
		$('#log').html('<span style="color: red; font-weight: bold;">WS ERROR:' +evt.data+ '</span>');
		websocket.close(); 
		websocket = null;
	}
	websocket.onclose = function(evt) { 
		$('#log').html('<span class="line btn btn-info" style="color: red; font-weight: bold;" onclick="start_ws();">CONNECT</span>'); 
		websocket = null;  
	}
}
function check_ws () {
	if (websocket == null) {
		start_ws();
		console.log ('check_ws websocket: ' +websocket);
	}
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
//	fa fa-arrow-left

var listTS = {}

function get_listTS (data) {
//	alert (data);
	var plist = eval(data);
//	alert ('plist.length: ' + plist.length);
//	var LeafIcon = L.Icon.extend({options: {iconAnchor: [12,12], popupAnchor: [0, -15], tooltipAnchor: [5,0]}});
	var tt = L.tooltip({options:{opacity: 0.2}});
	for (var i=0; i<=plist.length-1; i++) {
		var gosnum = plist[i]['gosnum'];
		var code = plist[i]['code'];
		var YX = plist[i]['r'][0];
		if (plist[i]['rnum']) 
			if (plist[i]['ex'] || plist[i]['ex'] == 'default')
				var rnum = '<span class="sz12 bferr">№' + plist[i]['rnum'] + '&nbsp;</span>';
			else	var rnum = '<span class="tit">' + plist[i]['rnum'] + '&nbsp;</span>';
		else	var rnum = '<span class="sz12 bfligt">'+ gosnum +'</span>';
		if (listTS[code])	{	//.hasOwnProperty[code]) {
		//	listTS[code].setPosition(YX);
			listTS[code].remove();
			delete(listTS[code]);
		}
		var str_ppup = "<span class='bfinf'>"+ gosnum +"</span> " +plist[i]['opts'];
		if (plist[i]['cr5'])
			var img = "<img src='/img/kurs/a"+ plist[i]['cr5'] +".png'>"
		else	var img = '<span class="fa-stack fa-lg bfinf"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.7"></i><i class="fa fa-bus fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
		if (document.myForm.view_gosnum.value == 'on')	//	str_html += rnum;	//gosnum;
			var str_html = '<div class="btn-group bfinf">'+ img +' '+ rnum +'</div>';
	//		var str_html = '<div class="btn-group bfinf"><span class="fa-stack fa-lg"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.7"></i><i class="fa fa-bus fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'+ rnum +'</div>';
	//	else	var str_html = '<span class="fa-stack fa-lg bfinf"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.7"></i><i class="fa fa-bus fa-stack-1x fa-inverse" aria-hidden="true"></i></span>';
		else	var str_html = img
		listTS[code] = L.marker(YX, {icon: L.divIcon({className: 'icon', iconAnchor: [2,20], html: str_html})}).addTo(mymap).bindPopup(str_ppup);
/*
		var iIcon = new LeafIcon({iconUrl: "/img/kurs/a"+ plist[i]['cr5'] +".png" });
		if (document.myForm.view_gosnum.value == 'on') {
			listTS[code] = L.marker(YX, {icon: iIcon }).addTo(mymap).bindPopup(str_ppup).bindTooltip(rnum).openTooltip();
		//	dict_gosnumber[i] = L.marker(YX, {icon: L.divIcon({className: 'icon', html: rnum})}).addTo(mymap);
		} else {
			listTS[code] = L.marker(YX, {icon: iIcon, title: gosnum }).addTo(mymap).bindPopup(str_ppup);
		}
*/
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

function view_gosnumber(j) {
	if (document.myForm.view_gosnum.value == 'off')
		document.myForm.view_gosnum.value='on';
	else	document.myForm.view_gosnum.value='off';
}
