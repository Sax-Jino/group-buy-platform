import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/OrderPage.css';

const OrderPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await fetch('http://localhost:5000/api/orders/user', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const data = await response.json();
        setOrders(data);
      } catch (err) {
        console.error('Failed to fetch orders:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);

  return (
    <div className="order-page">
      <h2>我的訂單</h2>
      {loading ? (
        <LoadingSpinner />
      ) : orders.length === 0 ? (
        <p>您目前沒有訂單。</p>
      ) : (
        <div className="order-list">
          {orders.map((order) => (
            <div key={order.id} className="order-card">
              <h3>訂單 #{order.id}</h3>
              <p>商品ID: {order.product_id}</p>
              <p>數量: {order.quantity}</p>
              <p>總金額: NT$ {order.total_amount}</p>
              <p>狀態: {order.status}</p>
              <p>下單時間: {new Date(order.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrderPage;