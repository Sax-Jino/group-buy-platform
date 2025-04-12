import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <p>&copy; 2025 團購平台. All rights reserved.</p>
        <div className="footer-links">
          <a href="/about">關於我們</a>
          <a href="/contact">聯絡我們</a>
          <a href="/terms">服務條款</a>
          <a href="/privacy">隱私政策</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;