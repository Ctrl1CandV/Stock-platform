<template>
  <div class="ownership-page">
    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-container">
        <div id="assetDistributionChart" class="chart"></div>
      </div>
      <div class="chart-container">
        <div id="holdTimeChart" class="chart"></div>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <select v-model="searchType">
        <option value="code">股票代码</option>
        <option value="name">股票名称</option>
      </select>
      <input type="text" v-model="searchKeyword" placeholder="输入搜索关键词">
      <button @click="searchOwnerships">搜索</button>
    </div>

    <!-- 持有股列表 -->
    <div class="ownership-list">
      <div v-for="ownership in paginationOwnerships" :key="ownership.stock_code" class="ownership-item">
        <div class="ownership-info">
          <p v-if="ownership.stock_code">代码: {{ ownership.stock_code }}</p>
          <p v-if="ownership.stock_name">名称: {{ ownership.stock_name }}</p>
          <p v-if="ownership.hold_number">持有数量: {{ ownership.hold_number }}</p>
          <p v-if="ownership.purchase_per_price">购入价格: {{ ownership.purchase_per_price }}</p>
        </div>
        <div class="ownership-actions">
          <button @click="openSellModal(ownership)">卖出</button>
          <button @click="toStock(ownership)">详情</button>
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

    <!-- 卖出模态窗口 -->
    <div v-if="showSellModal" class="modal-mask">
      <div class="modal-content">
        <h3>{{ currentOwnership.stock_name }} ({{ currentOwnership.stock_code }})</h3>
        <p>当前持有: {{ currentOwnership.hold_number }} 股</p>
        <p>购入价格: {{ currentOwnership.purchase_per_price }} 元</p>
        <p>最新价格:{{ currentPrice }}</p>
        <input type="number" v-model.number="sellQuantity" placeholder="输入卖出数量" min="1"
          :max="currentOwnership.hold_number">
        <div class="modal-actions">
          <button @click="confirmSell">确认</button>
          <button @click="showSellModal = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'OwnershipPage',
  data() {
    return {
      searchType: 'code',
      searchKeyword: '',
      ownershipList: [],
      filteredOwnerships: [],
      assetDistributionMap: {},
      holdTimeList: [],
      showSellModal: false,
      currentOwnership: {},
      currentPrice: null,
      sellQuantity: 0,
      currentPage: 1,
      itemsPerPage: 12,
    };
  },
  mounted() {
    this.loadChartData();
    this.fetchOwnershipData();
  },
  computed: {
    paginationOwnerships() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      if (this.filteredOwnerships) {
        return this.filteredOwnerships.slice(start, end);
      } else {
        return this.ownershipList.slice(start, end);
      }
    },
    totalPages() {
      if (this.filteredOwnerships) {
        return Math.ceil(this.filteredOwnerships.length / this.itemsPerPage);
      } else {
        return Math.ceil(this.ownershipList.length / this.itemsPerPage);
      }
    }
  },
  methods: {
    async toStock(ownership) {
      // 更新数据
      try {
        const response = await this.$axios.post('/platform/updateAnnualDailyQuotes', { stockCode: ownership.stock_code });
        if (response.data.status === 'SUCCESS') {
          this.$router.push('/user/stock');
          localStorage.setItem('stockCode', ownership.stock_code);
          localStorage.setItem('stockName', ownership.stock_name);
        } else {
          alert('跳转失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    async loadChartData() {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        alert('无法获取用户ID，请重新登录');
        return;
      }

      try {
        const response = await this.$axios.get('/user/ownershipPageLoad', {
          params: { userID: userID }
        });

        if (response.data.status === 'SUCCESS') {
          this.assetDistributionMap = response.data.assetDistributionMap;
          this.holdTimeList = response.data.holdTimeList;

          // 开始初始化图表
          this.$nextTick(() => {
            this.initAssetDistributionChart();
            this.initHoldTimeChart();
          });
        } else {
          alert('获取数据失败:' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    initAssetDistributionChart() {
      const chartDom = document.getElementById('assetDistributionChart');
      if (!chartDom) return;
      this.assetDistributionChart = echarts.init(chartDom);

      // 进行图表前置的数据处理
      const data = [];
      let totalAsset = 0;
      for (const [key, value] of Object.entries(this.assetDistributionMap)) {
        totalAsset += value;
        data.push({ name: key, value: value });
      }

      const option = {
        title: {
          text: `资产分布 (总计: ${totalAsset.toFixed(2)}元)`,
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const percent = ((params.value / totalAsset) * 100).toFixed(2);
            return `${params.seriesName}<br/>${params.name}: ${params.value}元 (${percent}%)`;
          }
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'center',
          type: 'scroll',
          max: 10
        },
        series: [
          {
            name: '资产分布',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}: {d}%'
            },
            labelLine: {
              show: true
            },
            data: data
          }
        ]
      };

      this.assetDistributionChart.setOption(option);
      window.addEventListener('resize', () => {
        this.assetDistributionChart.resize();
      });
    },
    initHoldTimeChart() {
      const chartDom = document.getElementById('holdTimeChart');
      if (!chartDom) return;
      this.holdTimeChart = echarts.init(chartDom);

      const data = this.holdTimeList.map(item => {
        return [item[0], item[1]];
      })
      const option = {
        title: {
          text: '持有股票时间分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: function (params) {
            return '价格: ' + params.value[0] + ' 元<br/>持有时间: ' + params.value[1] + ' 小时';
          }
        },
        xAxis: {
          type: 'value',
          name: '价格 (元)',
          nameLocation: 'middle',
          nameGap: 30
        },
        yAxis: {
          type: 'value',
          name: '持有时间 (小时)',
          nameLocation: 'middle',
          nameGap: 30
        },
        series: [
          {
            type: 'scatter',
            symbolSize: function (data) {
              return Math.sqrt(data[1]) * 5 + 5;
            },
            data: data,
            itemStyle: {
              color: function (params) {
                const price = params.value[0];
                if (price < 10) return '#5470c6';
                if (price < 20) return '#91cc75';
                if (price < 30) return '#fac858';
                return '#ee6666';
              }
            }
          }
        ]
      };

      this.holdTimeChart.setOption(option);
      window.addEventListener('resize', () => {
        this.holdTimeChart.resize();
      });
    },
    async fetchOwnershipData() {
      try {
        const userID = localStorage.getItem('userID');
        const response = await this.$axios.get('/user/getStockOwnership', {
          params: { userID: userID }
        });

        if (response.data.status === 'SUCCESS') {
          this.ownershipList = response.data.stockOwnershipList;
          this.filteredOwnerships = this.ownershipList; // 初始时不进行过滤，显示全部
        } else {
          alert('获取持有股失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    },
    searchOwnerships() {
      if (!this.searchKeyword) {
        this.filteredOwnerships = this.ownershipList;
        return;
      }

      this.filteredOwnerships = this.ownershipList.filter(ownership => {
        if (this.searchType === 'code') {
          return ownership.stock_code.includes(this.searchKeyword);
        } else if (this.searchType === 'name') {
          return ownership.stock_name.includes(this.searchKeyword);
        }
      });
    },
    async openSellModal(ownership) {
      try {
        const response = await this.$axios.get('/platform/isTrading', {
          params: { stockCode: ownership.stock_code }
        });
        if (response.data.status === 'SUCCESS') {
          this.currentOwnership = ownership;
          this.currentPrice = response.data.perPrice;
          this.showSellModal = true;
        } else if (response.data.status === 'ERROR') {
          alert(response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async confirmSell() {
      if (this.sellQuantity <= 0 || this.sellQuantity > this.currentOwnership.hold_number) {
        alert('无效的卖出数量');
        return;
      }

      const userID = localStorage.getItem('userID');
      if (!userID) {
        alert('当前身份信息错误，无法卖出');
        return;
      }

      try {
        const response = await this.$axios.post('/platform/sellStock', {
          ownershipID: this.currentOwnership.ownership_id,
          sellNumber: this.sellQuantity
        });

        if (response.data.status === 'SUCCESS') {
          alert('卖出成功，卖出收益为 ' + response.data.gain);
          this.showSellModal = false;
          this.fetchOwnershipData(); // 更新持有股数据
        } else {
          alert('卖出失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    }
  }
};
</script>

<style scoped>
/* 样式基础 */
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

.ownership-page {
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.chart-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}

.chart {
  width: 100%;
  height: 400px;
}

/* 搜索区域样式 */
.search-section {
  display: flex;
  width: 80%;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
}

.search-section select {
  width: 20%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: border-color 0.3s;
}

.search-section select:focus {
  border-color: #409eff;
  outline: none;
}

.search-section input {
  width: 40%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: border-color 0.3s;
  margin-right: 0;
}

.search-section input:focus {
  border-color: #409eff;
  outline: none;
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

/* 持有股列表样式 */
.ownership-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.ownership-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.ownership-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.ownership-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.ownership-info p {
  width: 100%;
  font-size: 15px;
  color: #555;
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}

.ownership-info p:last-child {
  border-bottom: none;
}

.ownership-actions {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-top: 15px;
}

.ownership-actions button {
  flex: 1;
  padding: 10px 14px;
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(245, 108, 108, 0.3);
}

.ownership-actions button:hover {
  background-color: #e64242;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(245, 108, 108, 0.4);
}

.ownership-actions button:active {
  transform: translateY(0);
}

.ownership-actions button:last-child {
  background-color: #409eff;
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

.ownership-actions button:last-child:hover {
  background-color: #66b1ff;
  box-shadow: 0 5px 12px rgba(64, 158, 255, 0.4);
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

/* 卖出模态窗口 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.modal-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  width: 450px;
  max-width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content h3 {
  font-size: 20px;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
  font-weight: 600;
}

.modal-content p {
  font-size: 16px;
  margin-bottom: 15px;
  text-align: center;
  color: #555;
}

.modal-content input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 25px;
  transition: border-color 0.3s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.modal-content input:focus {
  border-color: #409eff;
  outline: none;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.modal-actions button {
  flex: 1;
  padding: 12px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s;
}

.modal-actions button:first-child {
  background-color: #67c23a;
  color: white;
  box-shadow: 0 3px 8px rgba(103, 194, 58, 0.3);
}

.modal-actions button:first-child:hover {
  background-color: #529b2e;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(103, 194, 58, 0.4);
}

.modal-actions button:first-child:active {
  transform: translateY(0);
}

.modal-actions button:last-child {
  background-color: #909399;
  color: white;
  box-shadow: 0 3px 8px rgba(144, 147, 153, 0.3);
}

.modal-actions button:last-child:hover {
  background-color: #606266;
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(144, 147, 153, 0.4);
}

.modal-actions button:last-child:active {
  transform: translateY(0);
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

  .ownership-list {
    grid-template-columns: 1fr;
  }

  .ownership-item {
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
  
  .modal-content {
    width: 90%;
    padding: 20px;
  }
}
</style>