import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/HomePage.css';

const HomePage = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [hotProducts, setHotProducts] = useState([]);
  const [latestProducts, setLatestProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const isAuthenticated = !!localStorage.getItem('token');

  // 輪播圖片數據
  const bannerImages = [
    { url: 'https://via.placeholder.com/1440x400?text=商品圖片+1', text: '新品上市：家用咖啡機' },
    { url: 'https://via.placeholder.com/1440x400?text=商品圖片+2', text: '限時特惠：藍芽耳機' },
    { url: 'https://via.placeholder.com/1440x400?text=商品圖片+3', text: '團購優惠：保養品系列' },
    { url: 'https://via.placeholder.com/1440x400?text=商品圖片+4', text: '熱銷推薦：健康食品' },
    { url: 'https://via.placeholder.com/1440x400?text=商品圖片+5', text: '新春特惠：年節禮盒' },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 獲取熱賣商品
        const hotResponse = await fetch('http://localhost:5000/api/products/hot?limit=5');
        if (!hotResponse.ok) throw new Error('Failed to fetch hot products');
        const hotData = await hotResponse.json();
        setHotProducts(hotData);

        // 獲取最新商品
        const latestResponse = await fetch('http://localhost:5000/api/products/latest?limit=10');
        if (!latestResponse.ok) throw new Error('Failed to fetch latest products');
        const latestData = await latestResponse.json();
        setLatestProducts(latestData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('無法載入商品資訊，請稍後再試');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // 自動輪播
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % bannerImages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const handleProductClick = (productId) => {
    if (!isAuthenticated) {
      alert('請先登入！');
      return false;
    }
    return true;
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="home-page">
      <div className="banner">
        <img src={bannerImages[currentSlide].url} alt="Banner" />
        <div className="text">{bannerImages[currentSlide].text}</div>
        <div className="dots">
          {bannerImages.map((_, index) => (
            <span
              key={index}
              className={index === currentSlide ? 'active' : ''}
              onClick={() => setCurrentSlide(index)}
            />
          ))}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="main-content">
        <div className="top-products">
          <h2>熱賣商品</h2>
          <ul>
            {hotProducts.map(product => (
              <li key={product.id}>
                <Link to={`/products/${product.id}`}>
                  {product.name}
                </Link>
                <p className="order-count">{product.order_count || '0'} 筆訂單</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="latest-products">
          <h2>最新商品</h2>
          <div className="grid">
            {latestProducts.map(product => (
              <div key={product.id} className="card">
                <Link 
                  to={`/products/${product.id}`}
                  onClick={() => handleProductClick(product.id)}
                >
                  <img 
                    src={product.image_url || 'https://via.placeholder.com/260x200?text=商品圖片'} 
                    alt={product.name}
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = 'https://via.placeholder.com/260x200?text=無商品圖片';
                    }}
                  />
                  <p className="name">{product.name}</p>
                  <p className="description">{product.description}</p>
                  <p>
                    <span className="market-price">市價：${product.market_price}</span>
                    <span className="group-price">團購價：${product.price}</span>
                  </p>
                  {product.stock <= 10 && product.stock > 0 && (
                    <p className="stock-warning">庫存剩下 {product.stock} 件</p>
                  )}
                  {product.stock === 0 && (
                    <p className="out-of-stock">已售完</p>
                  )}
                </Link>
              </div>
            ))}
          </div>
          <div className="pagination">
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              上一頁
            </button>
            <span className="page-info">第 {page} 頁，共 {totalPages} 頁</span>
            <button 
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              下一頁
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;