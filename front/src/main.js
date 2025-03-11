import Vue from 'vue'
import App from './App.vue'
import router from "./router";
import axios from "axios";
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';

// 设置Axios全局默认配置
axios.defaults.baseURL = "http://localhost:8000";
axios.defaults.headers['Content-Type'] = 'application/json';
Vue.prototype.$axios = axios;
Vue.config.productionTip = false
Vue.use(ElementUI)

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
