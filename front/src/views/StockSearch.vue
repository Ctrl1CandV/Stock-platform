<template>
  <div class="stock-search-page">
    <!-- 搜索框和选择框 -->
    <div class="search-container">
      <input
          v-model="searchQuery"
          type="text"
          placeholder="请输入股票代码或名称"
          @keyup.enter="searchStocks"
      />
      <select v-model="searchType">
        <option value="code">股票代码</option>
        <option value="name">股票名称</option>
      </select>
      <button @click="searchStocks">搜索</button>
    </div>

    <!-- 股票列表 -->
    <div class="stock-list">
      <table v-if="stocks.length > 0">
        <thead>
        <tr>
          <th>股票代码</th>
          <th>股票名称</th>
          <th>所属行业</th>
          <th>地域</th>
          <th>上市日期</th>
          <th>操作</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="stock in stocks" :key="stock.stockCode">
          <td>{{ stock.stockCode }}</td>
          <td>{{ stock.stockName }}</td>
          <td>{{ stock.industry }}</td>
          <td>{{ stock.area }}</td>
          <td>{{ stock.listDate }}</td>
          <td>
            <button @click="router.push('/stock')">详情</button>
            <button @click="openBuyModal(stock)">买入</button>
          </td>
        </tr>
        </tbody>
      </table>
      <p v-else>暂无股票信息</p>
    </div>

    <!-- 买入弹窗 -->
    <div v-if="showBuyModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeBuyModal">&times;</span>
        <h2>买入股票</h2>
        <p>股票代码: {{ selectedStock.stockCode }}</p>
        <p>股票名称: {{ selectedStock.stockName }}</p>
        <p>最新价格: {{ latestPrice }}</p>
        <input v-model="buyQuantity" type="number" placeholder="请输入买入数量" />
        <button @click="confirmBuy">确认买入</button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore.ts';
import { ref } from "vue";
import { queryStockByName, queryStockByCode, buyStock, isTrading,  } from '../api/stock.ts'

interface Stock {
  stockCode: string;
  stockName: string;
  industry: string;
  area: string;
  listDate: string;
}

const authStore = useAuthStore();
const router = useRouter();
const searchQuery = ref('');
const searchType = ref('code');
const stocks = ref<Stock[]>([]);
const showBuyModal = ref(false);
const selectedStock = ref<Stock | null>(null);
const latestPrice = ref(0);
const buyQuantity = ref(0);

// 查询股票列表
const searchStocks = async () => {
  if (!searchQuery) {
    alert('输入不能为空');
    return null;
  }

  if (searchType === 'code'){
    const response = await queryStockByCode({stockCode: searchQuery});
    stocks.value = response.stockInformation;
  }else if (searchType === 'name'){
    const response = await queryStockByName({stockName: searchQuery});
    stocks.value = response.stockInformation;
  }
};

// 打开和关闭买入窗口
const openBuyModal = async ( stock: Stock ) => {
  const response = await isTrading(stock.stockCode);
  if (response){
    latestPrice.value = response.perPrice;
  }
  selectedStock.value = stock;
  showBuyModal.value = true;
};
const closeBuyModal = () => {
  showBuyModal.value = false;
  selectedStock.value = null;
  buyQuantity.value = 0;
};

// 买入股票
const confirmBuy = async () => {
  userID = authStore.user.user_id;
  if ( buyQuantity * latestPrice > authStore.user.user_balance ){
    alert('余额不足，无法买入');
    return null;
  }
  const response = await buyStock({ userID: userID, stockCode: selectedStock.stockCode, buyNumber: buyQuantity});
  if (response){
    closeBuyModal()
  }
};
</script>