import React, { useState } from 'react';
import { useLocation, useParams, useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/PaymentPage.css';

const PaymentPage = () => {
  const { orderId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [accountLast5, setAccountLast5] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const paymentInfo = location.state?.paymentInfo;

  if (!paymentInfo) {
    return <div className="payment-page">
      <div className="error-message">找不到付款資訊</div>
    </div>;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (accountLast5.length !== 5) {
      setError('請輸入帳號後五碼');
      return;
    }

    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`http://localhost:5000/api/orders/${orderId}/submit_remittance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ account_last5: accountLast5 }),
      });

      const data = await response.json();
      if (response.ok) {
        navigate('/orders');
      } else {
        setError(data.error || '提交匯款資訊失敗');
      }
    } catch (err) {
      console.error('Failed to submit remittance info:', err);
      setError('系統錯誤，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="payment-page">
      <h2>付款資訊</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="payment-info">
        <p><strong>銀行名稱：</strong>{paymentInfo.bank_name}</p>
        <p><strong>分行代碼：</strong>{paymentInfo.bank_code}</p>
        <p><strong>匯款帳號：</strong>{paymentInfo.account_number}</p>
        <p><strong>付款期限：</strong>{new Date(paymentInfo.payment_deadline).toLocaleString()}</p>
      </div>

      <form onSubmit={handleSubmit} className="remittance-form">
        <div className="form-group">
          <label>匯款帳號後五碼</label>
          <input
            type="text"
            value={accountLast5}
            onChange={(e) => {
              const value = e.target.value.replace(/[^0-9]/g, '');
              if (value.length <= 5) {
                setAccountLast5(value);
              }
            }}
            maxLength="5"
            pattern="[0-9]{5}"
            required
            placeholder="請輸入匯款帳號後五碼"
          />
        </div>
        <button type="submit">確認已付款</button>
      </form>

      <div className="payment-notes">
        <h3>注意事項</h3>
        <ul>
          <li>請於付款期限前完成匯款，否則訂單將自動取消。</li>
          <li>匯款後請務必填寫帳號後五碼，以利核對款項。</li>
          <li>如有任何問題，請聯繫客服。</li>
        </ul>
      </div>
    </div>
  );
};

export default PaymentPage;