<template>
  <div class="stock-detail-container">
    <!-- 顶部股票信息卡片 -->
    <div class="stock-header-card">
      <div class="stock-basic-info">
        <div class="stock-title">
          <h1 class="stock-name">{{ stockName }}</h1>
          <span class="stock-code">{{ stockCode }}</span>
        </div>
        <div class="stock-intro">
          <p>{{ stockIntroduction }}</p>
        </div>
      </div>
      <div class="stock-quick-stats">
        <div class="stat-item">
          <span class="stat-label">当前价格</span>
          <span class="stat-value price">¥{{ currentPrice.toFixed(2) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">涨跌幅</span>
          <span class="stat-value change" :class="priceChangePercent >= 0 ? 'positive' : 'negative'">
            {{ priceChangePercent >= 0 ? '+' : '' }}{{ priceChangePercent.toFixed(2) }}%
          </span>
        </div>
        <div class="stat-item">
          <span class="stat-label">今日开盘</span>
          <span class="stat-value open">¥{{ openPrice.toFixed(2) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">成交量</span>
          <span class="stat-value volume">{{ volume.toFixed(1) }}万手</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">市值</span>
          <span class="stat-value market-cap">{{ marketCap.toFixed(1) }}亿</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">市盈率</span>
          <span class="stat-value pe-ratio">{{ peRatio.toFixed(1) }}</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧图表区域 -->
      <div class="charts-section">
        <!-- K线图卡片 -->
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-chart"></i>
              K线图分析
            </h3>
            <div class="chart-controls">
              <div class="control-group">
                <label>类型</label>
                <select v-model="chartType" class="modern-select">
                  <option value="1">日线</option>
                  <option value="2">周线</option>
                  <option value="3">月线</option>
                </select>
              </div>
              <div class="control-group">
                <label>时间跨度</label>
                <input type="number" v-model="timeSpan" class="modern-input" placeholder="400" min="1" max="1000" />
              </div>
              <button @click="getStockQurve" class="fetch-btn">
                <i class="icon-refresh"></i>
                获取数据
              </button>
            </div>
          </div>
          <div class="card-content">
            <div v-if="loadingKline" class="loading-state">
              <div class="loading-spinner"></div>
              <p>K线图加载中...</p>
            </div>
            <div v-else class="chart-wrapper">
              <div id="kline-chart"></div>
            </div>
          </div>
        </div>

        <!-- 技术指标卡片 -->
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-indicator"></i>
              技术指标
            </h3>
            <div class="indicator-tabs">
              <button v-for="(name, key) in indicatorNameMap" :key="key" @click="selectIndicator(key)"
                :class="['indicator-tab', { active: indicatorType === key }]">
                {{ name }}
              </button>
            </div>
          </div>
          <div class="card-content">
            <div v-if="loadingIndicator" class="loading-state">
              <div class="loading-spinner"></div>
              <p>技术指标加载中...</p>
            </div>
            <div v-else class="chart-wrapper">
              <div id="indicator-chart"></div>
            </div>
          </div>
        </div>

        <!-- 估值比率图卡片 -->
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-valuation"></i>
              估值比率变化
            </h3>
          </div>
          <div class="card-content">
            <div v-if="loadingValuation" class="loading-state">
              <div class="loading-spinner"></div>
              <p>估值比率图加载中...</p>
            </div>
            <div v-else class="chart-wrapper">
              <div id="valuation-chart"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="info-panel">
        <!-- 智能预测分析卡片 -->
        <div class="info-card forecast-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-forecast"></i>
              智能预测分析
            </h3>
            <button v-if="!forecastVisible" @click="toggleForecast" class="analyze-btn">
              <i class="icon-ai"></i>
              开始分析
            </button>
          </div>

          <div v-if="forecastVisible" class="forecast-content">
            <!-- AI预测结果 -->
            <div class="prediction-section">
              <h4 class="section-title">Transformer预测结果</h4>
              <div class="prediction-cards">
                <div class="prediction-card primary">
                  <div class="prediction-icon">
                    <i class="icon-target"></i>
                  </div>
                  <div class="prediction-data">
                    <div class="prediction-value">{{ nextClose }}元</div>
                    <div class="prediction-label">预测收盘价</div>
                  </div>
                </div>
                <div class="prediction-card" :class="gainRate >= 0 ? 'positive' : 'negative'">
                  <div class="prediction-icon">
                    <i :class="gainRate >= 0 ? 'icon-trend-up' : 'icon-trend-down'"></i>
                  </div>
                  <div class="prediction-data">
                    <div class="prediction-value">
                      {{ gainRate >= 0 ? '+' : '' }}{{ gainRate }}%
                    </div>
                    <div class="prediction-label">预期收益率</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 风险评估 -->
            <div class="risk-section">
              <h4 class="section-title">风险评估</h4>
              <div class="risk-metrics">
                <!-- Z分模型 -->
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-name">Z分模型</span>
                    <span class="metric-score" :class="getZScoreClass(zScore)">{{ zScore }}</span>
                  </div>
                  <div class="metric-details">
                    <div class="detail-row" v-for="(value, index) in X" :key="index">
                      <span class="detail-label">{{ getZScoreLabel(index) }}</span>
                      <span class="detail-value">{{ value }}</span>
                    </div>
                  </div>
                </div>

                <!-- 夏普比率 -->
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-name">夏普比率</span>
                    <div class="sharpe-indicator" :class="getSharpeRatioClass">
                      <span class="sharpe-value">{{ sharpeRatio }}</span>
                    </div>
                  </div>
                  <div class="metric-description">
                    <p>衡量风险调整后收益的重要指标</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 预期收益率卡片 -->
        <div class="info-card rate-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="icon-rate"></i>
              预期收益率
            </h3>
          </div>
          <div class="card-content">
            <div v-if="loadingRate" class="loading-state">
              <div class="loading-spinner"></div>
              <p>收益率计算中...</p>
            </div>
            <div v-else class="rate-content">
              <div class="rate-grid">
                <div class="rate-item" v-for="(rate, period, index) in rateMap" :key="period">
                  <span class="rate-period">{{ period }}</span>
                  <span class="rate-value">{{ rate }}{{ index === Object.keys(rateMap).length - 1 ? '‰' : '%' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 财务指标独立模块 - 放在主要内容区域下方 -->
    <div class="financial-section">
      <div class="info-card financial-card-full">
        <div class="card-header">
          <h3 class="card-title">
            <i class="icon-financial"></i>
            财务指标详情
          </h3>
        </div>
        <div class="card-content">
          <div v-if="loadingFinancial" class="loading-state">
            <div class="loading-spinner"></div>
            <p>财务数据加载中...</p>
          </div>
          <div v-else class="financial-table-wrapper-full">
            <div class="table-container-full">
              <table class="modern-table-full">
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
                    <td>{{ formatNumber(financial.profit_dedt) }}</td>
                    <td :class="getChangeClass(financial.q_profit_yoy)">
                      {{ formatPercent(financial.q_profit_yoy) }}
                    </td>
                    <td :class="getChangeClass(financial.or_yoy)">
                      {{ formatPercent(financial.or_yoy) }}
                    </td>
                    <td>{{ formatNumber(financial.bps) }}</td>
                    <td>{{ formatNumber(financial.cfps) }}</td>
                    <td>{{ formatPercent(financial.roe) }}</td>
                    <td>{{ formatPercent(financial.ar_turn) }}</td>
                    <td>{{ formatPercent(financial.grossprofit_margin) }}</td>
                    <td>{{ formatNumber(financial.revenue) }}</td>
                    <td>{{ formatNumber(financial.n_income_attr_p) }}</td>
                    <td>{{ formatNumber(financial.basic_eps) }}</td>
                    <td>{{ formatNumber(financial.sell_exp) }}</td>
                    <td>{{ formatNumber(financial.admin_exp) }}</td>
                    <td>{{ formatNumber(financial.rd_exp) }}</td>
                    <td>{{ formatNumber(financial.fin_exp) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import '@/css/StockDetail.css';

export default {
  name: 'StockDetail',
  data() {
    return {
      stockCode: localStorage.getItem('stockCode') || '',
      stockName: localStorage.getItem('stockName') || '',
      stockIntroduction: '',

      // 新增：顶部股票统计数据（样例数据）
      currentPrice: 45.67,
      priceChange: 2.34,
      priceChangePercent: 5.41,
      openPrice: 43.89,
      volume: 1256.8, // 万手
      marketCap: 892.5, // 亿
      peRatio: 18.6,

      fetchStockData() {
        // 获取股票基础数据的方法
        console.log('Fetching stock data...');
      },

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
      loadingRate: false,

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
    selectIndicator(key) {
      this.indicatorType = key;
      this.updateIndicatorChart();
    },
    getZScoreClass(score) {
      if (score >= 3) return 'excellent';
      if (score >= 1.8) return 'good';
      if (score >= 1) return 'average';
      return 'poor';
    },
    getZScoreLabel(index) {
      const labels = [
        '流动资产占比',
        '保留盈余占比',
        '总利润占比',
        '市值占比',
        '营业收入占比'
      ];
      return labels[index] || `X${index + 1}`;
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
    getChangeClass(value) {
      if (value > 0) return 'positive';
      if (value < 0) return 'negative';
      return 'neutral';
    },
    formatNumber(value) {
      if (!value) return '--';
      return (value / 10000).toFixed(2);
    },
    formatPercent(value) {
      if (!value) return '--';
      return value.toFixed(2) + '%';
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
          console.log(response.data);
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
  async mounted() {
    await this.getIntroduction();
    await this.getStockQurve();
    await this.getTechnicalIndicator();
    await this.getFinancialMetric();
    await this.getValuationRatio();
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose();
    }
    if (this.indicatorChart) {
      this.indicatorChart.dispose();
    }
    if (this.valuationChart) {
      this.valuationChart.dispose();
    }
  }
};
</script>