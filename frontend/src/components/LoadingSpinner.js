import React from 'react';
import '../styles/LoadingSpinner.css';

const LoadingSpinner = ({ type = 'spinner' }) => {
  if (type === 'products') {
    return (
      <div className="products-skeleton">
        <div className="banner-skeleton" />
        <div className="main-content">
          <div className="sidebar-skeleton">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="product-item-skeleton" />
            ))}
          </div>
          <div className="grid-skeleton">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="product-card-skeleton">
                <div className="image-skeleton" />
                <div className="title-skeleton" />
                <div className="price-skeleton" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="loading-spinner-container">
      <div className="loading-spinner" />
      <p>載入中...</p>
    </div>
  );
};

export default LoadingSpinner;