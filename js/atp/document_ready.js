function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}

	$(document).ready(function () {
	$.ajaxSetup({ url: "/cgi-bin/ajax.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	$('#map').css({'height': document.documentElement.clientHeight +'px', 'width': '100%'});
//	set_shadow('get_transport');
	start_ws ();

//var timerId = setInterval(set_shadow, 20000, 'view_canvas');

	mymap = L.map('map').setView([56.32354, 43.99121], 14);

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
var	yndx = new L.Yandex();
var	ytraffic = new L.Yandex("null", {traffic:true, opacity:0.8, overlay:true});
var	baseMaps = { "OpenStreetMap": osmLayer, 'L.Yandex': yndx };
//var	baseMaps = { "OpenStreetMap": osmLayer, 'Дороги Нижнего Новгорода': roadsLayer };
var	overlays = { };	//"Marker": marker};

var	layersControl = new L.Control.Layers(baseMaps, overlays),	// overlayMaps),
	popup = new L.Popup();

mymap.addControl(layersControl);
/*
mymap.on('click', (e) => {
    popup.setLatLng(e.latlng);
    popup.setContent('Point ' +
      ' (' + e.latlng.lat.toFixed(6) +
      ', ' + e.latlng.lng.toFixed(6) + ')');
    mymap.openPopup(popup);
  })
*/
if (window.location.search) {	set_shadow('GET&get_'+ window.location.search.replace('?', ''))	}
});
