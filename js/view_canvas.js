function view_canvas() {
var popCanvas = $("#popChart");
var barChart = new Chart(popCanvas, {
  type: 'bar',
 // type: 'line',
  data: {
    labels: ["China", "India", "United States", "Indonesia", "Brazil", "Pakistan", "Nigeria", "Bangladesh", "Russia", "Japan"],
    datasets: [{
      label: 'Population',
      data: [1379302771, 1281935911, 326625791, 260580739, 207353391, 204924861, 190632261, 157826578, 142257519, 126451398],
      backgroundColor: [
        'rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)', 'rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)',
      ]
    },
	{
	label: 'Next',
      data: [126451398, 142257519, 157826578, 190632261, 204924861, 207353391, 260580739, 326625791, 1281935911, 1379302771]
	}
	]
  },
  options: {
/*
    legend: {
      display: true,
      position: 'bottom',
      labels: { boxWidth: 80, fontColor: 'rgb(60, 180, 100)' }
    }
*/
        tooltips: {
          cornerRadius: 0,
          caretSize: 0,
          xPadding: 16,
          yPadding: 10,
          backgroundColor: 'rgba(0, 150, 100, 0.9)',
          titleFontStyle: 'normal',
          titleMarginBottom: 15
        }

  }
});
};
