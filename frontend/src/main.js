import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router' // Importe createRouter e createWebHistory

import DashboardVue from './views/Dashboard.vue'
import FileList from './components/FileList.vue'

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';

const routes = [
  { path: '/', component: DashboardVue },
  { path: '/lista', component: FileList },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App)
  .use(router)
  .mount('#app')
