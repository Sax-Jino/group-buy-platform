import axios from 'axios';
import io from 'socket.io-client';

const API_URL = '/api';

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

export const socket = io('/socket.io', {
    path: '/socket.io',
    transports: ['websocket', 'polling'],
    auth: {
        token: localStorage.getItem('jwtToken')
    },
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 20000
});

socket.on('connect', () => {
    console.log('Connected to /collaboration');
});

socket.on('connect_error', (err) => {
    console.error('Socket error:', err);
});

export default api;