import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { addToCart } from '../store/reducers/cartReducer';
import LoadingSpinner from '../components/LoadingSpinner';
import CartNotification from '../components/CartNotification';
import '../styles/SearchPage.css';

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantities, setQuantities] = useState({});
  const [notification, setNotification] = useState({ show: false, message: '' });
  const [totalPages, setTotalPages] = useState(1);
  
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || '';
  const sort = searchParams.get('sort') || 'relevance';
  const page = parseInt(searchParams.get('page')) || 1;
  
  useEffect(() => {
    const fetchProducts = async () => {
      if (!query.trim()) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:5000/api/products/search?` + 
          `q=${encodeURIComponent(query)}` +
          `&category=${encodeURIComponent(category)}` +
          `&sort=${encodeURIComponent(sort)}` +
          `&page=${page}`
        );
        
        if (!response.ok) throw new Error('搜尋失敗');
        
        const data = await response.json();
        setProducts(data.products);
        setTotalPages(data.pages);
        
        // 初始化商品數量
        const initialQuantities = {};
        data.products.forEach(product => {
          initialQuantities[product.id] = 1;
        });
        setQuantities(initialQuantities);
        
      } catch (err) {
        console.error('Search failed:', err);
        setError('搜尋失敗，請稍後再試');
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducts();
  }, [query, category, sort, page]);

  const handleQuantityChange = (productId, value) => {
    const newValue = parseInt(value);
    if (isNaN(newValue) || newValue < 1) return;
    
    const product = products.find(p => p.id === productId);
    if (product.stock && newValue > product.stock) {
      setNotification({
        show: true,
        message: `商品庫存只剩 ${product.stock} ${product.unit || '件'}`
      });
      return;
    }
    
    setQuantities(prev => ({
      ...prev,
      [productId]: newValue
    }));
  };

  const handleAddToCart = (product) => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
      return;
    }
    
    dispatch(addToCart({
      product,
      quantity: quantities[product.id]
    }));
    
    setNotification({
      show: true,
      message: `已將 ${quantities[product.id]} ${product.unit || '件'} ${product.name} 加入購物車`
    });
  };

  const handleCategoryChange = (newCategory) => {
    searchParams.set('category', newCategory);
    searchParams.set('page', '1');
    setSearchParams(searchParams);
  };

  const handleSortChange = (newSort) => {
    searchParams.set('sort', newSort);
    searchParams.set('page', '1');
    setSearchParams(searchParams);
  };

  const handlePageChange = (newPage) => {
    if (newPage < 1 || newPage > totalPages) return;
    searchParams.set('page', newPage.toString());
    setSearchParams(searchParams);
  };

  if (loading) return <LoadingSpinner />;

  if (!query.trim()) {
    return (
      <div className="search-page">
        <div className="no-query">
          請輸入搜尋關鍵字
        </div>
      </div>
    );
  }

  return (
    <div className="search-page">
      <CartNotification 
        show={notification.show}
        message={notification.message}
        onHide={() => setNotification({ ...notification, show: false })}
      />

      <div className="search-header">
        <h2>搜尋結果：{query}</h2>
        <div className="search-filters">
          <div className="filter-group">
            <label>分類：</label>
            <select 
              value={category} 
              onChange={(e) => handleCategoryChange(e.target.value)}
            >
              <option value="">全部分類</option>
              <option value="food">食品</option>
              <option value="beauty">美妝保養</option>
              <option value="baby">媽咪寶貝</option>
              <option value="life">生活日用</option>
              <option value="3c">3C家電</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>排序：</label>
            <select 
              value={sort}
              onChange={(e) => handleSortChange(e.target.value)}
            >
              <option value="relevance">相關度</option>
              <option value="price_asc">價格由低到高</option>
              <option value="price_desc">價格由高到低</option>
              <option value="newest">最新上架</option>
            </select>
          </div>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {products.length === 0 ? (
        <div className="no-results">
          沒有找到相關商品
        </div>
      ) : (
        <>
          <div className="product-grid">
            {products.map((product) => (
              <div key={product.id} className="product-card">
                <img
                  src={product.image_url || '/placeholder.jpg'}
                  alt={product.name}
                  onClick={() => navigate(`/products/${product.id}`)}
                />
                <div className="product-info">
                  <h3 onClick={() => navigate(`/products/${product.id}`)}>
                    {product.name}
                  </h3>
                  <p className="description">{product.description}</p>
                  <div className="price-row">
                    <span className="price">NT$ {product.price}</span>
                    {product.market_price && (
                      <span className="market-price">
                        NT$ {product.market_price}
                      </span>
                    )}
                  </div>
                  {product.stock && (
                    <p className="stock">
                      庫存：{product.stock} {product.unit || '件'}
                    </p>
                  )}
                  
                  <div className="product-actions">
                    <div className="quantity-control">
                      <button
                        onClick={() => handleQuantityChange(
                          product.id,
                          quantities[product.id] - 1
                        )}
                        disabled={quantities[product.id] <= 1}
                      >-</button>
                      <input
                        type="number"
                        min="1"
                        max={product.stock || 999}
                        value={quantities[product.id]}
                        onChange={(e) => handleQuantityChange(
                          product.id,
                          e.target.value
                        )}
                      />
                      <button
                        onClick={() => handleQuantityChange(
                          product.id,
                          quantities[product.id] + 1
                        )}
                        disabled={
                          product.stock &&
                          quantities[product.id] >= product.stock
                        }
                      >+</button>
                    </div>
                    
                    <button
                      className="add-to-cart"
                      onClick={() => handleAddToCart(product)}
                      disabled={!product.stock || product.stock === 0}
                    >
                      加入購物車
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page <= 1}
            >
              上一頁
            </button>
            <span className="page-info">
              第 {page} 頁，共 {totalPages} 頁
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page >= totalPages}
            >
              下一頁
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default SearchPage;