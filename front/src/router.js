import Vue from "vue";
import Router from  'vue-router';
import LoginPage from "@/components/LoginPage.vue";
import UserMain from "@/components/UserMain.vue";
import HomePage from "@/components/HomePage.vue";
import UserProfile from "@/components/UserProfile.vue";
import OwnershipSearch from "@/components/OwnershipSearch.vue";
import TransactionSearch from "@/components/TransactionSearch.vue";
import ManagerPage from "@/components/ManagerPage.vue";
import StockDetail from "@/components/StockDetail.vue";
import WatchlistedPage from "@/components/WatchlistedPage.vue";
import UserManagement from "@/components/UserManagement.vue";
import ModelDialogue from "./components/ModelDialogue.vue";

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
            path: '/user',
            name: 'User',
            component: UserMain,
            children: [
                { path: '', component: HomePage },
                { path: 'profile', component: UserProfile },
                { path: 'ownership', component: OwnershipSearch },
                { path: 'transaction', component: TransactionSearch },
                { path: 'watchlist', component: WatchlistedPage },
                { path:'dialogue', component: ModelDialogue },
                { path: 'stock', component: StockDetail },
            ]
        },
        {
            path: '/manager',
            name: 'Manager',
            component: ManagerPage,
            children: [
                { path: '', component: UserManagement },
                { path: 'search', component: HomePage },
                { path:'stock', component: StockDetail },
            ]
        },
        {
            path: '*',
            redirect: '/login',
        },
    ],
});