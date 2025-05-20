import 'element-ui/lib/theme-chalk/index.css';
import ElementUI from 'element-ui';
import Cookies from 'js-cookie';
import router from "./router";
import App from './App.vue';
import axios from "axios";
import Vue from 'vue'

function getCSRFToken() {
  return Cookies.get('csrftoken') || '';
}

const front_ip = process.env.VUE_APP_FRONT_IP;

// 设置Axios全局默认配置
axios.defaults.baseURL = `http://${front_ip}:8000`;
axios.defaults.headers['Content-Type'] = 'application/json';
Vue.prototype.$axios = axios;
axios.interceptors.request.use(
  config => {
    const token = getCSRFToken();
    if (token) {
      config.headers['X-CSRFToken'] = token;
    }
    config.withCredentials = true;
    return config;
  },
  error => Promise.reject(error)
);
Vue.config.productionTip = false
Vue.use(ElementUI)

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
