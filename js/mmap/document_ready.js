function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}

	$(document).ready(function () {
	$.ajaxSetup({ url: "/cgi-bin/ajax.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	$('#map').css({'height': -40 + document.documentElement.clientHeight +'px', 'width': '100%'});		// на Карте
//	$('#map').css({'height': (-100 + document.documentElement.clientHeight) +'px', 'width': '100%'});	// <div id='log' ... /div> под картой
//	set_shadow('get_transport');
	start_ws();

//var timerId = setInterval(set_shadow, 20000, 'view_canvas');

	mymap = L.map('map').setView([56.32354, 43.99121], 12);

var	rnic_nn = ' &copy; <a href="http://rnc52.ru/" title="РНИЦ Нижегородской области">RNIC 52</s>';
var	osmLayer = new L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	maxZoom: 18,
	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors |' + rnic_nn
	}).addTo(mymap);
/*
var	marker = L.marker([56.32354, 43.99121]).addTo(mymap)
	.bindPopup('A pretty CSS3 popup.<br> и текст по Русски.')
	.openPopup();
*/
var	roadsLayer = new L.tileLayer('http://212.193.103.5/{alias}/{z}/{x}/{y}.png', {maxZoom: 18, attribution: rnic_nn, alias: 'enk2'});
//var	yndx = new L.Yandex();
//var	ytraffic = new L.Yandex("null", {traffic:true, opacity:0.8, overlay:true});
//var	baseMaps = { "OpenStreetMap": osmLayer, 'Дороги Нижнего Новгорода': roadsLayer, 'L.Yandex': yndx },
var	baseMaps = { "OpenStreetMap": osmLayer, 'Дороги Нижнего Новгорода': roadsLayer },
	overlays = { };	//"Marker": marker};

var	layersControl = new L.Control.Layers(baseMaps, overlays),	// overlayMaps),
	popup = new L.Popup();
/*
var geojsonFeature = { "type": "FeatureCollection",
    "features": [
      { "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [52.0, 55.5]},
        "properties": {"prop0": "value0"}
        },
      { "type": "Feature",
        "geometry": {
          "type": "LineString",
          "coordinates": [
            [52.0, 55.0], [53.0, 56.0], [54.0, 55.0], [55.0, 56.0]
            ]
          },
        "properties": {
          "prop0": "value0",
          "prop1": 0.0
          }
        },
      { "type": "Feature",
         "geometry": {
           "type": "Polygon",
           "coordinates": [
             [ [43.0, 55.0], [43.8663098413745,56.3519299270262],[43.8662400424986,56.3518808173214], [51.0, 55.0], [51.0, 56.0],
               [50.0, 56.0], [43.0, 55.0] ],
	     [
		[43.8663098413745,56.3519299270262],[43.8662400424986,56.3518808173214],
		[43.8663098413745,56.3519299270262]
		]
             ]
         },
         "properties": {
           "prop0": "value0",
           "prop1": {"this": "that"}
           }
         }
       ]
     }
var	geoLayer = L.geoJSON(geojsonFeature).addTo(mymap);
//var	geoLayer = L.geoJSON().addTo(mymap);
*/
mymap.addControl(layersControl);
mymap.on('click', (e) => {
    popup.setLatLng(e.latlng);
    popup.setContent('Point ' +
      ' (' + e.latlng.lat.toFixed(6) +
      ', ' + e.latlng.lng.toFixed(6) + ')');
    mymap.openPopup(popup);
  })

if (window.location.search) {	set_shadow('GET&get_'+ window.location.search.replace('?', ''))	}
});
