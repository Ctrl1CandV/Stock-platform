<template>
  <div id="stock-details">
    <!-- 股票名称和代码及简介 -->
    <div class="stock-header">
      <h1>{{ stockName }} ({{ stockCode }})</h1>
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
      <img :src="klineImage" alt="K线图" />
    </div>

    <!-- 技术指标 -->
    <div class="indicator-section">
      <h2>技术指标</h2>
      <div class="indicators">
        <label for="indicator-type">选择技术指标：</label>
        <select v-model="indicatorType" id="indicator-type" @change="getTechnicalIndicator">
          <option value="MACDImage">MACD</option>
          <option value="KDJImage">KDJ</option>
          <option value="BOLLImage">BOLL</option>
          <option value="BIASImage">BIAS</option>
          <option value="RSIImage">RSI</option>
          <option value="WRImage">WR</option>
        </select>
      </div>
      <img :src="indicatorImages[indicatorType]" alt="技术指标图" />
    </div>

    <!-- 公司财务指标 -->
    <div class="financial-section">
      <h2>公司财务指标</h2>
      <table>
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
      <img :src="valuationImage" alt="估值比率变化图" />
    </div>

    <!-- 预测分析区域 -->
    <div class="forecast-section">
      <button @click="toggleForecast" v-if="!forecastVisible">点击预测分析</button>
      <div v-if="forecastVisible">
        <h2>预测分析内容</h2>

        <!-- Transformer预测结果 -->
        <div class="forecast-item">
          <h3>Transformer预测结果</h3>
          <p>预测下一个收盘价:{{ nextClose }} 元</p>
          <p>对应的收益率：{{ gainRate }}%</p>
        </div>

        <!-- Z分模型得分 -->
        <div class="forecast-item">
          <h3>Z分模型得分</h3>
          <p>总得分：{{ zScore }}</p>
          <ul>
            <li>X1（流动资产与流动负债之差占比）：{{ X[0] }}</li>
            <li>X2（保留盈余占比）：{{ X[1] }}</li>
            <li>X3（总利润占比）：{{ X[2] }}</li>
            <li>X4（市值占比）：{{ X[3] }}</li>
            <li>X5（营业收入占比）：{{ X[4] }}</li>
          </ul>
        </div>

        <!-- 夏普比率 -->
        <div class="forecast-item">
          <h3>夏普比率分析</h3>
          <p>夏普比率：{{ sharpeRatio }}</p>
        </div>

        <!-- 国债收益率 -->
        <div class="forecast-item">
          <h3>参考国债收益率</h3>
          <ul>
            <li v-for="(rate, period) in rateMap" :key="period">
              {{ period }}：{{ rate }}%
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockDetail',
  data() {
    return {
      // 股票基本信息
      stockCode: localStorage.getItem('stockCode') || '',
      stockName: localStorage.getItem('stockNode') || '',

      // 图表数据
      klineImage: '', // base64字符串，来自后端
      indicatorImages: {},
      valuationImage: '', // base64字符串，来自后端

      // 选择项
      chartType: '1', // 默认日线
      timeSpan: 400, // 默认400天
      indicatorType: 'MACDImage', // 默认MACD

      // 财务数据
      financialMetrics: [],

      // 预测分析显示状态
      forecastVisible: false,

      // 预测部分的数据
      nextClose: 0,
      gainRate: 0,
      zScore: 0,
      X: [],
      sharpeRatio: 0,
      rateMap: {},
    };
  },
  methods: {
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    async getStockQurve() {
      try{
        const response = await this.$axios.get('/platform/showStockQurve', {
          params: { stockCode: this.stockCode, timeSpan: this.timeSpan, type: this.chartType }
        });
        if (response.data.status === 'SUCCESS'){
          this.klineImage = 'data:image/png;base64,' + response.data.image;
          console.log('K线图获取成功');
        }else if (response.data.status === 'ERROR'){
          alert('K线图获取失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async getTechnicalIndicator() {
      try{
        const response = await this.$axios.get('/platform/showTechnicalIndicator', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS'){
          this.indicatorImages = response.data.indicatorCharts;
        }else if (response.data.status === 'ERROR'){
          alert('技术指标变化图获取失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async getFinancialMetric() {
      try{
        const response = await this.$axios.get('/platform/getFinancialMetric', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS'){
          this.financialMetrics = response.data.financialMetricMap;
        }else if (response.data.status === 'ERROR'){
          alert('财务数据获取失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async getValuationRatio() {
      try{
        const response = await this.$axios.get('/platform/showValuationRatio', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS'){
          this.valuationImage = 'data:image/png;base64,' + response.data.valuationRatioImage;
          console.log('股票估值比率变化图获取成功');
        }else if (response.data.status === 'ERROR'){
          alert('股票估值比率变化图获取失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    // 请求股票数据
    async fetchStockData() {
      this.getFinancialMetric();
      this.getStockQurve();
      this.getValuationRatio();
      this.getTechnicalIndicator();
    },
    // 切换预测分析显示状态
    async forecastStock() {
      try{
        const response = await this.$axios.get('/platform/analyse/forecastStock', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS'){
          this.nextClose = response.data.result;
          this.gainRate = response.data.gainRate;
          console.log('Transformer预测成功');
        }else if (response.data.status === 'ERROR'){
          alert('Transformer预测失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async getZScore() {
      try{
        const response = await this.$axios.get('/platform/analyse/showZScore', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS'){
          this.zScore = response.data.zScore;
          this.X = response.data.X;
          console.log('Z分模型得分计算成功');
        }else if (response.data.status === 'ERROR'){
          alert('Z分模型得分计算失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    async getSharpeRatio() {
      try{
        const response = await this.$axios.get('/platform/analyse/showSharpeRatio', {
          params: { stockCode: this.stockCode }
        });
        if (response.data.status === 'SUCCESS'){
          this.sharpeRatio = response.data.sharpeRatio;
          this.rateMap = response.data.rateMap;
          console.log('夏普比率计算成功');
        }else if (response.data.status === 'ERROR'){
          alert('夏普比率计算失败:' + response.data.errorMessage);
        }
      }catch (error) {
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
  }
};
</script>

<style scoped>
#stock-details {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: 'Segoe UI', system-ui, sans-serif;
  color: #2c3e50;
}

/* 通用样式 */
h1, h2, h3 {
  color: #1a237e;
  margin: 1.2em 0 0.8em;
}

h1 {
  font-size: 2.2rem;
  border-bottom: 2px solid #e8eaf6;
  padding-bottom: 0.5em;
}

button {
  background: #3f51b5;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

button:hover {
  background: #283593;
  transform: translateY(-1px);
}

select, input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin: 0 8px;
}

/* 卡片式布局 */
.chart-section,
.indicator-section,
.financial-section,
.valuation-section,
.forecast-section > div {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 24px;
}

/* K线图区域 */
.chart-options {
  display: flex;
  gap: 16px;
  align-items: center;
  margin: 16px 0;
}

/* 技术指标 */
.indicators {
  margin: 16px 0;
}

/* 财务表格 */
.financial-section {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
  min-width: 1000px;
}

th, td {
  padding: 12px;
  text-align: right;
  border-bottom: 1px solid #eee;
  font-size: 0.9em;
}

th {
  background: #f5f5f5;
  font-weight: 500;
}

tr:hover td {
  background-color: #f8f9fa;
}

/* 预测分析 */
.forecast-item {
  background: #f8f9ff;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
}

.forecast-item h3 {
  color: #3f51b5;
  margin-top: 0;
}

ul {
  padding-left: 24px;
  color: #666;
}

/* 图片样式 */
img {
  width: 100%;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-options {
    flex-wrap: wrap;
  }

  button, select, input {
    margin: 4px;
    width: 100%;
  }

  h1 {
    font-size: 1.8rem;
  }

  .financial-section {
    padding: 10px;
  }
}
</style>
