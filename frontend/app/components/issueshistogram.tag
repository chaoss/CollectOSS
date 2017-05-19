<issueshistogram>

<div class="issues-chart" style="width: 100%; height: 400px;"></div>

<script>

  this.on('mount', () => {
    var echarts = require('echarts')
    var issuesChart = echarts.init(this.root.querySelector('.issues-chart'))
    issuesChart.showLoading()

    this.opts.api.get('timeseries/issues/response_time').then((issueResponses) => {

      var data = [];
      var labels = [];

      issueResponses.forEach((elem) => {
        labels.push(elem['hours_between'])
        data.push(elem['count']);
      })

      console.log(data)

      issuesChart.hideLoading()

      issuesChart.setOption({
        color: ['#3398DB'],
        xAxis: [
          {
            type : 'category',
            label: 'Hours Before First Response',
            data: labels
          }
        ],
        yAxis: [
            {
                type: 'value',
                label: 'Count'
            }
        ],
        series: [
            {
                type: 'bar',
                barWidth: '100%',
                data: data
            }
        ]
      })

    })
  })

</script>
</issueshistogram>