Highcharts.addEvent(Highcharts.Series, 'addPoint', e => {
    const point = e.point,
        series = e.target;

    if (!series.pulse) {
        series.pulse = series.chart.renderer.circle()
            .add(series.markerGroup);
    }
    setTimeout(() => {
        series.pulse
            .attr({
                x: series.xAxis.toPixels(point.x, true),
                y: series.yAxis.toPixels(point.y, true),
                r: series.options.marker.radius,
                opacity: 1,
                fill: series.color
            })
            .animate({
                r: 20,
                opacity: 0
            }, {
                duration: 1000
            });
    }, 1);
});

function getTDOA(x, y, x1, y1, x2, y2, trued1, trued2) {
    const d1 = Math.sqrt(Math.pow(x1 - x, 2) + Math.pow(y1 - y, 2)),
        d2 = Math.sqrt(Math.pow(x2 - x, 2) + Math.pow(y2 - y, 2));
    return d1 - d2 - (trued1 - trued2);
}

function generateTDOAData(x1, y1, x2, y2, trued1, trued2) {
    let data = [];
    for (let x = 0; x <= 100; x++) {
        for (let y = 0; y <= 100; y++) {
            data.push([x, y, getTDOA(x, y, x1, y1, x2, y2, trued1, trued2)]);
        }
    }
    return data
}

function getFDOA(x, y, vx, vy, x1, y1, x2, y2, trued1, trued2) {
    const f1 = (vx * (x - x1) + vy * (y - y1)) / Math.sqrt(Math.pow(x - x1, 2) + Math.pow(y - y1, 2)),
        f2 = (vx * (x - x2) + vy * (y - y2)) / Math.sqrt(Math.pow(x - x2, 2) + Math.pow(y - y2, 2));
    return f1 - f2 - (trued1 - trued2);
}

function generateFDOAData(vx, vy, x1, y1, x2, y2, xTrue, yTrue){
    const trued1 = (vx * (xTrue - x1) + vy * (yTrue - y1)) / Math.sqrt(Math.pow(xTrue - x1, 2) + Math.pow(yTrue - y1, 2)),
        trued2 = (vx * (xTrue - x2) + vy * (yTrue - y2)) / Math.sqrt(Math.pow(xTrue - x2, 2) + Math.pow(yTrue - y2, 2));
    let data = [];
    for (let x = 0; x <= 100; x++) {
        for (let y = 0; y <= 100; y++) {
            data.push([x, y, getFDOA(x, y, vx, vy, x1, y1, x2, y2, trued1, trued2)]);
        }
    }
    return data
}

function plotFDOA(contourSeries, receiverSeries, emitterSeries){
    var orangePoints = receiverSeries.data;
    var bluePoints = emitterSeries.data;
    x1 = orangePoints[0].x;
    y1 = orangePoints[0].y;
    x2 = orangePoints[1].x;
    y2 = orangePoints[1].y; 
    velocity = parseFloat(document.getElementById('velocity').value);
    direction = parseFloat(document.getElementById('direction').value);
    angleRadians = direction * Math.PI / 180.0;
    vx = velocity * Math.cos(angleRadians);
    vy = velocity * Math.sin(angleRadians);
    fdoaData = generateFDOAData(vx, vy, x1, y1, x2, y2, bluePoints[0].x, bluePoints[0].y);
    if (contourSeries) {
        contourSeries.setData(fdoaData, true); // true to redraw
    } else {
        // If it doesn't exist yet, add it
        this.addSeries({
            name: 'TDOA Contours',
            type: 'heatmap',  // Can be replaced with 'line' or custom type
            data: fdoaData,
            turboThreshold: 0
        });
    }
}

function plotTDOA(contourSeries, receiverSeries, emitterSeries){
    var orangePoints = receiverSeries.data;
    var bluePoints = emitterSeries.data;
    td1 = Math.sqrt( Math.pow(orangePoints[0].x - bluePoints[0].x, 2) + Math.pow(orangePoints[0].y - bluePoints[0].y, 2) );
    td2 = Math.sqrt( Math.pow(orangePoints[1].x - bluePoints[0].x, 2) + Math.pow(orangePoints[1].y - bluePoints[0].y, 2) );
    x1 = orangePoints[0].x;
    y1 = orangePoints[0].y;
    x2 = orangePoints[1].x;
    y2 = orangePoints[1].y; 
    tdoaData = generateTDOAData(x1, y1, x2, y2, td1, td2);
    if (contourSeries) {
        contourSeries.setData(tdoaData, true); // true to redraw
    } else {
        // If it doesn't exist yet, add it
        this.addSeries({
            name: 'TDOA Contours',
            type: 'heatmap',  // Can be replaced with 'line' or custom type
            data: tdoaData,
            turboThreshold: 0
        });
    }
}

function clearAndRedrawContours(chart) {
    let contourSeries = chart.series.find(s => s.name === 'TDOA Contours');
    if (contourSeries) {
        contourSeries.setData([]); // Clear the data
    }
    chart.redraw(); // Redraw the chart to reflect the empty contour series
}

