<template>
    <div class="watchlisted-container">
        <h1 class="page-title">我的自选股</h1>

        <div class="table-container" v-if="isLoading">
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>股票代码</th>
                        <th>股票名称</th>
                        <th>行业</th>
                        <th>地区</th>
                        <th>昨收价</th>
                        <th>当前价</th>
                        <th>最高价</th>
                        <th>最低价</th>
                        <th>涨跌幅</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="stock in favoriteStocksList" :key="stock.stock_code">
                        <td>{{ stock.stock_code }}</td>
                        <td>{{ stock.stock_name }}</td>
                        <td>{{ stock.industry }}</td>
                        <td>{{ stock.area }}</td>
                        <td>{{ stock.preClosePrice }}</td>
                        <td :class="getPriceClass(stock.currentPrice, stock.preClosePrice)">
                            {{ stock.currentPrice }}
                        </td>
                        <td>{{ stock.highPrice }}</td>
                        <td>{{ stock.lowPrice }}</td>
                        <td :class="getPriceClass(stock.currentPrice, stock.preClosePrice)">
                            {{ calculateChangePercent(stock.currentPrice, stock.preClosePrice) }}
                        </td>
                        <td>
                            <button class="action-btn" @click="toStock(stock)">查看详情</button>
                            <button class="action-btn remove-btn" @click="removeFromWatchlist(stock)">移除</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="empty-state" v-else>
            <p>您还没有添加任何自选股</p>
            <button class="add-btn" @click="goToMarket">去市场添加</button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'WatchlistedPage',
    data() {
        return {
            userID: localStorage.getItem('userID'),
            favoriteStocksList: [],
            isLoading: true,
        };
    },
    async mounted() {
        this.getFavoriteStocks();
    },
    methods: {
        async getFavoriteStocks() {
            this.isLoading = true;
            try {
                const response = await this.$axios.get('/user/getFavoriteStocksInformation', {
                    params: { userID: this.userID },
                });

                if (response.data.status === 'SUCCESS') {
                    if (response.data.favoriteStocksList.length === 0) {
                        this.isLoading = false;
                    }
                    this.favoriteStocksList = response.data.favoriteStocksList;
                } else {
                    alert('获取自选股信息失败: ' + response.data.errorMessage);
                }
            } catch (error) {
                alert('请求失败: ' + error.message);
                this.isLoading = false;
            }
        },
        getPriceClass(currentPrice, preClosePrice) {
            if (!currentPrice || !preClosePrice) return '';
            if (currentPrice > preClosePrice) return 'price-up';
            if (currentPrice < preClosePrice) return 'price-down';
            return '';
        },
        calculateChangePercent(currentPrice, preClosePrice) {
            if (!currentPrice || !preClosePrice) return '0.00%';
            const change = ((currentPrice - preClosePrice) / preClosePrice * 100).toFixed(2);
            return change > 0 ? `+${change}%` : `${change}%`;
        },
        viewStockDetail(stock) {
            this.$router.push({
                name: 'StockDetail',
                params: { stockCode: stock.stock_code }
            });
        },
        async removeFromWatchlist(stock) {
            try {
                const response = await this.$axios.post('/platform/removeFavoriteStock', {
                    userID: this.userID,
                    stockCode: stock.stock_code
                });

                if (response.data.status === 'SUCCESS') {
                    alert(stock.stock_name + "已从自选股中移除");
                    // 重新获取以刷新界面
                    await this.getFavoriteStocks();
                } else {
                    alert('移除自选股失败:' + response.data.errorMessage);
                }
            } catch (error) {
                alert('请求失败: ' + error.message);
            }
        },
        goToMarket() {
            this.$router.push('/user');
        },
        async toStock(stock) {
            try {
                console.log(stock.stock_code);
                const response = await this.$axios.post('/platform/updateAnnualDailyQuotes', { stockCode: stock.stock_code });
                if (response.data.status === 'SUCCESS') {
                    localStorage.setItem('stockCode', stock.stock_code);
                    localStorage.setItem('stockName', stock.stock_name);
                    this.$router.push('/user/stock');
                } else {
                    alert('跳转失败: ' + response.data.errorMessage);
                }
            } catch (error) {
                alert('请求失败: ' + error.message);
            }
        },
    },
}
</script>

<style scoped>
/* 基础样式 */
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

.watchlisted-container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 20px;
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.page-title {
    color: #333;
    margin-bottom: 30px;
    text-align: center;
    font-size: 28px;
    font-weight: 600;
    position: relative;
    padding-bottom: 15px;
}

.page-title:after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 3px;
    background: linear-gradient(to right, #409eff, #67c23a);
    border-radius: 3px;
}

/* 加载状态样式 */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 50px 0;
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #409eff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-container p {
    color: #606266;
    font-size: 16px;
}

/* 表格容器样式 */
.table-container {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: fadeIn 0.5s ease-out;
}

.table-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

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

/* 表格样式 */
.stock-table {
    width: 100%;
    border-collapse: collapse;
}

.stock-table th,
.stock-table td {
    padding: 15px;
    text-align: center;
    border-bottom: 1px solid #eee;
}

.stock-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #555;
    position: sticky;
    top: 0;
    z-index: 10;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stock-table tr {
    transition: background-color 0.2s ease;
}

.stock-table tr:hover {
    background-color: #f0f7ff;
}

.stock-table tr:last-child td {
    border-bottom: none;
}

/* 价格样式 */
.price-up {
    color: #f56c6c;
    font-weight: bold;
}

.price-down {
    color: #67c23a;
    font-weight: bold;
}

/* 按钮样式 */
.action-btn {
    background-color: #409eff;
    color: white;
    border: none;
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    margin-right: 8px;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 2px 5px rgba(64, 158, 255, 0.3);
}

.action-btn:hover {
    background-color: #66b1ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(64, 158, 255, 0.4);
}

.action-btn:active {
    transform: translateY(0);
}

.remove-btn {
    background-color: #f56c6c;
    box-shadow: 0 2px 5px rgba(245, 108, 108, 0.3);
}

.remove-btn:hover {
    background-color: #f78989;
    box-shadow: 0 4px 8px rgba(245, 108, 108, 0.4);
}

/* 空状态样式 */
.empty-state {
    text-align: center;
    padding: 60px 0;
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    animation: fadeIn 0.5s ease-out;
}

.empty-state p {
    color: #909399;
    margin-bottom: 25px;
    font-size: 18px;
}

.add-btn {
    background-color: #67c23a;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 3px 8px rgba(103, 194, 58, 0.3);
}

.add-btn:hover {
    background-color: #85ce61;
    transform: translateY(-2px);
    box-shadow: 0 5px 12px rgba(103, 194, 58, 0.4);
}

.add-btn:active {
    transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 1024px) {
    .stock-table {
        font-size: 14px;
    }
    
    .stock-table th,
    .stock-table td {
        padding: 12px 8px;
    }
}

@media (max-width: 768px) {
    .stock-table {
        font-size: 12px;
    }

    .stock-table th,
    .stock-table td {
        padding: 10px 5px;
    }

    .action-btn {
        padding: 6px 10px;
        font-size: 11px;
        margin-right: 4px;
    }
    
    .page-title {
        font-size: 24px;
    }
}

@media (max-width: 576px) {
    .watchlisted-container {
        padding: 15px 10px;
    }
    
    .stock-table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }
}
</style>