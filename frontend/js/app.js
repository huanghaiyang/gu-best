import { createApp } from 'vue';
import Index from './index.vue';
import api from './api.js';

const app = createApp(Index);
app.config.globalProperties.$api = api;
app.mount('#app');