<template>
  <div class="transaction-page">
    <!-- 交易收益折线图 -->
    <div class="charts-section">
      <div class="chart-container">
        <div id="transactionProfitChart" class="chart"></div>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <select v-model="searchType">
        <option value="type">交易类型</option>
        <option value="code">股票代码</option>
        <option value="name">股票名称</option>
      </select>
      <input v-if="searchType !== 'type'" type="text" v-model="searchKeyword" placeholder="输入搜索关键词" />
      <select v-else v-model="searchKeyword">
        <option value="">全部</option>
        <option value="0">买入</option>
        <option value="1">卖出</option>
      </select>
      <button @click="searchTransactions">搜索</button>
    </div>

    <!-- 交易记录列表 -->
    <div class="transaction-list">
      <div v-for="transaction in paginatedTransactions"
        :key="`${transaction.stock_code}_${transaction.transaction_type}_${transaction.transaction_date}`"
        class="transaction-item">
        <div class="transaction-info">
          <p>交易类型: {{ transaction.transaction_type === 0 ? '买入' : '卖出' }}</p>
          <p>股票代码: {{ transaction.stock_code }} 股票名称: {{ transaction.stock_name }}</p>
          <p>交易时间: {{ transaction.transaction_date }}</p>
          <p>交易数量: {{ transaction.transaction_number }} 交易单价: {{ transaction.per_price }} 元</p>
          <p :style="`color: ${transaction.gains >= 0 ? 'red' : 'green'}`">
            收益: {{ transaction.gains }} 元
          </p>
        </div>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="currentPage === 1" @click="currentPage--"
        :class="{ 'disabled': currentPage === 1 }">上一页</button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage === totalPages" @click="currentPage++"
        :class="{ 'disabled': currentPage === totalPages }">下一页</button>
    </div>

  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'TransactionPage',
  data() {
    return {
      searchType: 'type',
      searchKeyword: '',
      transactionList: [],
      filteredTransactions: [],
      transactionProfitList: [],
      currentPage: 1,
      itemsPerPage: 12,
      profitChart: null,
    };
  },
  async mounted() {
    await this.fetchTransactionData();
    await this.loadChartData();
  },
  computed: {
    paginatedTransactions() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      if (this.filteredTransactions) {
        return this.filteredTransactions.slice(start, end);
      } else {
        return this.transactionList.slice(start, end);
      }
    },
    totalPages() {
      if (this.filteredTransactions) {
        return Math.ceil(this.filteredTransactions.length / this.itemsPerPage);
      } else {
        return Math.ceil(this.transactionList.length / this.itemsPerPage);
      }
    },
  },
  methods: {
    async loadChartData() {
      const userID = localStorage.getItem('userID');
      try {
        const response = await this.$axios.get('/user/transactionPageLoad', {
          params: { userID: userID },
        });

        if (response.data.status === 'SUCCESS') {
          this.transactionProfitList = response.data.transactionProfitList;
          this.$nextTick(() => {
            this.initTransactionProfitChart();
          });
        } else {
          this.$message.error('获取图表数据失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    initTransactionProfitChart() {
      const chartDom = document.getElementById('transactionProfitChart');
      if (!chartDom) return;
      this.profitChart = echarts.init(chartDom);

      const dates = [];
      const profits = [];
      let cumulativeProfit = 0;
      this.transactionProfitList.forEach(item => {
        const dateStr = item[0];
        const profit = item[1];

        cumulativeProfit += profit;
        dates.push(dateStr);
        profits.push(cumulativeProfit.toFixed(2));
      });

      const option = {
        title: {
          text: '交易收益变化趋势',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function (params) {
            const param = params[0];
            return `日期: ${param.name}<br/>累计收益: ${param.value} 元`;
          }
        },
        xAxis: {
          type: 'category',
          data: dates,
          name: '日期',
          nameLocation: 'middle',
          nameGap: 30,
          axisLabel: {
            rotate: 45,
            interval: 'auto'
          }
        },
        yAxis: {
          type: 'value',
          name: '累计收益(元)',
          nameLocation: 'middle',
          nameGap: 30
        },
        series: [
          {
            name: '累计收益',
            type: 'line',
            data: profits,
            itemStyle: {
              color: function (params) {
                return params.value >= 0 ? '#c23531' : '#2f4554';
              }
            },
            lineStyle: {
              width: 2
            },
            areaStyle: {
              opacity: 0.2
            },
            markLine: {
              data: [
                {
                  yAxis: 0,
                  lineStyle: {
                    color: '#000',
                    type: 'dashed'
                  }
                }
              ]
            }
          }
        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
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
        ]
      };

      this.profitChart.setOption(option);
      window.addEventListener('resize', () => {
        this.profitChart.resize();
      });
    },
    // 获取交易记录数据
    async fetchTransactionData() {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        this.$message.error('无法获取用户ID，请重新登录');
        return;
      }

      try {
        const response = await this.$axios.get('/user/getTransactionRecords', {
          params: { userID: userID },
        });

        if (response.data.status === 'SUCCESS') {
          this.transactionList = response.data.stockTransactionList;
          this.filteredTransactions = this.transactionList; // 初始显示全部数据
        } else {
          this.$message.error('获取交易记录失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },

    // 根据搜索条件过滤交易记录
    searchTransactions() {
      this.currentPage = 1;
      if (this.searchKeyword === '') {
        this.filteredTransactions = [...this.transactionList]; 
        return;
      }
      const keywordLower = this.searchKeyword.toLowerCase();

      this.filteredTransactions = this.transactionList.filter((transaction) => {
        if (this.searchType === 'type') {
          return transaction.transaction_type.toString() === this.searchKeyword;
        } else if (this.searchType === 'code') {
          return transaction.stock_code && typeof transaction.stock_code === 'string' &&
            transaction.stock_code.toLowerCase().includes(keywordLower);
        } else if (this.searchType === 'name') {
          return transaction.stock_name && typeof transaction.stock_name === 'string' &&
            transaction.stock_name.toLowerCase().includes(keywordLower);
        }
        return false;
      });
    },
  },
};
</script>

<style scoped>
/* 页面基础样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

.transaction-page {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 图表区域样式 */
.charts-section {
  display: flex;
  flex-wrap: wrap;
  gap: 25px;
  margin-bottom: 35px;
}

.chart-container {
  flex: 1;
  min-width: 300px;
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.chart-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.chart {
  width: 100%;
  height: 400px;
}

/* 搜索区域样式 */
.search-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
  width: 80%;
}

.search-section select,
.search-section input {
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: border-color 0.3s;
}

.search-section select:focus,
.search-section input:focus {
  border-color: #409eff;
  outline: none;
}

.search-section select {
  width: 20%;
}

.search-section input {
  width: 40%;
}

.search-section button {
  padding: 12px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

.search-section button:hover {
  background-color: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(64, 158, 255, 0.4);
}

.search-section button:active {
  transform: translateY(0);
}

/* 交易记录列表样式 */
.transaction-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.transaction-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.transaction-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.transaction-info p {
  margin: 8px 0;
  font-size: 15px;
  color: #555;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}

.transaction-info p:last-child {
  border-bottom: none;
  font-weight: 600;
  font-size: 16px;
}

/* 分页控件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  gap: 20px;
}

.pagination button {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

.pagination button:hover:not(.disabled) {
  background-color: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(64, 158, 255, 0.4);
}

.pagination button:active:not(.disabled) {
  transform: translateY(0);
}

.pagination button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  box-shadow: none;
}

.page-info {
  font-size: 16px;
  font-weight: bold;
  color: #555;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }

  .search-section select,
  .search-section input,
  .search-section button {
    width: 100%;
    margin-bottom: 10px;
  }

  .transaction-list {
    grid-template-columns: 1fr;
  }

  .transaction-item {
    padding: 15px;
  }

  .charts-section {
    flex-direction: column;
  }

  .chart-container {
    width: 100%;
  }

  .chart {
    height: 300px;
  }
}

/* 自定义动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.transaction-item {
  animation: fadeIn 0.3s ease-out;
}
</style>