<template>
  <div id="stock-details">
    <!-- 股票名称和代码及简介 -->
    <div class="stock-header">
      <h1>{{ stockName }} ({{ stockCode }})</h1>
      <p>{{ stockIntroduction }}</p>
    </div>

    <!-- K线图选择区域 -->
    <div class="chart-section">
      <h2>K线图</h2>
      <div class="chart-options">
        <label for="chart-type">选择类型:</label>
        <select v-model="chartType" id="chart-type">
          <option value="1">日线</option>
          <option value="2">周线</option>
          <option value="3">月线</option>
        </select>

        <label for="time-span">输入时间跨度:</label>
        <input type="text" v-model="timeSpan" id="time-span" placeholder="如：400" />
        <button @click="getStockQurve">获取</button>
      </div>
      <div v-if="loadingKline" class="loading-container">
        <div class="loading-spinner"></div>
        <p>K线图加载中...</p>
      </div>
      <div v-else class="chart-container">
        <div id="kline-chart" style="width: 100%; height: 400px;"></div>
      </div>
    </div>

    <!-- 技术指标 -->
    <div class="indicator-section">
      <h2>技术指标</h2>
      <div class="indicators">
        <label for="indicator-type">选择技术指标：</label>
        <select v-model="indicatorType" id="indicator-type" @change="updateIndicatorChart">
          <option value="MACD_12_26_9">MACD</option>
          <option value="K_9_3">KDJ</option>
          <option value="BBM_5_2.0">BOLL</option>
          <option value="BIAS_SMA_26">BIAS</option>
          <option value="RSI_14">RSI</option>
          <option value="WILLR_14">WR</option>
        </select>
      </div>
      <div v-if="loadingIndicator" class="loading-container">
        <div class="loading-spinner"></div>
        <p>技术指标加载中...</p>
      </div>
      <div v-else class="chart-container">
        <div id="indicator-chart" style="width: 100%; height: 400px;"></div>
      </div>
    </div>

    <!-- 公司财务指标 -->
    <div class="financial-section">
      <h2>公司财务指标</h2>
      <div v-if="loadingFinancial" class="loading-container">
        <div class="loading-spinner"></div>
        <p>财务数据加载中...</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>公告日期</th>
            <th>扣非净利润(元)</th>
            <th>净利润同比增长率(%)</th>
            <th>营业收入同比增长率(%)</th>
            <th>每股净资产(元)</th>
            <th>每股现金流量净额(元)</th>
            <th>净资产收益率(%)</th>
            <th>应收账款周转率(%)</th>
            <th>销售毛利率(%)</th>
            <th>营业收入(元)</th>
            <th>净利润(不含少数股东损益)(元)</th>
            <th>基本每股收益(元)</th>
            <th>销售费用(元)</th>
            <th>管理费用(元)</th>
            <th>研发费用(元)</th>
            <th>财务费用(元)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="financial in financialMetrics" :key="financial.ann_date">
            <td>{{ financial.ann_date }}</td>
            <td>{{ financial.profit_dedt }}</td>
            <td>{{ financial.q_profit_yoy }}</td>
            <td>{{ financial.or_yoy }}</td>
            <td>{{ financial.bps }}</td>
            <td>{{ financial.cfps }}</td>
            <td>{{ financial.roe }}</td>
            <td>{{ financial.ar_turn }}</td>
            <td>{{ financial.grossprofit_margin }}</td>
            <td>{{ financial.revenue }}</td>
            <td>{{ financial.n_income_attr_p }}</td>
            <td>{{ financial.basic_eps }}</td>
            <td>{{ financial.sell_exp }}</td>
            <td>{{ financial.admin_exp }}</td>
            <td>{{ financial.rd_exp }}</td>
            <td>{{ financial.fin_exp }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 股票估值比率变化图 -->
    <div class="valuation-section">
      <h2>股票估值比率变化图</h2>
      <div v-if="loadingValuation" class="loading-container">
        <div class="loading-spinner"></div>
        <p>估值比率图加载中...</p>
      </div>
      <div v-else class="chart-container">
        <div id="valuation-chart" style="width: 100%; height: 400px;"></div>
      </div>
    </div>

    <!-- 预测分析区域 -->
    <div class="forecast-section">
      <button @click="toggleForecast" v-if="!forecastVisible">进行预测分析</button>
      <div v-if="forecastVisible">
        <h2>预测分析内容</h2>

        <!-- Transformer预测结果 -->
        <div class="forecast-item">
          <h3>Transformer预测结果</h3>
          <div class="prediction-result">
            <div class="prediction-card">
              <div class="prediction-value">{{ nextClose }} <span>元</span></div>
              <div class="prediction-label">预测下一个收盘价</div>
            </div>
            <div class="prediction-card">
              <div class="prediction-value" :class="{ 'positive': gainRate > 0, 'negative': gainRate < 0 }">
                {{ gainRate > 0 ? '+' : '' }}{{ gainRate }}% <i class="arrow"
                  :class="{ 'up': gainRate > 0, 'down': gainRate < 0 }"></i>
              </div>
              <div class="prediction-label">对应的收益率</div>
            </div>
          </div>
        </div>

        <!-- Z分模型得分 -->
        <div class="forecast-item">
          <h3>Z分模型得分</h3>
          <div class="z-score-container">
            <div class="z-score-value">
              <span>总得分：</span>
              <strong>{{ zScore }}</strong>
            </div>
            <table class="z-score-table">
              <thead>
                <tr>
                  <th>指标</th>
                  <th>描述</th>
                  <th>得分</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>X1</td>
                  <td>流动资产与流动负债之差占比</td>
                  <td>{{ X[0] }}</td>
                </tr>
                <tr>
                  <td>X2</td>
                  <td>保留盈余占比</td>
                  <td>{{ X[1] }}</td>
                </tr>
                <tr>
                  <td>X3</td>
                  <td>总利润占比</td>
                  <td>{{ X[2] }}</td>
                </tr>
                <tr>
                  <td>X4</td>
                  <td>市值占比</td>
                  <td>{{ X[3] }}</td>
                </tr>
                <tr>
                  <td>X5</td>
                  <td>营业收入占比</td>
                  <td>{{ X[4] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 夏普比率 -->
        <div class="forecast-item">
          <h3>夏普比率分析</h3>
          <div class="sharpe-ratio-container">
            <div class="sharpe-ratio-value">
              <div class="ratio-circle" :class="getSharpeRatioClass">
                {{ sharpeRatio }}
              </div>
            </div>
            <div class="sharpe-ratio-desc">
              <p>夏普比率是衡量投资组合风险调整后收益的指标。</p>
              <p>比率越高，表示单位风险所获得的超额回报越高。</p>
            </div>
          </div>
        </div>

        <!-- 国债收益率 -->
        <div class="forecast-item">
          <h3>参考国债收益率</h3>
          <table class="bond-rate-table">
            <thead>
              <tr>
                <th>期限</th>
                <th>收益率(%)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(rate, period) in rateMap" :key="period">
                <td>{{ period }}</td>
                <td>{{ rate }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'StockDetail',
  data() {
    return {
      stockCode: localStorage.getItem('stockCode') || '',
      stockName: localStorage.getItem('stockName') || '',
      stockIntroduction: '',
      klineData: [],
      klineTitle: '',
      chart: null,
      indicatorChart: null,
      valuationChart: null,
      indicatorData: [],
      valuationData: [],
      chartType: '1',
      timeSpan: 500,
      indicatorType: 'MACD_12_26_9',
      financialMetrics: [],
      loadingKline: false,
      loadingIndicator: false,
      loadingValuation: false,
      loadingFinancial: false,

      forecastVisible: false,
      nextClose: 0,
      gainRate: 0,
      zScore: 0,
      X: [],
      sharpeRatio: 0,
      rateMap: {},

      // 技术指标名称映射
      indicatorNameMap: {
        'MACD_12_26_9': 'MACD',
        'K_9_3': 'KDJ',
        'BBM_5_2.0': 'BOLL',
        'BIAS_SMA_26': 'BIAS',
        'RSI_14': 'RSI',
        'WILLR_14': 'WR'
      },

      // 估值指标名称映射
      valuationNameMap: {
        'pe': '市盈率(PE)',
        'pb': '市净率(PB)',
        'ps': '市销率(PS)'
      }
    };
  },
  computed: {
    getSharpeRatioClass() {
      if (this.sharpeRatio >= 0) return 'excellent';
      if (this.sharpeRatio >= -50) return 'good';
      if (this.sharpeRatio >= -100) return 'average';
      return 'poor';
    }
  },
  methods: {
    async getIntroduction() {
      try {
        const response = await this.$axios.get('/platform/gainIntroduction', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.stockIntroduction = response.data.introduction;
        } else if (response.data.status === 'ERROR') {
          this.$message.error('公司简介获取失败:' + response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    drawKlineChart(data, title) {
      const chartDom = document.getElementById('kline-chart');
      if (!chartDom) return;

      if (this.chart) {
        this.chart.dispose();
      }
      this.chart = echarts.init(chartDom);

      // 处理日期，减少横坐标密集问题
      const dates = data.map(item => item.trade_date);
      const displayDates = [];
      const step = Math.ceil(dates.length / 10);

      for (let i = 0; i < dates.length; i++) {
        displayDates.push(i % step === 0 ? dates[i] : '');
      }

      // 设置K线图和交易量图表选项
      const option = {
        backgroundColor: '#fff',
        title: {
          text: title,
          left: 'center',
          textStyle: {
            fontSize: 16
          }
        },
        legend: {
          data: ['K线', '5日均线', '10日均线', '20日均线'],
          top: '30px'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            lineStyle: {
              color: '#999',
              width: 1,
              type: 'dashed'
            }
          }
        },
        axisPointer: {
          link: { xAxisIndex: 'all' }
        },
        grid: [{
          left: '3%',
          right: '3%',
          top: '60px',
          height: '60%'
        }, {
          left: '3%',
          right: '3%',
          top: '75%',
          height: '15%'
        }],
        xAxis: [
          {
            type: 'category',
            data: dates,
            axisLabel: {
              rotate: 45,
              formatter: function (value, index) {
                return displayDates[index];
              }
            },
            boundaryGap: false,
            axisLine: { lineStyle: { color: '#8392A5' } },
            splitLine: { show: false }
          },
          {
            type: 'category',
            gridIndex: 1,
            data: dates,
            axisLabel: { show: false },
            axisLine: { lineStyle: { color: '#8392A5' } },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],
        yAxis: [
          {
            scale: true,
            splitArea: {
              show: true,
              areaStyle: {
                color: ['rgba(250,250,250,0.1)', 'rgba(240,240,240,0.1)']
              }
            },
            axisLine: { lineStyle: { color: '#8392A5' } },
            splitLine: {
              show: true,
              lineStyle: {
                color: '#eee',
                type: 'dashed'
              }
            }
          },
          {
            scale: true,
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: [0, 1],
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线',
            type: 'candlestick',
            data: data.map(item => [item.open, item.close, item.low, item.high]),
            itemStyle: {
              color: '#ec0000',
              color0: '#00da3c',
              borderColor: '#ec0000',
              borderColor0: '#00da3c'
            },
            markPoint: {
              label: {
                formatter: function (param) {
                  return param != null ? Math.round(param.value) + '' : '';
                }
              },
              data: [
                {
                  name: '最高值',
                  type: 'max',
                  valueDim: 'highest'
                },
                {
                  name: '最低值',
                  type: 'min',
                  valueDim: 'lowest'
                }
              ],
              tooltip: {
                formatter: function (param) {
                  return param.name + '<br>' + (param.data.coord || '');
                }
              }
            }
          },
          {
            name: '5日均线',
            type: 'line',
            data: calculateMA(5, data),
            smooth: true,
            lineStyle: {
              opacity: 0.5
            }
          },
          {
            name: '10日均线',
            type: 'line',
            data: calculateMA(10, data),
            smooth: true,
            lineStyle: {
              opacity: 0.5
            }
          },
          {
            name: '20日均线',
            type: 'line',
            data: calculateMA(20, data),
            smooth: true,
            lineStyle: {
              opacity: 0.5
            }
          },
          {
            name: '成交量',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: data.map(item => {
              const color = item.open < item.close ? '#00da3c' : '#ec0000';
              return {
                value: item.vol,
                itemStyle: {
                  color: color
                }
              };
            })
          }
        ]
      };

      this.chart.setOption(option);

      // 添加窗口大小变化时自动调整图表大小
      window.addEventListener('resize', () => {
        if (this.chart) {
          this.chart.resize();
        }
      });

      // 计算移动平均线函数
      function calculateMA(dayCount, data) {
        var result = [];
        for (var i = 0, len = data.length; i < len; i++) {
          if (i < dayCount - 1) {
            result.push('-');
            continue;
          }
          var sum = 0;
          for (var j = 0; j < dayCount; j++) {
            sum += +data[i - j].close;
          }
          result.push((sum / dayCount).toFixed(2));
        }
        return result;
      }
    },
    async getStockQurve() {
      try {
        this.loadingKline = true;
        const response = await this.$axios.get('/platform/showStockQurve', {
          params: {
            stockCode: this.stockCode,
            timeSpan: this.timeSpan,
            type: this.chartType
          }
        });

        if (response.data.status === 'SUCCESS') {
          this.klineData = response.data.data;
          this.klineTitle = response.data.title;

          // 确保DOM已经更新
          await this.$nextTick();
          // 使用更长的延迟确保DOM完全渲染
          setTimeout(() => {
            if (this.klineData && this.klineData.length > 0) {
              try {
                this.drawKlineChart(this.klineData, this.klineTitle);
              } catch (err) {
                console.error('绘制K线图失败:', err);
              }
            }
          }, 300);
        } else {
          this.$message.error('K线图数据获取失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        console.error('获取K线数据出错:', error);
        alert(error.message);
      } finally {
        this.loadingKline = false;
      }
    },
    async getTechnicalIndicator() {
      try {
        this.loadingIndicator = true;
        const response = await this.$axios.get('/platform/showTechnicalIndicator', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.indicatorData = response.data.indicatorData;
          await this.$nextTick();
          // 添加延迟确保DOM完全渲染
          setTimeout(() => {
            this.updateIndicatorChart();
          }, 300);
        } else if (response.data.status === 'ERROR') {
          this.$message.error('技术指标变化图获取失败:' + response.data.errorMessage);
        }
      } catch (error) {
        console.error('获取技术指标出错:', error);
        this.$message.error(error.message);
      } finally {
        this.loadingIndicator = false;
      }
    },
    updateIndicatorChart() {
      if (!this.indicatorData || this.indicatorData.length === 0) {
        console.warn('技术指标数据为空，无法绘制图表');
        return;
      }

      const chartDom = document.getElementById('indicator-chart');
      if (!chartDom) {
        console.warn('找不到技术指标图表DOM元素');
        return;
      }

      if (this.indicatorChart) {
        this.indicatorChart.dispose();
      }

      this.indicatorChart = echarts.init(chartDom);

      // 提取日期和选定的指标数据
      const dates = this.indicatorData.map(item => item.trade_date);
      const values = this.indicatorData.map(item => item[this.indicatorType]);

      console.log('绘制技术指标图表:', this.indicatorType);
      console.log('日期数据:', dates);
      console.log('指标值:', values);

      // 设置图表选项
      const option = {
        title: {
          text: this.indicatorNameMap[this.indicatorType] + '指标变化',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}'
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            rotate: 45,
            interval: Math.floor(dates.length / 10)
          }
        },
        yAxis: {
          type: 'value',
          scale: true
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            type: 'slider',
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: this.indicatorNameMap[this.indicatorType],
            type: 'line',
            data: values,
            smooth: true,
            lineStyle: {
              width: 2
            },
            itemStyle: {
              color: '#5470c6'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgba(84, 112, 198, 0.5)'
                },
                {
                  offset: 1,
                  color: 'rgba(84, 112, 198, 0.1)'
                }
              ])
            }
          }
        ]
      };

      this.indicatorChart.setOption(option);

      // 添加窗口大小变化时自动调整图表大小
      window.addEventListener('resize', () => {
        if (this.indicatorChart) {
          this.indicatorChart.resize();
        }
      });
    },
    async getFinancialMetric() {
      try {
        const response = await this.$axios.get('/platform/getFinancialMetric', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.financialMetrics = response.data.financialMetricMap;
        } else if (response.data.status === 'ERROR') {
          alert('财务数据获取失败:' + response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async getValuationRatio() {
      try {
        this.loadingValuation = true;
        const response = await this.$axios.get('/platform/showValuationRatio', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.valuationData = response.data.valuationData;
          await this.$nextTick();
          // 添加延迟确保DOM完全渲染
          setTimeout(() => {
            this.drawValuationChart();
          }, 300);
        } else if (response.data.status === 'ERROR') {
          this.$message.error('股票估值比率变化图获取失败:' + response.data.errorMessage);
        }
      } catch (error) {
        console.error('获取估值比率出错:', error);
        this.$message.error(error.message);
      } finally {
        this.loadingValuation = false;
      }
    },

    drawValuationChart() {
      if (!this.valuationData || this.valuationData.length === 0) {
        console.warn('估值数据为空，无法绘制图表');
        return;
      }

      const chartDom = document.getElementById('valuation-chart');
      if (!chartDom) {
        console.warn('找不到估值图表DOM元素');
        return;
      }

      if (this.valuationChart) {
        this.valuationChart.dispose();
      }

      this.valuationChart = echarts.init(chartDom);

      // 提取日期和估值指标数据
      const dates = this.valuationData.map(item => item.trade_date);
      const peValues = this.valuationData.map(item => item.pe);
      const pbValues = this.valuationData.map(item => item.pb);
      const psValues = this.valuationData.map(item => item.ps);

      // 设置图表选项
      const option = {
        title: {
          text: '股票估值比率变化',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['市盈率(PE)', '市净率(PB)', '市销率(PS)'],
          top: '30px'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            rotate: 45,
            interval: Math.floor(dates.length / 10)
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '市盈率/市销率',
            position: 'left',
            axisLine: {
              show: true,
              lineStyle: {
                color: '#5470c6'
              }
            },
            axisLabel: {
              formatter: '{value}'
            }
          },
          {
            type: 'value',
            name: '市净率',
            position: 'right',
            axisLine: {
              show: true,
              lineStyle: {
                color: '#91cc75'
              }
            },
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            type: 'slider',
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: '市盈率(PE)',
            type: 'line',
            data: peValues,
            smooth: true,
            lineStyle: {
              width: 2
            },
            itemStyle: {
              color: '#5470c6'
            }
          },
          {
            name: '市净率(PB)',
            type: 'line',
            yAxisIndex: 1,
            data: pbValues,
            smooth: true,
            lineStyle: {
              width: 2
            },
            itemStyle: {
              color: '#91cc75'
            }
          },
          {
            name: '市销率(PS)',
            type: 'line',
            data: psValues,
            smooth: true,
            lineStyle: {
              width: 2
            },
            itemStyle: {
              color: '#fac858'
            }
          }
        ]
      };

      this.valuationChart.setOption(option);

      // 添加窗口大小变化时自动调整图表大小
      window.addEventListener('resize', () => {
        if (this.valuationChart) {
          this.valuationChart.resize();
        }
      });
    },
    // 请求股票数据
    async fetchStockData() {
      this.getIntroduction();
      this.getFinancialMetric();
      this.getStockQurve();
      this.getValuationRatio();
      this.getTechnicalIndicator();
    },
    // 切换预测分析显示状态
    async forecastStock() {
      try {
        const response = await this.$axios.get('/platform/analyse/forecastStock', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.nextClose = response.data.result;
          this.gainRate = response.data.gainRate;
        } else if (response.data.status === 'ERROR') {
          alert('Transformer预测失败:' + response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async getZScore() {
      try {
        const response = await this.$axios.get('/platform/analyse/showZScore', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.zScore = response.data.zScore;
          this.X = response.data.X;
        } else if (response.data.status === 'ERROR') {
          alert('Z分模型得分计算失败:' + response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async getSharpeRatio() {
      try {
        const response = await this.$axios.get('/platform/analyse/showSharpeRatio', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS') {
          this.sharpeRatio = response.data.sharpeRatio;
          this.rateMap = response.data.rateMap;
        } else if (response.data.status === 'ERROR') {
          alert('夏普比率计算失败:' + response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async toggleForecast() {
      this.forecastStock();
      this.getZScore();
      this.getSharpeRatio();
      this.forecastVisible = !this.forecastVisible;
    }
  },
  created() {
    this.fetchStockData();
  },
  beforeDestroy() {
    // 清理图表实例，避免内存泄漏
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
    if (this.indicatorChart) {
      this.indicatorChart.dispose();
      this.indicatorChart = null;
    }
    if (this.valuationChart) {
      this.valuationChart.dispose();
      this.valuationChart = null;
    }
    // 移除事件监听器
    window.removeEventListener('resize', () => { });
  }
};
</script>

<style scoped>
#stock-details {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  color: #2c3e50;
  background-color: #f8f9fa;
  line-height: 1.6;
}

/* 通用样式 */
h1,
h2,
h3 {
  color: #1a237e;
  margin: 1.2em 0 0.8em;
  font-weight: 600;
  letter-spacing: -0.5px;
}

h1 {
  font-size: 2.2rem;
  border-bottom: 2px solid #e8eaf6;
  padding-bottom: 0.5em;
  color: #303f9f;
}

h2 {
  font-size: 1.6rem;
  color: #3949ab;
  position: relative;
  padding-left: 12px;
}

h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 25%;
  height: 50%;
  width: 4px;
  background: linear-gradient(to bottom, #3f51b5, #7986cb);
  border-radius: 2px;
}

button {
  background: linear-gradient(135deg, #3f51b5, #5c6bc0);
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(63, 81, 181, 0.3);
}

button:hover {
  background: linear-gradient(135deg, #303f9f, #3f51b5);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(63, 81, 181, 0.4);
}

select,
input {
  padding: 8px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin: 0 8px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
  font-size: 0.95rem;
}

select:focus,
input:focus {
  border-color: #7986cb;
  outline: none;
  box-shadow: 0 0 0 3px rgba(121, 134, 203, 0.2);
}

/* 卡片式布局 */
.chart-section,
.indicator-section,
.financial-section,
.valuation-section,
.forecast-section>div,
.stock-header {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 28px;
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid rgba(230, 230, 250, 0.7);
}

.chart-section:hover,
.indicator-section:hover,
.valuation-section:hover,
.forecast-section>div:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

/* K线图区域 */
.chart-options {
  display: flex;
  gap: 16px;
  align-items: center;
  margin: 20px 0;
  flex-wrap: wrap;
}

.chart-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-top: 16px;
  overflow: hidden;
}

/* 技术指标 */
.indicators {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.indicators label {
  margin-right: 10px;
  font-weight: 500;
}

.indicators select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #d0d7de;
  background-color: #fff;
  font-size: 14px;
  color: #24292f;
  cursor: pointer;
  transition: border-color 0.3s;
}

.indicators select:hover,
.indicators select:focus {
  border-color: #3f51b5;
  outline: none;
}

/* 财务表格 */
.financial-section {
  overflow-x: auto;
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-top: 16px;
  min-width: 1000px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

th,
td {
  padding: 14px;
  text-align: right;
  border-bottom: 1px solid #eee;
  font-size: 0.9em;
}

th {
  background: linear-gradient(to bottom, #f5f7ff, #e8eaf6);
  font-weight: 600;
  color: #3f51b5;
  position: sticky;
  top: 0;
  z-index: 10;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background-color: #f5f7ff;
}

/* 图片样式 */
img {
  width: 100%;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-top: 16px;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s;
}

img:hover {
  transform: scale(1.01);
}

/* 添加一些动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stock-header,
.chart-section,
.indicator-section,
.financial-section,
.valuation-section,
.forecast-section {
  animation: fadeIn 0.5s ease-out forwards;
}

.chart-section {
  animation-delay: 0.1s;
}

.indicator-section {
  animation-delay: 0.2s;
}

.financial-section {
  animation-delay: 0.3s;
}

.valuation-section {
  animation-delay: 0.4s;
}

.forecast-section {
  animation-delay: 0.5s;
}

/* 预测分析 */
.forecast-section button {
  margin: 20px 0;
  width: 100%;
  padding: 14px;
  font-size: 1.1rem;
  background: linear-gradient(135deg, #3949ab, #5c6bc0);
}

.forecast-item {
  background: white;
  border-radius: 10px;
  padding: 24px;
  margin: 20px 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #7986cb;
  transition: all 0.3s ease;
}

.forecast-item:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-3px);
}

.forecast-item h3 {
  color: #3f51b5;
  margin-top: 0;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.forecast-item h3::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: #3f51b5;
  border-radius: 50%;
  margin-right: 10px;
}

/* Transformer预测结果样式 */
.prediction-result {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.prediction-card {
  flex: 1;
  background: linear-gradient(to bottom right, #f5f7ff, #e8eaf6);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.03);
}

.prediction-value {
  font-size: 2rem;
  font-weight: 600;
  color: #303f9f;
  margin-bottom: 10px;
}

.prediction-value span {
  font-size: 1.2rem;
  opacity: 0.8;
}

.prediction-label {
  color: #666;
  font-size: 0.9rem;
}

.positive {
  color: #f44336;
}

.negative {
  color: #4caf50;
}

.arrow {
  display: inline-block;
  width: 0;
  height: 0;
  margin-left: 5px;
}

.arrow.up {
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 8px solid #4caf50;
}

.arrow.down {
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 8px solid #f44336;
}

/* Z分模型表格样式 */
.z-score-container {
  margin-top: 15px;
}

.z-score-value {
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: #333;
}

.z-score-value strong {
  font-size: 1.5rem;
  color: #303f9f;
  margin-left: 5px;
}

.z-score-table,
.bond-rate-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin: 15px 0;
}

.z-score-table th,
.bond-rate-table th {
  background: linear-gradient(to bottom, #f0f2ff, #e3e6ff);
  color: #3f51b5;
  font-weight: 600;
  text-align: left;
  padding: 12px 15px;
}

.z-score-table td,
.bond-rate-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
  text-align: left;
}

.z-score-table tr:last-child td,
.bond-rate-table tr:last-child td {
  border-bottom: none;
}

.z-score-table tr:nth-child(even),
.bond-rate-table tr:nth-child(even) {
  background-color: #f9faff;
}

.z-score-table tr:hover td,
.bond-rate-table tr:hover td {
  background-color: #f0f2ff;
}

/* 夏普比率样式 */
.sharpe-ratio-container {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-top: 15px;
}

.sharpe-ratio-value {
  flex-shrink: 0;
}

.ratio-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #3949ab, #5c6bc0);
  box-shadow: 0 4px 15px rgba(63, 81, 181, 0.3);
}

.ratio-circle.good {
  background: linear-gradient(135deg, #43a047, #66bb6a);
}

.ratio-circle.excellent {
  background: linear-gradient(135deg, #00897b, #26a69a);
}

.ratio-circle.poor {
  background: linear-gradient(135deg, #e53935, #ef5350);
}

.sharpe-ratio-desc {
  flex: 1;
}

.sharpe-ratio-desc p {
  margin: 0 0 10px;
  color: #555;
}

.sharpe-ratio-desc ul {
  margin-top: 10px;
  padding-left: 20px;
}

.sharpe-ratio-desc li {
  margin-bottom: 5px;
  color: #666;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chart-options {
    flex-direction: column;
    align-items: stretch;
  }

  button,
  select,
  input {
    margin: 6px 0;
    width: 100%;
  }

  h1 {
    font-size: 1.8rem;
  }

  .financial-section {
    padding: 15px;
  }

  .stock-header h1 {
    font-size: 1.6rem;
  }

  .prediction-result {
    flex-direction: column;
  }

  .sharpe-ratio-container {
    flex-direction: column;
    align-items: flex-start;
  }

  .ratio-circle {
    margin: 0 auto 20px;
  }
}
</style>