document.querySelectorAll('input[name="plotMode"]').forEach((radio) => {
    radio.addEventListener('change', function() {
        // This function is triggered whenever a radio button is switched
        var selectedMode = document.querySelector('input[name="plotMode"]:checked').value;
        var chart = Highcharts.charts[0];
        var contourSeries = chart.series.find(s => s.name === 'TDOA Contours');
        var receiverSeries = chart.series.find(s => s.name === 'Receivers');
        var emitterSeries = chart.series.find(s => s.name === 'Emitter');
        clearAndRedrawContours(chart);
        if (selectedMode == 'FDOA') {
            plotFDOA(contourSeries, receiverSeries, emitterSeries);
        }else{
            plotTDOA(contourSeries, receiverSeries, emitterSeries);
        }
    });
});

document.getElementById('velocity').addEventListener('input', function() {
    var selectedMode = document.querySelector('input[name="plotMode"]:checked').value;
    if (selectedMode == 'FDOA') {
        var chart = Highcharts.charts[0];
        var contourSeries = chart.series.find(s => s.name === 'TDOA Contours');
        var receiverSeries = chart.series.find(s => s.name === 'Receivers');
        var emitterSeries = chart.series.find(s => s.name === 'Emitter');
        clearAndRedrawContours(chart);
        plotFDOA(contourSeries, receiverSeries, emitterSeries);
    }
});

document.getElementById('direction').addEventListener('input', function() {
    var selectedMode = document.querySelector('input[name="plotMode"]:checked').value;
    if (selectedMode == 'FDOA') {
        var chart = Highcharts.charts[0];
        var contourSeries = chart.series.find(s => s.name === 'TDOA Contours');
        var receiverSeries = chart.series.find(s => s.name === 'Receivers');
        var emitterSeries = chart.series.find(s => s.name === 'Emitter');
        clearAndRedrawContours(chart);
        plotFDOA(contourSeries, receiverSeries, emitterSeries);
    }
});

Highcharts.chart('container', {
    chart: {
        type: 'scatter',
        margin: [70, 50, 60, 80],
        events: {
            click: function (e) {
                const x = Math.round(e.xAxis[0].value),
                    y = Math.round(e.yAxis[0].value),
                    receiverSeries = this.series.find(s => s.name === 'Receivers');
                    emitterSeries = this.series.find(s => s.name === 'Emitter');
                
                var orangeCount = receiverSeries.data.length;
                var blueCount = emitterSeries.data.length;
                
                if (e.shiftKey){
                    if (blueCount < 1) {
                        // Add it
                        emitterSeries.addPoint({
                            x: x,
                            y: y,
                            color: '#ff00ff',
                            symbol: 'circle'
                        });
                    }
                }
                else {
                    if (orangeCount < 2) {
                        // Add it
                        receiverSeries.addPoint({
                            x: x,
                            y: y,
                            color: '#00ff00'
                        });
                    }
                }

                var orangeCount = receiverSeries.data.length;
                var blueCount = emitterSeries.data.length;
                var contourSeries = this.series.find(s => s.name === 'TDOA Contours');
                var selectedMode = document.querySelector('input[name="plotMode"]:checked').value;

                if (orangeCount >= 2 && blueCount >= 1) {
                    if (selectedMode == 'FDOA'){
                        plotFDOA(contourSeries, receiverSeries, emitterSeries);
                    }else{
                        plotTDOA(contourSeries, receiverSeries, emitterSeries);
                    }
                }
            }
        }
    },
    title: {
        text: 'TDOA and FDOA lines',
        align: 'center'
    },
    subtitle: {
        text: 'Left click the plot area to add a receiver. Shift + left click to add the emitter. Left click an existing point to remove it.',
        align: 'center'
    },
    accessibility: {
        announceNewData: {
            enabled: true
        }
    },
    xAxis: {
        title: {
            text: 'x'
        },
        min: 0,
        max: 100,
        gridLineWidth: 1,
        minPadding: 0.2,
        maxPadding: 0.2,
        maxZoom: 60
    },
    yAxis: {
        title: {
            text: 'y'
        },
        min: 0,
        max: 100,
        minPadding: 0.2,
        maxPadding: 0.2,
        maxZoom: 60,
        plotLines: [{
            value: 0,
            width: 1,
            color: '#808080'
        }]
    },
    legend: {
        enabled: false
    },
    exporting: {
        enabled: false
    },
    plotOptions: {
        series: {
            stickyTracking: true,
            lineWidth: 0,
            point: {
                events: {
                    click: function () {
                        if (this.series.data.length > 0) {
                            var contourSeries = this.series.chart.series.find(s => s.name === 'TDOA Contours');
                            if (contourSeries) {
                                contourSeries.setData([], false); // true to redraw
                            }
                            this.remove();
                            contourSeries.chart.redraw();
                        }
                    }
                }
            }
        }
    },
    colorAxis: {
        min: -40,
        max: 40,
        stops: [
            [0, '#3060cf'],
            [0.5, '#fffbbc'],
            [1, '#c4463a'],
            [1, '#c4463a']
        ]
    },
    series: [{
        name: 'TDOA Contours',
        type: 'heatmap',
        data: [],
        zindex: 1,
        colsize: 1,
        tooltip: {
            pointFormat: '{point.x}, {point.y}: {point.value}'
        }
    },{
        name: 'Receivers',
        data: [],
        zindex: 2,
        type: 'scatter',
        color: '#00ff00',
        marker: {
            lineWidth: 2,
            radius: 6
        }
    },{
        name: 'Emitter',
        data: [],
        zindex: 3,
        type: 'scatter',
        color: '#ff00ff',
        marker: {
            lineWidth: 2,
            radius: 6,
            symbol: 'circle'
        }
    }
    ]
});
