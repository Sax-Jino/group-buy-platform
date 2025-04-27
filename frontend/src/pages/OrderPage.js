import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import TrackingDialog from '../components/TrackingDialog';
import '../styles/OrderPage.css';

const OrderPage = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date_desc');
  const [products, setProducts] = useState({});
  const [selectedOrderId, setSelectedOrderId] = useState(null);

  // 訂單狀態對應的中文說明
  const statusMap = {
    pending: '待付款',
    paid: '已付款',
    shipped: '已出貨',
    completed: '已完成',
    cancelled: '已取消'
  };

  useEffect(() => {
    const fetchOrders = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      try {
        const response = await fetch('http://localhost:5000/api/orders/user', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch orders');
        }
        const data = await response.json();
        setOrders(data);

        // 獲取所有訂單相關的商品資訊
        const productIds = [...new Set(data.map(order => order.product_id))];
        const productPromises = productIds.map(id =>
          fetch(`http://localhost:5000/api/products/${id}`).then(res => res.json())
        );
        const productData = await Promise.all(productPromises);
        const productMap = {};
        productData.forEach(product => {
          productMap[product.id] = product;
        });
        setProducts(productMap);
      } catch (err) {
        console.error('Failed to fetch orders:', err);
        setError('載入訂單失敗');
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, [navigate]);

  const getFilteredOrders = () => {
    let filtered = [...orders];
    if (filter !== 'all') {
      filtered = filtered.filter(order => order.status === filter);
    }
    
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date_desc':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'date_asc':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'price_desc':
          return b.total_price - a.total_price;
        case 'price_asc':
          return a.total_price - b.total_price;
        default:
          return 0;
      }
    });
    
    return filtered;
  };

  const handlePayment = (orderId) => {
    navigate(`/orders/${orderId}/payment`);
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'paid':
        return 'status-paid';
      case 'shipped':
        return 'status-shipped';
      case 'completed':
        return 'status-completed';
      case 'cancelled':
        return 'status-cancelled';
      default:
        return '';
    }
  };

  const handleTrackingClick = (orderId) => {
    setSelectedOrderId(orderId);
  };

  const handleCloseTracking = () => {
    setSelectedOrderId(null);
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="order-page">
      <h2>我的訂單</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="order-filters">
        <div className="filter-group">
          <label>訂單狀態：</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">全部</option>
            <option value="pending">待付款</option>
            <option value="paid">已付款</option>
            <option value="shipped">已出貨</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>排序方式：</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="date_desc">最新訂單</option>
            <option value="date_asc">最舊訂單</option>
            <option value="price_desc">金額高到低</option>
            <option value="price_asc">金額低到高</option>
          </select>
        </div>
      </div>

      {getFilteredOrders().length === 0 ? (
        <div className="empty-message">
          <p>沒有符合條件的訂單</p>
          <button onClick={() => navigate('/products')}>去購物</button>
        </div>
      ) : (
        <div className="order-list">
          {getFilteredOrders().map((order) => {
            const product = products[order.product_id];
            return (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <h3>訂單 #{order.id}</h3>
                  <span className={`order-status ${getStatusClass(order.status)}`}>
                    {statusMap[order.status]}
                  </span>
                </div>

                <div className="order-content">
                  <div className="product-info">
                    <img 
                      src={product?.image_url || '/placeholder.jpg'} 
                      alt={product?.name} 
                    />
                    <div className="product-details">
                      <h4>{product?.name}</h4>
                      <p>數量：{order.quantity}</p>
                      <p className="price">單價：NT$ {product?.price}</p>
                    </div>
                  </div>

                  <div className="order-details">
                    <p>總金額：<span className="total-price">NT$ {order.total_price}</span></p>
                    <p>下單時間：{new Date(order.created_at).toLocaleString()}</p>
                    {order.payment_deadline && (
                      <p className="payment-deadline">
                        付款期限：{new Date(order.payment_deadline).toLocaleString()}
                      </p>
                    )}
                    {order.tracking_number && (
                      <p>物流單號：{order.tracking_number}</p>
                    )}
                  </div>

                  <div className="order-actions">
                    {order.status === 'pending' && (
                      <button 
                        className="pay-button"
                        onClick={() => handlePayment(order.id)}
                      >
                        立即付款
                      </button>
                    )}
                    {order.status === 'shipped' && (
                      <button 
                        className="track-button"
                        onClick={() => handleTrackingClick(order.id)}
                      >
                        追蹤物流
                      </button>
                    )}
                    {order.status === 'completed' && (
                      <button className="review-button">
                        評價商品
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedOrderId && (
        <TrackingDialog 
          orderId={selectedOrderId} 
          onClose={handleCloseTracking} 
        />
      )}
    </div>
  );
};

export default OrderPage;