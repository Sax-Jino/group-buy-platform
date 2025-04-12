import React from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/HomePage.css';

const HomePage = () => {
  // eslint-disable-next-line no-unused-vars
  const [loading, setLoading] = React.useState(false);

  return (
    <div className="home-page">
      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <h1>歡迎來到團購平台</h1>
          <p>探索優質商品，參與團購協作，享受最佳購物體驗！</p>
          <div className="home-actions">
            <a href="/products" className="btn">瀏覽商品</a>
            <a href="/collaborations" className="btn">參與協作</a>
          </div>
        </>
      )}
    </div>
  );
};

export default HomePage;