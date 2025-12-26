var chart;

function clearCanvas(){
    // canvas要素を取り出す。
    const canvas = document.getElementById("stage");
    if (!canvas.getContext) {
        return;
    }

    const existingChart = Chart.getChart(canvas);
    // クリアする。
    if (existingChart) {
        existingChart.destroy();
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
    const chartData = {
        labels: xLabels,      // x軸ラベル配列。
        datasets: [
            {
                label: '工事種別支出',
                borderWidth: 2,                 // 線の太さ
                borderColor: "red",             // 線の色
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
                font:{size:14},
                text: '工事費支出グラフ'
            },
            legend: {   // 凡例
                display: true,
                labels: { boxWidth:10, padding:20 }
            },
            tooltip: {
                enabled: true,
                mode: 'index',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
            }
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
    }

    // (4) チャート描画。
    clearCanvas();
    chart = new Chart(document.getElementById('stage'), {
        type: 'bar',  
        data: chartData,
        options: myChartOption
    });
}
