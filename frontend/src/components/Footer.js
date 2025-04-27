import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <p>&copy; 2025 團購平台. All rights reserved.</p>
        <div className="footer-links">
          <Link to="/about">關於我們</Link>
          <Link to="/contact">聯絡我們</Link>
          <Link to="/terms">服務條款</Link>
          <Link to="/privacy">隱私政策</Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;