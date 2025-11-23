// http://mussyu1204.myhome.cx/wordpress/it/?p=322
var shuuzenhichart;

// 一度描画したcanvasが消せない！
function clearCanvas(){
    // canvas要素を取り出す。
    var canvas = document.getElementById("simulate_graph");
    // contextを取得。
    var ctx = canvas.getContext('2d');
    // クリアする。
    ctx.clearRect(0,0,800,500);
    if (shuuzenhichart){
        shuuzenhichart.destroy();
    }
}
/*
****************************************************************
* 多次元配列による修繕費収入グラフ表示 by N.Goto
****************************************************************
*/
function simulateShuuzenhiChart(data){
    // (1) chart.jsのdataset用の配列を用意。
    var xLabels = [], incomeData = [], expenseData = []; differenceData = [];
    for (var row in data) {
        xLabels.push(data[row][0]);
        incomeData.push(data[row][1]);
        expenseData.push(data[row][2]);
        differenceData.push(data[row][1]-data[row][2]);
    }
    // (2) データオブジェクトを用意。
    var chartData = {
        labels: xLabels,      // x軸ラベル配列。
        datasets: [
            {
                type: 'line',
                fill: false,   // 面を非表示 trueの場合backgroundColorを指定すること。
                label: '修繕費収入累計',
                borderWidth: 2,                 // 線の太さ
                borderColor: "red",             // 線の色
                tension:0,                      // 線は直線
                pointBorderColor: "red",        // ポイント線の色
                pointBackgroundColor: "red",    // ポイント面の色
                pointRadius: 2,                 // ポイントサイズ
                pointHoverRadius: 6,            // ホバーした時のポイントサイズ
                pointHitRadius: 8,              // カーソルのヒットエリア
                backgroundColor: "red",
                data: incomeData,
                yAxisID: "y-axis",
            },
            {
                type: 'line',
                fill: false,                    // 面を非表示 trueの場合backgroundColorを指定すること。
                label: '修繕費支出累計',
                borderWidth: 2,                 // 線の太さ
                borderColor: "blue",            // 線の色
                tension:0,                      // 線は直線
                pointBorderColor: "blue",       // ポイント線の色
                pointBackgroundColor: "blue",   // ポイント面の色
                pointRadius: 2,                 // ポイントサイズ
                pointHoverRadius: 6,            // ホバーした時のポイントサイズ
                pointHitRadius: 8,              // カーソルのヒットエリア
                backgroundColor: "blue",
                data: expenseData,
                yAxisID: "y-axis",
            },
            // 残高のチャートは表示しない。2024-02-09
            // {
            //     type: 'line',
            //     fill: false,                    // 面を非表示 trueの場合backgroundColorを指定すること。
            //     label: '資産残高(右目盛り)',
            //     borderWidth: 2,                 // 線の太さ
            //     borderColor: "green",           // 線の色
            //     tension:0,                      // 線は直線
            //     pointBorderColor: "green",      // ポイント線の色
            //     pointBackgroundColor: "green",  // ポイント面の色
            //     pointRadius: 2,                 // ポイントサイズ
            //     pointHoverRadius: 6,            // ホバーした時のポイントサイズ
            //     pointHitRadius: 8,              // カーソルのヒットエリア
            //     backgroundColor: "green",
            //     data: differenceData,
            //     yAxisID: "y-axis-difference"
            // }
        ]
    };
    // (3) チャートオプション
    // http://www.chartjs.org/docs/#chart-configuration-tooltip-configuration
    var myChartOption = {
        responsive:true,   // canvasサイズを固定する。(trueの場合windowの大きさに連動する)
        maintainAspectRatio: true,
        title: {
            display: true,
            fontSize:14,
            text: '修繕費シミュレーション'
        },
        scales: {
            yAxes: [
                {
                    id: "y-axis",
                    type: "linear",
                    position: "left", // 目盛りは左側に表示。
                    scaleLabel:{
                        display:true,
                        fontSize:10,
                        fontStyle:"bold",
                        labelString:"単位 (円)",
                    },
                    gridLines: {    // 横軸グリッドラインを非表示にする。
                        drawOnChartArea: true,
                    },
                    ticks:{ // Y軸目盛を3桁区切りにする。
                        callback: function (value) {
                            // 正規表現による3桁区切り。
                            return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                            // ブラウザがHTML5対応していれば以下でオーケー。
                            //return value.toLocaleString();
                        }
                    }
                },
                // 残高のチャートは表示しない。2024-02-09
                // {
                //     id: "y-axis-difference",
                //     type: "linear",
                //     position: "right", // 目盛りは右側に表示。
                //     scaleLabel:{
                //         display:true,
                //         fontSize:10,
                //         fontStyle:"bold",
                //         labelString:"単位 (円)",
                //     },
                //     gridLines: {    // 横軸グリッドラインを表示にする。
                //         drawOnChartArea: false,
                //     },
                //     ticks:{ // Y軸目盛を3桁区切りにする。
                //         callback: function (value) {
                //             // ブラウザがHTML5対応していれば以下でオーケー。
                //             return value.toLocaleString();
                //             // 正規表現による3桁区切り。ブラウザがHTML5非対応の場合
                //             // return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                //         }
                //     }
                // }
            ],
            xAxes: [{
                display: true,
                scaleLabel:{
                    display:true,
                    fontSize:10,
                    fontStyle:"bold",
                    labelString:"西暦",
                },
                gridLines: {
                    display: true
                },
                ticks: {
                    fontColor:"black",
                    callback:function(value){
                        return value;
                    }
                }
            }]
        },
        legend: {
            labels: {
                boxWidth:10,
                padding:20 //凡例の各要素間の距離
            },
            display: true
        },
        tooltips: {
            enabled: true,
            mode: 'index',
            displayColors:true,           // 凡例を表示する。
            titleFontColor: 'white',
            titleFontSize: 14,            // デファルトは12。
            bodyFontColor: 'white',
            bodyFontSize: 14,             // デファルトは12。
            backgroundColor: 'black',
            xPadding: 12,
            yPadding: 8,
            callbacks: {
                label: function(tooltipItem,data) {
                    return '  '+ data.datasets[tooltipItem.datasetIndex].label+' : '+   tooltipItem.yLabel.toLocaleString()+' 円';
                }
            }
        },
    };
    // (4) チャート描画。
    var ctx = document.getElementById('simulate_graph').getContext('2d');
    clearCanvas();
    // chartをグローバル変数とする。http://mussyu1204.myhome.cx/wordpress/it/?p=322
    shuuzenhichart = new Chart(ctx, {
        type: 'line',               // datasetでグラフtypeを指定するだけではチャートが表示できない！？
        options: myChartOption,     // Optionを記述したオブジェクトを指定。
        data: chartData             // データオブジェクト。
    });
}

