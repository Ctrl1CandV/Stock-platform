<template>
  <div id="stock-details">
    <!-- 股票名称和代码及简介 -->
    <div class="stock-header">
      <h1>{{ stockName }} ({{ stockCode }})</h1>
      <p>{{ stockDescription }}</p>
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
        <select v-model="indicatorType" id="indicator-type">
          <option value="macd">MACD</option>
          <option value="kdj">KDJ</option>
          <option value="boll">BOLL</option>
          <option value="bias">BIAS</option>
          <option value="rsi">RSI</option>
          <option value="wr">WR</option>
        </select>
      </div>
      <img :src="indicatorImages" alt="技术指标图" />
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
      <img :src="valuationImages" alt="估值比率变化图" />
    </div>

    <!-- 预测分析区域 -->
    <div class="forecast-section">
      <button @click="toggleForecast" v-if="!forecastVisible">点击预测分析</button>
      <div v-if="forecastVisible">
        <h2>预测分析内容</h2>
        <p>这里展示预测分析的内容...</p>
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
      stockDescription: '',

      // 图表数据
      klineImage: '', // base64字符串，来自后端
      indicatorImages: {}, // base64字符串，来自后端
      valuationImage: '', // base64字符串，来自后端

      // 选择项
      chartType: '1', // 默认日线
      timeSpan: 400, // 默认400天
      indicatorType: 'macd', // 默认MACD

      // 财务数据
      financialMetrics: [],

      // 预测分析显示状态
      forecastVisible: false,
    };
  },
  methods: {
    async getStockQurve() {
      try{
        const response = await this.$axios.get('/platform/StockQurve', {
          params: { stockCode: this.stockCode, timeSpan: this.timeSpan, type: this.chartType }
        });
        if (response.data.status === 'SUCCESS'){
          this.klineImage = response.data.image;
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
          this.indicatorImages = response.data.charts;
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
          this.valuationImage = response.data.image;
        }else if (response.data.status === 'ERROR'){
          alert('股票估值比率变化图获取失败:' + response.data.errorMessage);
        }
      }catch (error) {
        alert(error.message);
      }
    },
    // 请求股票数据
    async fetchStockData() {
      this.stockDescription = "股票简介"; // 示例填充

      this.getStockQurve();
      this.getTechnicalIndicator();
      this.getFinancialMetric();
      this.getValuationRatio();
    },
    // 切换预测分析显示状态
    toggleForecast() {
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
  padding: 20px;
}

.stock-header {
  text-align: center;
  margin-bottom: 20px;
}

.chart-section,
.indicator-section,
.financial-section,
.valuation-section {
  margin-bottom: 20px;
}

.chart-options,
.valuation-options {
  margin: 10px 0;
}

button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>
