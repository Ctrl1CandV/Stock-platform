import Vue from "vue";
import Router from  'vue-router';
import LoginPage from "@/components/LoginPage.vue";
import RegisterPage from "@/components/RegisterPage.vue";
import UserMain from "@/components/UserMain.vue";
import HomePage from "@/components/HomePage.vue";
import UserProfile from "@/components/UserProfile.vue";
import OwnershipSearch from "@/components/OwnershipSearch.vue";
import TransactionSearch from "@/components/TransactionSearch.vue";
import ManagerPage from "@/components/ManagerPage.vue";
import StockDetail from "@/components/StockDetail.vue";

Vue.use(Router);

export default new Router({
    mode: 'history',
    routes: [
        {
            path: '/login',
            name: 'Login',
            component: LoginPage,
        },
        {
            path: '/register',
            name: 'Register',
            component: RegisterPage,
        },
        {
            path: '/user',
            name: 'User',
            component: UserMain,
            children: [
                { path: '', component: HomePage },
                { path: 'profile', component: UserProfile },
                { path: 'ownership', component: OwnershipSearch },
                { path: 'transaction', component: TransactionSearch },
                { path: 'stock', component: StockDetail },
            ]
        },
        {
            path: '/manager',
            name: 'Manager',
            component: ManagerPage,
        },
        {
            path: '*',
            redirect: '/login',
        },
    ],
});