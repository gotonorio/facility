// http://mussyu1204.myhome.cx/wordpress/it/?p=322
var chart;

// 一度描画したcanvasが消せない！
function clearCanvas(){
    // canvas要素を取り出す。
    var canvas = document.getElementById("stage");
    // contextを取得。
    var ctx = canvas.getContext('2d');
    // クリアする。
    ctx.clearRect(0,0,800,500);
    if (chart){
        chart.destroy();
    }
}
/*
****************************************************************
* 多次元配列による修繕費収入グラフ表示 by N.Goto
****************************************************************
*/
function koujiShubetuChart(data){
    // (1) chart.jsのdataset用の配列を用意。
    var xLabels = [], cost = [];
    for (var row in data) {
        xLabels.push(data[row][0]);
        cost.push(data[row][1]);
    }
    // (2) データオブジェクトを用意。
    var chartData = {
        labels: xLabels,      // x軸ラベル配列。
        datasets: [
            {
                type: 'horizontalBar',
                fill: false,   // 面を非表示 trueの場合backgroundColorを指定すること。
                label: '工事種別支出',
                borderWidth: 2,                 // 線の太さ
                borderColor: "red",             // 線の色
                tension:0,                      //  線は直線
                pointBorderColor: "red",        // ポイント線の色
                pointBackgroundColor: "red",    // ポイント面の色
                pointRadius: 2,                 // ポイントサイズ
                pointHoverRadius: 6,            // ホバーした時のポイントサイズ
                pointHitRadius: 8,              // カーソルのヒットエリア
                backgroundColor: "red",
                data: cost,
            },
        ]
    };
    // (3) チャートオプション
    // http://www.chartjs.org/docs/#chart-configuration-tooltip-configuration
    var myChartOption = {
        responsive:true,   // canvasサイズを固定する。(trueの場合windowの大きさに連動する)
        maintainAspectRatio: true,
        title: {
            display: false,
            fontSize:14,
            text: '工事費支出グラフ'
        },
        scales: {
            xAxes: [{
                display: true,
                gridLines: {
                    display: true
                },
                ticks: {
                    fontColor:"black",
                    callback:function(value){
                        // 正規表現による3桁区切り。
                        return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                    }
                }
            }]
        },
        legend: {   // 凡例
            labels: {
                boxWidth:10,
                padding:20 //凡例の各要素間の距離
            },
            display: true
        },
        tooltips: {
            enabled: true,
            mode: 'index',
            displayColors: true,          // 凡例を表示する。
            titleFontColor: 'white',
            titleFontSize: 14,            // デファルトは12。
            bodyFontColor: 'white',
            bodyFontSize: 14,             // デファルトは12。
            backgroundColor: 'black',
            xPadding: 12,
            yPadding: 8,
            callbacks: {
                label: function(tooltipItem,data) {
                    return '  '+ tooltipItem.xLabel.toLocaleString()+' 円';
                }
            }
        },
    };
    // (4) チャート描画。
    var ctx = document.getElementById('stage').getContext('2d');
    clearCanvas();
    // chartをグローバル変数とする。http://mussyu1204.myhome.cx/wordpress/it/?p=322
    chart = new Chart(ctx, {
        type: 'horizontalBar',      // datasetでグラフtypeを指定するだけではチャートが表示できない！？
        options: myChartOption,     // Optionを記述したオブジェクトを指定。
        data: chartData             // データオブジェクト。
    });
}
