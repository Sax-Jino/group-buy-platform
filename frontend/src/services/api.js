import axios from 'axios';
import io from 'socket.io-client';

const API_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// 添加語言請求攔截器
api.interceptors.request.use(config => {
    const language = localStorage.getItem('language') || 'zh_TW';
    config.headers['Accept-Language'] = language;
    return config;
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('jwtToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const socket = io('http://localhost:5000/collaboration', {
    auth: {
        token: localStorage.getItem('jwtToken')
    }
});

socket.on('connect', () => {
    console.log('Connected to /collaboration');
});

socket.on('connect_error', (err) => {
    console.error('Socket error:', err);
});

export default api;