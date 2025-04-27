import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { Badge, notification, Drawer, List, Button } from 'antd';
import { BellOutlined } from '@ant-design/icons';
import { socket } from '../services/api';
import { setNotification } from '../store/actions/collaborationActions';
import '../styles/NotificationHandler.css';

const NotificationHandler = () => {
    const dispatch = useDispatch();
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isDrawerVisible, setIsDrawerVisible] = useState(false);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const fetchNotifications = async (page = 1) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(
                `http://localhost:5000/api/notifications?page=${page}`, 
                {
                    headers: { 'Authorization': `Bearer ${token}` }
                }
            );
            const data = await response.json();
            
            if (page === 1) {
                setNotifications(data.notifications);
            } else {
                setNotifications(prev => [...prev, ...data.notifications]);
            }
            
            setUnreadCount(data.notifications.filter(n => !n.is_read).length);
            setTotalPages(data.pages);
            setCurrentPage(data.current_page);
        } catch (error) {
            console.error('Failed to fetch notifications:', error);
        }
    };

    const handleNotificationClick = async (notificationId, relatedId, type) => {
        try {
            const token = localStorage.getItem('token');
            await fetch(
                `http://localhost:5000/api/notifications/${notificationId}/read`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            setNotifications(prev =>
                prev.map(n =>
                    n.id === notificationId ? { ...n, is_read: true } : n
                )
            );
            setUnreadCount(prev => Math.max(0, prev - 1));

            // 根據通知類型導航到相應頁面
            switch (type) {
                case 'order_status':
                case 'shipment_update':
                    window.location.href = `/orders/${relatedId}`;
                    break;
                case 'review_reminder':
                    window.location.href = `/orders/${relatedId}?review=true`;
                    break;
                default:
                    break;
            }
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    };

    const markAllAsRead = async () => {
        try {
            const token = localStorage.getItem('token');
            await fetch(
                'http://localhost:5000/api/notifications/read-all',
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            setNotifications(prev =>
                prev.map(n => ({ ...n, is_read: true }))
            );
            setUnreadCount(0);
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
        }
    };

    const loadMore = () => {
        if (currentPage < totalPages) {
            fetchNotifications(currentPage + 1);
        }
    };

    useEffect(() => {
        fetchNotifications();

        socket.on('frontend_notification', (data) => {
            notification.info({
                message: '新通知',
                description: data.message,
                placement: 'topRight',
            });
            
            setNotifications(prev => [data, ...prev]);
            setUnreadCount(prev => prev + 1);
            dispatch(setNotification(data));
        });

        return () => {
            socket.off('frontend_notification');
        };
    }, [dispatch]);

    return (
        <>
            <Badge count={unreadCount} onClick={() => setIsDrawerVisible(true)} className="notification-badge">
                <BellOutlined className="notification-icon" />
            </Badge>

            <Drawer
                title="通知中心"
                placement="right"
                onClose={() => setIsDrawerVisible(false)}
                open={isDrawerVisible}
                extra={
                    <Button onClick={markAllAsRead} disabled={unreadCount === 0}>
                        全部標為已讀
                    </Button>
                }
            >
                <List
                    dataSource={notifications}
                    renderItem={item => (
                        <List.Item 
                            className={`notification-item ${!item.is_read ? 'unread' : ''}`}
                            onClick={() => handleNotificationClick(item.id, item.related_id, item.type)}
                        >
                            <List.Item.Meta
                                title={item.type === 'order_status' ? '訂單狀態更新' : 
                                       item.type === 'shipment_update' ? '出貨通知' :
                                       item.type === 'review_reminder' ? '評價提醒' : '系統通知'}
                                description={item.message}
                            />
                            <div className="notification-time">
                                {new Date(item.created_at).toLocaleString()}
                            </div>
                        </List.Item>
                    )}
                    loadMore={
                        currentPage < totalPages && (
                            <div className="load-more">
                                <Button onClick={loadMore} loading={loading}>
                                    載入更多
                                </Button>
                            </div>
                        )
                    }
                />
            </Drawer>
        </>
    );
};

export default NotificationHandler;