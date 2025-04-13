import React, { useEffect } from 'react';
import { notification } from 'antd';
import { socket } from '../services/api';

const NotificationHandler = () => {
    useEffect(() => {
        socket.on('frontend_notification', (data) => {
            notification.info({
                message: '團購更新',
                description: data.message,
                placement: 'topRight',
            });
            console.log('Notification:', data);
        });

        socket.on('vote_cast', (data) => {
            notification.info({
                message: '新投票',
                description: `用戶 ${data.user_id} 在小組 ${data.group_id} 投了 ${data.proposal_option}`,
                placement: 'topRight',
            });
        });

        socket.on('proposal_status_updated', (data) => {
            notification.info({
                message: '提案狀態更新',
                description: `提案 ${data.proposal_id} 現為 ${data.status}`,
                placement: 'topRight',
            });
        });

        return () => {
            socket.off('frontend_notification');
            socket.off('vote_cast');
            socket.off('proposal_status_updated');
        };
    }, []);

    return null;
};

export default NotificationHandler;