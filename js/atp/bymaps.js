/*
var intervalID = null;
function	reload_ts () {
	return
	if (intervalID == null) {
		intervalID = setInterval(set_shadow, 20000, 'get_transport'); // Обновление ТС
	//	$('#updating_ts').html('<span class="fa-stack" title="Запретить Обновление"> <i class="fa fa-refresh fa-lg" aria-hidden="true"></i> <i class="fa fa-times fa-stack-2x text-danger"></i></span>')
		$('#updating_ts').html('<i class="fa fa-refresh fa-lg" aria-hidden="true" title="Запретить Обновление"></i> <i class="fa fa-times fa-stack-2x text-danger" title="Запретить Обновление"></i>')
	} else {
		clearInterval(intervalID);
		intervalID = null;
		$('#updating_ts').html('<i class="fa fa-refresh fa-lg" aria-hidden="true" title="Обновлять данные"></i>');	// Обновление');
	}
}
*/
var	dict_gosnumber = [];	// Гос№
var	dict_ts_list = [];	// Транспорт
var	list_regionn = [];	// районы города
var	list_tracks = [];	// Треки машин
var	list_streets = [];	// Улицы
var	list_routes = [];	// Маршруты Автобусов NimBus
var	user_position = null;

function	clear_map_object (obj) {
	for (k in obj) {
		if (obj.hasOwnProperty(k))	obj[k].remove();
		delete(obj[k])
	}
}

function	out_data (data) {
//	clear_ts_list ();
	clear_map_object (dict_ts_list);
	clear_map_object (dict_gosnumber);
	var LeafIcon = L.Icon.extend({options: {iconAnchor: [12,12], popupAnchor: [0, -15]}});	//, shadowAnchor: [16,37], shadowUrl: '/img/marker-shadow.png', shadowSize: [51, 37]}});
	var tsIcons = {};
	tsIcons['blue'] = new LeafIcon({iconUrl: '/img/circle-blu.svg'});
	tsIcons['green'] = new LeafIcon({iconUrl: '/img/circle-grn.svg'});
	tsIcons['grey'] = new LeafIcon({iconUrl: '/img/circle-gry.svg'});
	tsIcons['red'] = new LeafIcon({iconUrl: '/img/circle-red.svg'});
//	alert (data);
	var plist = eval(data);	//'[["44.054517", "56.366", "1520845490", "Привет QWER"], [ "44.068579", "56.372314", "1520846572", "В132ХА152" ]]');	//data);
	for (var i=0; i<=plist.length-1; i++) {
//		alert (plist[i])
		var YX = plist[i][0];
		var opts = plist[i][1]
		if (opts['icon'] && tsIcons.hasOwnProperty(opts['icon'])) {
			var jIcon = tsIcons[opts['icon']];
		} else	var jIcon = tsIcons['red'];
		if (document.getElementById('view_gosnum'))
			dict_ts_list[i] = L.marker(YX, {icon: jIcon}).addTo(mymap).bindPopup(opts['gosnum'] + opts['sp'] +'<br>' +opts['bn'] +opts['dt']);
		else	dict_ts_list[i] = L.marker(YX, {icon: jIcon}).addTo(mymap).bindTooltip(opts['gosnum']).bindPopup(opts['gosnum'] + opts['sp'] +'<br>' +opts['bn'] +opts['dt']);
		dict_gosnumber[i] = L.marker(YX, {icon: L.divIcon({className: 'icon', html: opts['bn']})});	//.addTo(mymap);
		if (document.myForm.view_gosnum.value == 'on')	dict_gosnumber[i].addTo(mymap);
	}
	if (document.myForm.view_trace.value == 'on')	set_shadow ('view_trace&set=on');
}

function view_gosnumber(j) {
	if (document.myForm.view_gosnum.value == 'off')
		document.myForm.view_gosnum.value='on';
	else	document.myForm.view_gosnum.value='off';
}

function mmm (txt) {
	var LeafIcon = L.Icon.extend({options: {iconAnchor: [12,24], popupAnchor: [0, -27], shadowAnchor: [16,37], shadowUrl: '/img/marker-shadow.png', shadowSize: [51, 37]}});
	var redIcon = new LeafIcon({iconUrl: '/img/circle-red.svg'})
	var marker = [L.marker([56.3271,44.0074], {icon: redIcon}).addTo(mymap).bindPopup(txt).openPopup(),
	L.marker([56.31271,44.01074], {icon: redIcon}).addTo(mymap).bindPopup('111 txt').openPopup()];
	L.marker([56.3271,44.02074], {icon: redIcon}).addTo(mymap).bindPopup('222 txt').openPopup();
	L.marker([56.33271,44.03074], {icon: redIcon}).addTo(mymap).bindPopup('333 txt');	//.openPopup();
} 
function check_bounds () {
	var bounds = mymap.getBounds();
	var BBB = 'YX: ' + bounds['_northEast'] +', 00: ' + bounds['_southWest'];
//	orthEast: LatLng(56.399655, 44.145813)	- Левый верхний
//	southWest: LatLng(56.247356, 43.836823)	- Првыый нижний
	alert (BBB);
}
