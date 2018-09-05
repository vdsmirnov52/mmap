function view_canvas(iddom) {
var popCanvas = $(iddom);	//	$("#popChart");
var barChart = new Chart(popCanvas, {
type: 'radar',	// line, bar, radar, polarArea, pie, doughnut или bubble
 // type: 'line',
data: {
	labels: ["China", "India", "United States", "Indonesia", "Brazil", "Pakistan", "Nigeria", "Bangladesh", "Russia", "Japan"],
	datasets: [{
		label: 'Population',
		data: [1379302771, 1281935911, 326625791, 260580739, 207353391, 204924861, 190632261, 157826578, 142257519, 126451398],
		backgroundColor: [
			'rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)',
			'rgba(255, 159, 64, 0.6)', 'rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', ]
		},{
		label: 'Next',
		data: [126451398, 142257519, 157826578, 190632261, 204924861, 207353391, 260580739, 326625791, 1281935911, 1379302771]
		}]
	},
options: {
//	legend: { display: true, position: 'bottom', labels: { boxWidth: 80, fontColor: 'rgb(60, 180, 100)' } },
//	tooltips: { cornerRadius: 0, caretSize: 0, xPadding: 16, yPadding: 10, backgroundColor: 'rgba(0, 150, 100, 0.9)', titleFontStyle: 'normal', titleMarginBottom: 15 }
	}
});
};

function	my_canvas (iddom, data) {
var	timeCanvas = $(iddom);
var	opts = {type: 'radar',
		data: {labels: ['04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
			'20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00'],
		options: {},
		datasets: [{label: 'Time', backgroundColor: ['rgba(54, 162, 235, 0.6)'],
			data: eval(data)	// [11, 22, 11, 44, 22, 55, 66, 77, 55, 44, 33, 88]	// eval(data)
		},{	label: 'Qwerty', backgroundColor: ['rgba(255, 99, 132, 0.6)'],
			data: [37, 35, 34, 33, 33, 75, 70, 46, 46, 45, 41, 20, 55, 84, 62, 33, 3, 3, 33, 33, 33, 33, 33]
		}		
		]}};
	var	barChart = new Chart(timeCanvas, opts);
}

function	big_canvas (iddom, labels, data) {
var	timeCanvas = $(iddom);
var	opts = {type: 'line',
		data: {labels: eval(labels),
		options: {},
		datasets: [{label: 'Расстояние до гаража, км', backgroundColor: ['rgba(54, 162, 235, 0.6)'],
			data: eval(data)
		}]
		}};
	var	barChart = new Chart(timeCanvas, opts);
}

