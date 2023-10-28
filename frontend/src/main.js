import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router' // Importe createRouter e createWebHistory
import Dashboard from './views/Dashboard.vue'
import FileList from './components/FileList.vue'
import LMap from './components/LMap.vue'
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';

const routes = [
  { path: '/', component: Dashboard},
  { path: '/lista', component: FileList },
  { path: '/map', component: LMap }
  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App)
  .use(router)
  .mount('#app')