/*
****************************************************************
* mobile用に表示を調整。
****************************************************************
*/
function simulateShuuzenhiChart_mobile(data){
    // (1) chart.jsのdataset用の配列を用意。
    var xLabels = [], incomeData = [], expenseData = [];
    for (var row in data) {
        xLabels.push(data[row][0]);
        incomeData.push(data[row][1]);
        expenseData.push(data[row][2]);
    }
    // (2) データオブジェクトを用意。
    var chartData = {
        labels: xLabels,       // x軸ラベル配列。
        datasets: [
            {
                type: 'line',
                fill: false,   // 面を非表示 trueの場合backgroundColorを指定すること。
                label: '修繕費収入累計',
                borderWidth: 2,                 // 線の太さ
                borderColor: "red",             // 線の色
                tension:0,                      // 線は直線
                pointBorderColor: "red",        // ポイント線の色
                pointBackgroundColor: "red",    // ポイント面の色
                pointRadius: 2,                 // ポイントサイズ
                pointHoverRadius: 6,            // ホバーした時のポイントサイズ
                pointHitRadius: 8,              // カーソルのヒットエリア
                backgroundColor: "red",
                data: incomeData,
                yAxisID: "y-axis",
            },
            {
                type: 'line',
                fill: false,                    // 面を非表示 trueの場合backgroundColorを指定すること。
                label: '修繕費支出累計',
                borderWidth: 2,                 // 線の太さ
                borderColor: "blue",            // 線の色
                tension:0,                      // 線は直線
                pointBorderColor: "blue",       // ポイント線の色
                pointBackgroundColor: "blue",   // ポイント面の色
                pointRadius: 2,                 // ポイントサイズ
                pointHoverRadius: 6,            // ホバーした時のポイントサイズ
                pointHitRadius: 8,              // カーソルのヒットエリア
                backgroundColor: "blue",
                data: expenseData,
                yAxisID: "y-axis",
            },
        ]
    };
    // (3) チャートオプション
    // http://www.chartjs.org/docs/#chart-configuration-tooltip-configuration
    var myChartOption = {
        responsive:true,   // canvasサイズを固定する。(trueの場合windowの大きさに連動する)
        maintainAspectRatio: true,
        title: {
            display: true,
            fontSize:14,
            text: '修繕費シミュレータ'
        },
        scales: {
            yAxes: [
                {
                    id: "y-axis",
                    type: "linear",
                    position: "left",           // 目盛りは左側に表示。
                    display: false,
                    scaleLabel:{
                        display:true,
                        fontSize:9,
                        fontStyle:"bold",
                        labelString:"単位 (円)",
                    },
                    gridLines: {                // 横軸グリッドラインを非表示にする。
                        drawOnChartArea: true,
                    },
                    ticks:{                     // Y軸目盛を3桁区切りにする。
                        callback: function (value) {
                            // ブラウザがHTML5対応していれば以下でオーケー。
                            return value.toLocaleString();
                            // 正規表現による3桁区切り。ブラウザがHTML5非対応の場合
                            // return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                        }
                    }
                },
            ],
            xAxes: [{
                display: true,
                scaleLabel:{
                    display:true,
                    fontSize:10,
                    fontStyle:"bold",
                    labelString:"西暦",
                },
                gridLines: {
                    display: true
                },
                ticks: {
                    fontColor:"black",
                    callback:function(value){
                        return value;
                    }
                }
            }]
        },
        legend: {
            labels: {
                boxWidth:10,
                padding:20 //凡例の各要素間の距離
            },
            display: true
        },
        tooltips: {
            enabled: true,
            mode: 'index',
            displayColors:true,           // 凡例を表示する。
            titleFontColor: 'white',
            titleFontSize: 14,            // デファルトは12。
            bodyFontColor: 'white',
            bodyFontSize: 14,             // デファルトは12。
            backgroundColor: 'black',
            xPadding: 12,
            yPadding: 8,
            callbacks: {
                label: function(tooltipItem,data) {// https://fiddle.jshell.net/chanonroy/v2dm44gp/
                    return '  '+ data.datasets[tooltipItem.datasetIndex].label+' : '+   tooltipItem.yLabel.toLocaleString()+' 円';
                }
            }
        },
    };
    // (4) チャート描画。
    var ctx = document.getElementById('simulate_graph').getContext('2d');
    clearCanvas();
    // chartをグローバル変数とする。http://mussyu1204.myhome.cx/wordpress/it/?p=322
    shuuzenhichart = new Chart(ctx, {
        type: 'line',                // datasetでグラフtypeを指定するだけではチャートが表示できない！？
        options: myChartOption,     // Optionを記述したオブジェクトを指定。
        data: chartData             // データオブジェクト。
    });
}
