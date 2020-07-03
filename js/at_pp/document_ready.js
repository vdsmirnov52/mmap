function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}

	$(document).ready(function () {
	$.ajaxSetup({ url: "/cgi-bin/ajax.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	$('#map').css({'height': document.documentElement.clientHeight +'px', 'width': '100%'});
//	set_shadow('get_transport');
	start_ws ();
	var ws_interval = setInterval(check_ws, 20000);


	var pos = [56.32354, 43.99121], mlv = 11;
	
	/* Достать список парамертов из URL ( pos=[56.357907,44.055898] - геопозиция пользователя )*/
	var purl = location.search.slice(1).split("&");	//[0].split("="));
	if (purl) {
		for (var j = 0; j < purl.length; j++) {
			var p = purl[j].split("=");
			if (p[0] == "pos") {
				if (p[1] == "BOR")
					pos = [56.357907,44.062008];
				else	pos = JSON.parse(p[1]);	//eval(p[1]);
				mlv = 14;
				break
			}
		}
	}
	mymap = L.map('map').setView(pos, 13);	//[56.32354, 43.99121], 12);

///	mymap = L.map('map').setView([56.32354, 43.99121], 14);

var	rnic_nn = '';	// &copy; <a href="http://rnc52.ru/" title="РНИЦ Нижегородской области">RNIC 52</s>';
var	osmLayer = new L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	maxZoom: 18,
	attribution: ''	// &copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors |' + rnic_nn
	}).addTo(mymap);
/*
var	marker = L.marker([56.32354, 43.99121]).addTo(mymap)
	.bindPopup('A pretty CSS3 popup.<br> и текст по Русски.')
	.openPopup();
*/
var	roadsLayer = new L.tileLayer('http://212.193.103.5/{alias}/{z}/{x}/{y}.png', {maxZoom: 18, attribution: rnic_nn, alias: 'enk2'});
var	locLayer = new L.tileLayer('http://10.10.2.241/{alias}/{z}/{x}/{y}.png', {maxZoom: 18, attribution: rnic_nn, alias: 'tiles'});
var	yndx = new L.Yandex();
var	ytraffic = new L.Yandex("null", {traffic:true, opacity:0.8, overlay:true});
//var	baseMaps = { "OpenStreetMap": osmLayer, 'L.Yandex': yndx };
var	baseMaps = { "L.Yandex": yndx, "OpenStreetMap": osmLayer,
	'212.193.103.5 roadsLayer': roadsLayer,
	'10.10.2.241 locLayer': locLayer,
	};
var	overlays = { };	//"Marker": marker};

var	layersControl = new L.Control.Layers(baseMaps, overlays),	// overlayMaps),
	popup = new L.Popup();

mymap.addControl(layersControl);
/*
*/
mymap.on('click', (e) => {
	popup.setLatLng(e.latlng);
	popup.setContent('('+ e.latlng.lng.toFixed(6) +','+ e.latlng.lat.toFixed(6) +')')
//	popup.setContent('Point ' + ' (' + e.latlng.lat.toFixed(6) + ', ' + e.latlng.lng.toFixed(6) + ')');
	mymap.openPopup(popup);
  })
if (window.location.search) {	set_shadow('GET&get_'+ window.location.search.replace('?', ''))	}
});
