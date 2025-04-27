import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { updateQuantity, removeFromCart } from '../store/reducers/cartReducer';
import '../styles/CartPage.css';

const CartPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const cartItems = useSelector(state => state.cart.items);

  const handleQuantityChange = (productId, quantity) => {
    dispatch(updateQuantity({ productId, quantity: parseInt(quantity) }));
  };

  const handleRemove = (productId) => {
    dispatch(removeFromCart(productId));
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => {
      return total + (item.product.price * item.quantity);
    }, 0);
  };

  const handleCheckout = () => {
    if (cartItems.length === 0) return;
    
    navigate('/checkout', { 
      state: { 
        items: cartItems
      }
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
      <h2>購物車</h2>
      <div className="cart-items">
        {cartItems.map((item) => (
          <div key={item.productId} className="cart-item">
            <img src={item.product.image_url || '/placeholder.jpg'} alt={item.product.name} />
            <div className="item-details">
              <h3>{item.product.name}</h3>
              <p className="price">NT$ {item.product.price}</p>
              <div className="quantity-control">
                <button 
                  onClick={() => handleQuantityChange(item.productId, item.quantity - 1)}
                  disabled={item.quantity <= 1}
                >-</button>
                <input
                  type="number"
                  min="1"
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
                >+</button>
              </div>
              <p className="subtotal">小計：NT$ {item.product.price * item.quantity}</p>
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
          <span>總金額：</span>
          <span className="total">NT$ {calculateTotal()}</span>
        </div>
        <button 
          className="checkout-button"
          onClick={handleCheckout}
        >
          前往結帳
        </button>
      </div>
    </div>
  );
};

export default CartPage;