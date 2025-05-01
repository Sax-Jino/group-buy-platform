import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { updateQuantity, removeFromCart } from '../store/reducers/cartReducer';
import CartNotification from '../components/CartNotification';
import '../styles/CartPage.css';

const CartPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const cartItems = useSelector(state => state.cart.items);
  const [notification, setNotification] = useState({ show: false, message: '' });

  const handleQuantityChange = (productId, quantity) => {
    const newQuantity = parseInt(quantity);
    if (isNaN(newQuantity) || newQuantity < 1) return;
    
    const item = cartItems.find(item => item.productId === productId);
    if (!item) return;

    if (item.product.stock && newQuantity > item.product.stock) {
      setNotification({
        show: true,
        message: `商品庫存只剩 ${item.product.stock} ${item.product.unit || '件'}`
      });
      return;
    }

    dispatch(updateQuantity({ productId, quantity: newQuantity }));
  };

  const handleRemove = (productId) => {
    dispatch(removeFromCart(productId));
    setNotification({ show: true, message: '已從購物車移除商品' });
  };

  const calculateItemTotal = (item) => {
    return item.product.price * item.quantity;
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => {
      return total + calculateItemTotal(item);
    }, 0);
  };

  const handleCheckout = () => {
    if (cartItems.length === 0) return;
    
    // 檢查庫存
    const invalidItems = cartItems.filter(
      item => item.product.stock && item.quantity > item.product.stock
    );

    if (invalidItems.length > 0) {
      setNotification({
        show: true,
        message: '部分商品庫存不足，請調整數量'
      });
      return;
    }
    
    navigate('/checkout', { 
      state: { items: cartItems }
    });
  };

  if (cartItems.length === 0) {
    return (
      <div className="cart-page">
        <h2>購物車</h2>
        <div className="empty-cart">
          <p>您的購物車是空的</p>
          <button onClick={() => navigate('/products')}>去購物</button>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <CartNotification 
        show={notification.show}
        message={notification.message}
        onHide={() => setNotification({ ...notification, show: false })}
      />

      <h2>購物車</h2>
      <div className="cart-items">
        {cartItems.map((item) => (
          <div key={item.productId} className="cart-item">
            <img 
              src={item.product.image_url || '/placeholder.jpg'} 
              alt={item.product.name}
              onClick={() => navigate(`/products/${item.productId}`)}
            />
            <div className="item-details">
              <h3 onClick={() => navigate(`/products/${item.productId}`)}>
                {item.product.name}
              </h3>
              <p className="price">單價：NT$ {item.product.price}</p>
              {item.product.stock && (
                <p className="stock">
                  庫存：{item.product.stock} {item.product.unit || '件'}
                </p>
              )}
              <div className="quantity-control">
                <button 
                  onClick={() => handleQuantityChange(item.productId, item.quantity - 1)}
                  disabled={item.quantity <= 1}
                >-</button>
                <input
                  type="number"
                  min="1"
                  max={item.product.stock || 999}
                  value={item.quantity}
                  onChange={(e) => handleQuantityChange(item.productId, e.target.value)}
                  onBlur={(e) => {
                    const value = parseInt(e.target.value);
                    if (isNaN(value) || value < 1) {
                      handleQuantityChange(item.productId, 1);
                    }
                  }}
                />
                <button 
                  onClick={() => handleQuantityChange(item.productId, item.quantity + 1)}
                  disabled={item.product.stock && item.quantity >= item.product.stock}
                >+</button>
              </div>
              <p className="subtotal">小計：NT$ {calculateItemTotal(item)}</p>
              <button 
                className="remove-button"
                onClick={() => handleRemove(item.productId)}
              >
                移除
              </button>
            </div>
          </div>
        ))}
      </div>
      
      <div className="cart-summary">
        <h3>訂單摘要</h3>
        <div className="summary-row">
          <span>商品總數：</span>
          <span>{cartItems.reduce((sum, item) => sum + item.quantity, 0)} 件</span>
        </div>
        <div className="summary-row">
          <span>總金額：</span>
          <span className="total">NT$ {calculateTotal()}</span>
        </div>
        <button 
          className="checkout-button"
          onClick={handleCheckout}
          disabled={cartItems.length === 0}
        >
          前往結帳
        </button>
      </div>
    </div>
  );
};

export default CartPage;