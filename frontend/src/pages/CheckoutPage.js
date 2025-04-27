import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { clearCart } from '../store/reducers/cartReducer';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/CheckoutPage.css';

const CheckoutPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(true);
  const [recipients, setRecipients] = useState([]);
  const [selectedRecipient, setSelectedRecipient] = useState('');
  const [useExistingRecipient, setUseExistingRecipient] = useState(true);
  const [newRecipient, setNewRecipient] = useState({
    name: '',
    phone: '',
    address: ''
  });
  const [error, setError] = useState('');

  // 從 location state 獲取商品資訊
  const { items } = location.state || {};
  const total = items?.reduce((sum, item) => sum + (item.product.price * item.quantity), 0) || 0;

  useEffect(() => {
    if (!items || items.length === 0) {
      navigate('/cart');
      return;
    }

    const fetchRecipients = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      try {
        const response = await fetch('http://localhost:5000/api/recipients', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const data = await response.json();
        setRecipients(data);
        if (data.length > 0) {
          setSelectedRecipient(data[0].id);
        } else {
          setUseExistingRecipient(false);
        }
      } catch (err) {
        console.error('Failed to fetch recipients:', err);
        setError('載入收貨人資料失敗');
      } finally {
        setLoading(false);
      }
    };

    fetchRecipients();
  }, [navigate, items]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const orderPromises = items.map(item => {
        const orderData = {
          product_id: item.productId,
          quantity: item.quantity,
          ...(useExistingRecipient
            ? { recipient_id: selectedRecipient }
            : {
                recipient_name: newRecipient.name,
                recipient_phone: newRecipient.phone,
                recipient_address: newRecipient.address,
              }),
        };

        return fetch('http://localhost:5000/api/orders', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(orderData),
        });
      });

      const responses = await Promise.all(orderPromises);
      const results = await Promise.all(responses.map(r => r.json()));
      
      const hasError = results.some(r => !r.order_id);
      if (hasError) {
        setError('部分訂單建立失敗');
        return;
      }

      // 清空購物車
      dispatch(clearCart());

      // 導向第一個訂單的付款頁面
      navigate(`/orders/${results[0].order_id}/payment`, {
        state: { paymentInfo: results[0].payment_info }
      });
    } catch (err) {
      console.error('Failed to create orders:', err);
      setError('系統錯誤，請稍後再試');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="checkout-page">
      <h2>結帳</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="order-summary">
        <h3>訂單資訊</h3>
        <div className="order-items">
          {items.map((item) => (
            <div key={item.productId} className="order-item">
              <img src={item.product.image_url || '/placeholder.jpg'} alt={item.product.name} />
              <div className="item-details">
                <h4>{item.product.name}</h4>
                <p>數量：{item.quantity}</p>
                <p className="price">小計：NT$ {item.product.price * item.quantity}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="total-amount">
          <span>總金額：</span>
          <span className="price">NT$ {total}</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="checkout-form">
        <h3>收貨資訊</h3>
        
        {recipients.length > 0 && (
          <div className="form-group">
            <label>
              <input
                type="radio"
                checked={useExistingRecipient}
                onChange={() => setUseExistingRecipient(true)}
              />
              使用已存收貨人
            </label>
            
            {useExistingRecipient && (
              <select
                value={selectedRecipient}
                onChange={(e) => setSelectedRecipient(e.target.value)}
                required
              >
                {recipients.map(r => (
                  <option key={r.id} value={r.id}>
                    {r.name} - {r.phone} - {r.address}
                  </option>
                ))}
              </select>
            )}
          </div>
        )}

        <div className="form-group">
          <label>
            <input
              type="radio"
              checked={!useExistingRecipient}
              onChange={() => setUseExistingRecipient(false)}
            />
            使用新收貨人
          </label>
          
          {!useExistingRecipient && (
            <div className="new-recipient-form">
              <div className="form-group">
                <label>收貨人姓名</label>
                <input
                  type="text"
                  value={newRecipient.name}
                  onChange={(e) => setNewRecipient(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required={!useExistingRecipient}
                  maxLength={100}
                />
              </div>

              <div className="form-group">
                <label>手機號碼</label>
                <input
                  type="tel"
                  value={newRecipient.phone}
                  onChange={(e) => setNewRecipient(prev => ({
                    ...prev,
                    phone: e.target.value
                  }))}
                  required={!useExistingRecipient}
                  pattern="09[0-9]{8}"
                  maxLength={10}
                  placeholder="09xxxxxxxx"
                />
              </div>

              <div className="form-group">
                <label>收貨地址</label>
                <input
                  type="text"
                  value={newRecipient.address}
                  onChange={(e) => setNewRecipient(prev => ({
                    ...prev,
                    address: e.target.value
                  }))}
                  required={!useExistingRecipient}
                  maxLength={200}
                />
              </div>
            </div>
          )}
        </div>

        <button type="submit" className="submit-button">確認下單</button>
      </form>
    </div>
  );
};

export default CheckoutPage;