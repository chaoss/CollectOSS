<contributions>

<div class="echarts-container" style="width: 100%; height: 400px;"></div>

<script>

  this.on('mount', () => {
    var echarts = require('echarts')
    var chart = echarts.init(this.root.querySelector('.echarts-container'))
    chart.showLoading()

    this.opts.api.get('contributions?orient=split').then((contributions) => {

      var data = [];

      contributions.data.forEach((row) => {
        for (var i = 1; i < row.length - 1; i++) {
          if (!row[i]) {
            row[i] = 0
          }
          data.push([row[0], row[i], contributions.columns[i]])
        }
      })

      chart.hideLoading()
      chart.setOption({
          singleAxis: {
            type: 'time',
            max: 'dataMax'
          },
          legend: {
            show: true,
            data: contributions.columns.splice(1, contributions.columns.length - 1)
          },
          dataZoom: [{
            type: 'inside',
            start: 90,
            end: 100
          }, {
            start: 0,
            end: 10,
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '80%',
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2
            }
          }],
          tooltip: {
            trigger: 'axis',
            position: function (pt) {
              return [pt[0], '10%'];
            }
          },
          series: [{
              type: 'themeRiver',
              data: data
          }]
      })

    })
  })

</script>
</contributions>