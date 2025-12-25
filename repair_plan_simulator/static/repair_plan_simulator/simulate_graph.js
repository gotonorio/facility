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
function simulateShuuzenhiChart(data) {
    // (1) chart.jsのdataset用の配列を用意。
    var xLabels = [], incomeData = [], expenseData = [], differenceData = [];

    for (const row of data) {
        xLabels.push(row[0]);
        incomeData.push(row[1]);
        expenseData.push(row[2]);
        differenceData.push(row[1] - row[2]);
    }

    // (2) データオブジェクトを用意。
    const chartData = {
        labels: xLabels,
        datasets: [
            {
                type: 'line',
                label: '修繕費収入累計',
                data: incomeData,
                borderColor: 'red',
                backgroundColor: 'red',
                borderWidth: 2,
                tension: 0,
                pointRadius: 2,
                pointHoverRadius: 6,
                yAxisID: 'y',
            },
            {
                type: 'line',
                label: '修繕費支出累計',
                data: expenseData,
                borderColor: 'blue',
                backgroundColor: 'blue',
                borderWidth: 2,
                tension: 0,
                pointRadius: 2,
                pointHoverRadius: 6,
                yAxisID: 'y',
            }
        ]
    };

    // (3) チャートオプション
    const myChartOption = {
        // canvasサイズを固定する。(trueの場合windowの大きさに連動する)
        responsive: true,
        // コンテナの幅に合わせて比率を維持する
        maintainAspectRatio: true,
        // 比率の設定　2:3（幅が高さの1.5倍）にしたいので「1.5」を指定
        aspectRatio: 1.5,

        plugins: {
            title: {
                display: true,
                text: '修繕費シミュレーション',
                font: {
                    size: 14
                }
            },
            legend: {
                display: true,
                labels: {
                    boxWidth: 10,
                    padding: 20
                }
            },
            tooltip: {
                mode: 'index',
                callbacks: {
                    label: function (context) {
                        return (
                            ' ' +
                            context.dataset.label +
                            ' : ' +
                            context.parsed.y.toLocaleString() +
                            ' 円'
                        );
                    }
                }
            }
        },

        scales: {
            y: {
                type: 'linear',
                position: 'left',
                title: {
                    display: true,
                    text: '単位 (円)',
                    font: {
                        size: 10,
                        weight: 'bold'
                    }
                },
                ticks: {
                    callback: function (value) {
                        return value.toLocaleString();
                    }
                },
                grid: {
                    drawOnChartArea: true
                }
            },
            x: {
                title: {
                    display: true,
                    text: '西暦',
                    font: {
                        size: 10,
                        weight: 'bold'
                    }
                },
                grid: {
                    display: true
                }
            }
        }
    };

    new Chart(document.getElementById('simulate_graph'), {
        type: 'line',  
        data: chartData,
        options: myChartOption
    });
}


