<template>
  <div class="transaction-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="icon-chart">📊</i>
        交易记录管理
      </h1>
      <p class="page-subtitle">查看您的交易历史和收益趋势</p>
    </div>

    <!-- 交易收益折线图 -->
    <div class="charts-section">
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">交易收益趋势</h3>
          <div class="chart-legend">
            <span class="legend-item profit">盈利</span>
            <span class="legend-item loss">亏损</span>
          </div>
        </div>
        <div id="transactionProfitChart" class="chart"></div>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-header">
        <h3 class="search-title">
          <i class="icon-search">🔍</i>
          筛选交易记录
        </h3>
      </div>
      <div class="search-controls">
        <div class="control-group search-type-group">
          <label class="control-label" style="color: black;">搜索类型</label>
          <div class="select-wrapper">
            <select v-model="searchType" class="search-select">
              <option value="type">交易类型</option>
              <option value="code">股票代码</option>
              <option value="name">股票名称</option>
            </select>
            <div class="select-arrow">▼</div>
          </div>
        </div>

        <div class="control-group" v-if="searchType !== 'type'">
          <label class="control-label" style="color: black;">关键词</label>
          <div class="input-wrapper">
            <input type="text" v-model="searchKeyword" placeholder="输入搜索关键词" class="search-input"
              @keyup.enter="searchTransactions" />
            <span class="input-icon" v-if="searchKeyword" @click="searchKeyword = ''">✕</span>
          </div>
        </div>

        <div class="control-group" v-else>
          <label class="control-label" style="color: black;">交易类型</label>
          <div class="select-wrapper">
            <select v-model="searchKeyword" class="search-select">
              <option value="">全部交易</option>
              <option value="0">买入交易</option>
              <option value="1">卖出交易</option>
            </select>
            <div class="select-arrow">▼</div>
          </div>
        </div>

        <div class="control-group button-group">
          <button @click="searchTransactions" class="search-btn">
            <i class="btn-icon">🔍</i>
            <span>搜索</span>
          </button>
          <button @click="resetSearch" class="reset-btn">
            <i class="btn-icon">🔄</i>
            <span>重置</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section" v-if="transactionList.length > 0">
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalTransactions }}</div>
          <div class="stat-label">总交易数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <div class="stat-value" :class="{ 'profit': totalProfit >= 0, 'loss': totalProfit < 0 }">
            {{ totalProfit >= 0 ? '+' : '' }}{{ totalProfit.toFixed(2) }}
          </div>
          <div class="stat-label">总收益(元)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ buyCount }}/{{ sellCount }}</div>
          <div class="stat-label">买入/卖出</div>
        </div>
      </div>
    </div>

    <!-- 交易记录列表 -->
    <div class="transaction-section">
      <div class="transaction-list" v-if="paginatedTransactions.length > 0">
        <div v-for="transaction in paginatedTransactions"
          :key="`${transaction.stock_code}_${transaction.transaction_type}_${transaction.transaction_date}`"
          class="transaction-item">
          <div class="transaction-header">
            <div class="transaction-type"
              :class="{ 'buy': transaction.transaction_type === 0, 'sell': transaction.transaction_type === 1 }">
              <i class="type-icon">{{ transaction.transaction_type === 0 ? '📈' : '📉' }}</i>
              {{ transaction.transaction_type === 0 ? '买入' : '卖出' }}
            </div>
            <div class="transaction-profit"
              :class="{ 'profit': transaction.gains >= 0, 'loss': transaction.gains < 0 }">
              {{ transaction.gains >= 0 ? '+' : '' }}{{ transaction.gains }} 元
            </div>
          </div>

          <div class="transaction-body">
            <div class="stock-info">
              <div class="stock-code">{{ transaction.stock_code }}</div>
              <div class="stock-name">{{ transaction.stock_name }}</div>
            </div>

            <div class="transaction-details">
              <div class="detail-row">
                <span class="detail-label">交易时间:</span>
                <span class="detail-value">{{ formatDate(transaction.transaction_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">交易数量:</span>
                <span class="detail-value">{{ transaction.transaction_number }} 股</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">交易单价:</span>
                <span class="detail-value">¥{{ transaction.per_price }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">交易金额:</span>
                <span class="detail-value total-amount">¥{{ (transaction.transaction_number *
                  transaction.per_price).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无交易记录</div>
        <div class="empty-subtext">请尝试调整搜索条件</div>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="currentPage === 1" @click="currentPage--" :class="{ 'disabled': currentPage === 1 }"
        class="pagination-btn prev-btn">
        <i class="btn-icon">⬅️</i>
        上一页
      </button>

      <div class="page-numbers">
        <button v-for="page in visiblePages" :key="page" @click="currentPage = page"
          :class="{ 'active': page === currentPage }" class="page-number">
          {{ page }}
        </button>
      </div>

      <button :disabled="currentPage === totalPages" @click="currentPage++"
        :class="{ 'disabled': currentPage === totalPages }" class="pagination-btn next-btn">
        下一页
        <i class="btn-icon">➡️</i>
      </button>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import '@/css/TransactionSearch.css';

export default {
  name: 'TransactionSearch',
  data() {
    return {
      searchType: 'type',
      searchKeyword: '',
      transactionList: [],
      filteredTransactions: [],
      transactionProfitList: [],
      currentPage: 1,
      itemsPerPage: 9, // 改为9个，3x3布局更美观
      profitChart: null,
      loading: false,
    };
  },
  async mounted() {
    this.loading = true;
    try {
      await Promise.all([
        this.fetchTransactionData(),
        this.loadChartData()
      ]);
    } finally {
      this.loading = false;
    }
  },
  computed: {
    paginatedTransactions() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      const transactions = this.filteredTransactions || this.transactionList;
      return transactions.slice(start, end);
    },
    totalPages() {
      const transactions = this.filteredTransactions || this.transactionList;
      return Math.ceil(transactions.length / this.itemsPerPage);
    },
    visiblePages() {
      const pages = [];
      const total = this.totalPages;
      const current = this.currentPage;

      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i);
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) pages.push(i);
          pages.push('...');
          pages.push(total);
        } else if (current >= total - 3) {
          pages.push(1);
          pages.push('...');
          for (let i = total - 4; i <= total; i++) pages.push(i);
        } else {
          pages.push(1);
          pages.push('...');
          for (let i = current - 1; i <= current + 1; i++) pages.push(i);
          pages.push('...');
          pages.push(total);
        }
      }
      return pages;
    },
    totalTransactions() {
      return this.transactionList.length;
    },
    totalProfit() {
      return this.transactionList.reduce((sum, transaction) => {
        return sum + (transaction.gains || 0);
      }, 0);
    },
    buyCount() {
      return this.transactionList.filter(t => t.transaction_type === 0).length;
    },
    sellCount() {
      return this.transactionList.filter(t => t.transaction_type === 1).length;
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    resetSearch() {
      this.searchType = 'type';
      this.searchKeyword = '';
      this.filteredTransactions = [...this.transactionList];
      this.currentPage = 1;
    },
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
        this.$message.error('请求失败: ' + error.message);
      }
    },
    initTransactionProfitChart() {
      const chartDom = document.getElementById('transactionProfitChart');
      if (!chartDom) return;

      // 销毁之前的图表实例
      if (this.profitChart) {
        this.profitChart.dispose();
      }

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
          text: '累计收益趋势',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold',
            color: '#333'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e6e6e6',
          borderWidth: 1,
          textStyle: {
            color: '#333'
          },
          formatter: function (params) {
            const param = params[0];
            const value = parseFloat(param.value);
            const color = value >= 0 ? '#f56c6c' : '#67c23a';
            return `
              <div style="padding: 8px;">
                <div style="margin-bottom: 4px; font-weight: bold;">${param.name}</div>
                <div style="color: ${color}; font-size: 14px;">
                  累计收益: ${value >= 0 ? '+' : ''}${value} 元
                </div>
              </div>
            `;
          }
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            rotate: 45,
            interval: 'auto',
            color: '#666'
          },
          axisLine: {
            lineStyle: {
              color: '#e6e6e6'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '累计收益(元)',
          nameTextStyle: {
            color: '#666'
          },
          axisLabel: {
            color: '#666',
            formatter: function (value) {
              return value >= 0 ? '+' + value : value;
            }
          },
          axisLine: {
            lineStyle: {
              color: '#e6e6e6'
            }
          },
          splitLine: {
            lineStyle: {
              color: '#f5f5f5'
            }
          }
        },
        series: [
          {
            name: '累计收益',
            type: 'line',
            data: profits,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: function (params) {
                return params.value >= 0 ? '#f56c6c' : '#67c23a';
              }
            },
            lineStyle: {
              width: 3,
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 1, y2: 0,
                colorStops: [
                  { offset: 0, color: '#67c23a' },
                  { offset: 1, color: '#f56c6c' }
                ]
              }
            },
            areaStyle: {
              opacity: 0.1,
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#f56c6c' },
                  { offset: 1, color: '#67c23a' }
                ]
              }
            },
            markLine: {
              silent: true,
              data: [
                {
                  yAxis: 0,
                  lineStyle: {
                    color: '#909399',
                    type: 'dashed',
                    width: 2
                  },
                  label: {
                    show: false
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
          top: '15%',
          containLabel: true
        },
        dataZoom: [
          {
            type: 'inside',
            start: Math.max(0, 100 - (dates.length > 30 ? 30 : dates.length) * 3),
            end: 100
          },
          {
            type: 'slider',
            start: Math.max(0, 100 - (dates.length > 30 ? 30 : dates.length) * 3),
            end: 100,
            height: 30
          }
        ]
      };

      this.profitChart.setOption(option);

      // 响应式处理
      const resizeHandler = () => {
        if (this.profitChart) {
          this.profitChart.resize();
        }
      };
      window.addEventListener('resize', resizeHandler);

      // 组件销毁时移除监听器
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', resizeHandler);
        if (this.profitChart) {
          this.profitChart.dispose();
        }
      });
    },
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
          this.transactionList = response.data.stockTransactionList.sort((a, b) => {
            return new Date(b.transaction_date) - new Date(a.transaction_date);
          });
          this.filteredTransactions = [...this.transactionList];
        } else {
          this.$message.error('获取交易记录失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        this.$message.error('请求失败: ' + error.message);
      }
    },
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
          return transaction.stock_code &&
            typeof transaction.stock_code === 'string' &&
            transaction.stock_code.toLowerCase().includes(keywordLower);
        } else if (this.searchType === 'name') {
          return transaction.stock_name &&
            typeof transaction.stock_name === 'string' &&
            transaction.stock_name.toLowerCase().includes(keywordLower);
        }
        return false;
      });
    },
  },
  beforeDestroy() {
    if (this.profitChart) {
      this.profitChart.dispose();
    }
  }
};
</script>