import React, { useState, useEffect } from 'react';
import '../styles/CartNotification.css';

const CartNotification = ({ show, message, onHide }) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onHide();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [show, onHide]);

  if (!show) return null;

  return (
    <div className="cart-notification">
      <div className="cart-notification-content">
        <span className="cart-icon">🛒</span>
        <span className="message">{message}</span>
      </div>
    </div>
  );
};

export default CartNotification;