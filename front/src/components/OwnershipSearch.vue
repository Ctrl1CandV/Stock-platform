<template>
  <div class="ownership-page">
    <!-- 页面标题 -->
    <h1 class="page-title">我的持仓</h1>
    
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
      <input 
        type="text" 
        v-model="searchKeyword" 
        placeholder="请输入搜索关键词..."
        @keyup.enter="searchOwnerships"
      >
      <button @click="searchOwnerships">搜索</button>
    </div>

    <!-- 持有股列表 -->
    <div class="ownership-list">
      <div v-for="ownership in paginationOwnerships" :key="ownership.stock_code" class="ownership-item">
        <div class="ownership-info">
          <p v-if="ownership.stock_code">
            <span>股票代码</span>
            <strong>{{ ownership.stock_code }}</strong>
          </p>
          <p v-if="ownership.stock_name">
            <span>股票名称</span>
            <strong>{{ ownership.stock_name }}</strong>
          </p>
          <p v-if="ownership.hold_number">
            <span>持有数量</span>
            <strong>{{ ownership.hold_number }} 股</strong>
          </p>
          <p v-if="ownership.purchase_per_price">
            <span>购入价格</span>
            <strong>¥{{ ownership.purchase_per_price }}</strong>
          </p>
        </div>
        <div class="ownership-actions">
          <button @click="openSellModal(ownership)">卖出</button>
          <button @click="toStock(ownership)">详情</button>
        </div>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        :disabled="currentPage === 1" 
        @click="currentPage--"
        :class="{ 'disabled': currentPage === 1 }"
      >
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button 
        :disabled="currentPage === totalPages" 
        @click="currentPage++"
        :class="{ 'disabled': currentPage === totalPages }"
      >
        下一页
      </button>
    </div>

    <!-- 卖出模态窗口 -->
    <div v-if="showSellModal" class="modal-mask" @click.self="showSellModal = false">
      <div class="modal-content">
        <h3>{{ currentOwnership.stock_name }} ({{ currentOwnership.stock_code }})</h3>
        <p><strong>当前持有:</strong> {{ currentOwnership.hold_number }} 股</p>
        <p><strong>购入价格:</strong> ¥{{ currentOwnership.purchase_per_price }}</p>
        <p><strong>最新价格:</strong> ¥{{ currentPrice }}</p>
        <input 
          type="number" 
          v-model.number="sellQuantity" 
          placeholder="请输入卖出数量" 
          min="1"
          :max="currentOwnership.hold_number"
        >
        <div class="modal-actions">
          <button @click="confirmSell">确认卖出</button>
          <button @click="showSellModal = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import '@/css/OwnershipSearch.css';

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
          this.$message.error('跳转失败: ' + response.data.errorMessage);
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
          this.$message.error('获取数据失败:' + response.data.errorMessage);
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
          this.filteredOwnerships = this.ownershipList;
        } else {
          this.$message.error('获取持有股失败: ' + response.data.errorMessage);
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
          this.$message.error(response.data.errorMessage);
        }
      } catch (error) {
        alert(error.message);
      }
    },
    async confirmSell() {
      const userID = localStorage.getItem('userID');
      if (!userID) {
        this.$message.warning('当前身份信息错误，无法卖出');
        return;
      }

      if (this.sellQuantity <= 0 || this.sellQuantity > this.currentOwnership.hold_number) {
        this.$message.warning('无效的卖出数量');
        return;
      }

      try {
        await this.$confirm(
          `确认卖出该股${this.sellQuantity}支吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        );
      } catch { return null; }

      try {
        const response = await this.$axios.post('/platform/sellStock', {
          ownershipID: this.currentOwnership.ownership_id,
          sellNumber: this.sellQuantity
        });

        if (response.data.status === 'SUCCESS') {
          this.$message.success('卖出成功，卖出收益为 ' + response.data.gain);
          this.showSellModal = false;
          this.fetchOwnershipData(); // 更新持有股数据
        } else {
          this.$message.error('卖出失败: ' + response.data.errorMessage);
        }
      } catch (error) {
        alert('请求失败: ' + error.message);
      }
    }
  }
};
</script>