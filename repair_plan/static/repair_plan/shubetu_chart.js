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

    for (const row of data) {
        xLabels.push(row[0]);
        cost.push(row[1]);
    }
    // (2) データオブジェクトを用意。
    var chartData = {
        labels: xLabels,      // x軸ラベル配列。
        datasets: [
            {
                // type: 'bar',
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
    const myChartOption = {
        // canvasサイズを固定する。(trueの場合windowの大きさに連動する)
        responsive:true,
        // コンテナの幅に合わせて比率を維持する
        maintainAspectRatio: true,
        // 比率の設定　2:3（幅が高さの1.5倍）にしたいので「1.5」を指定
        aspectRatio: 1.5,
        // 棒グラフを横向きにする。
        indexAxis: 'y',

        plugins: {
            title: {
                display: false,
                fontSize:14,
                text: '工事費支出グラフ'
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
        },
        scales: {
            // ★ 修正点3: scales はオブジェクト構造になり、x と y を明示的に定義
            x: { // ★ indexAxis: 'y' の場合、x軸が値軸 (value axis) になる
                display: true,
                grid: {
                    display: true
                },
                ticks: {
                    color: "black", // V3以降 fontColor -> color
                    callback: function(value) {
                        // toLocaleString() の使用を推奨 (V4でより一般的)
                        return value.toLocaleString();
                    }
                },
                title: { // 軸のタイトルを追加（推奨）
                    display: true,
                    text: '支出金額 (円)'
                }
            },
            y: { // ★ indexAxis: 'y' の場合、y軸がインデックス軸 (category axis) になる
                display: true,
                grid: {
                    display: false // カテゴリ軸のグリッドは非表示が一般的
                },
                title: { // 軸のタイトルを追加（推奨）
                    display: true,
                    text: '工事種別'
                }
            }
        },
    };

    // (4) チャート描画。
    new Chart(document.getElementById('stage'), {
        type: 'bar',  
        data: chartData,
        options: myChartOption
    });
}
