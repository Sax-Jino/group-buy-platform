import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { addToCart } from '../store/reducers/cartReducer';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/ProductPage.css';

const ProductPage = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [quantities, setQuantities] = useState({});

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/products');
        const data = await response.json();
        setProducts(data);
        // 初始化每個商品的數量為1
        const initialQuantities = {};
        data.forEach(product => {
          initialQuantities[product.id] = 1;
        });
        setQuantities(initialQuantities);
      } catch (err) {
        console.error('Failed to fetch products:', err);
        setError('載入商品失敗');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const handleQuantityChange = (productId, value) => {
    const newValue = parseInt(value);
    if (!isNaN(newValue) && newValue > 0) {
      setQuantities(prev => ({
        ...prev,
        [productId]: newValue
      }));
    }
  };

  const handleAddToCart = (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    dispatch(addToCart({
      product,
      quantity: quantities[product.id]
    }));
  };

  const handlePurchase = (product) => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    navigate('/checkout', { 
      state: { 
        items: [{
          productId: product.id,
          product,
          quantity: quantities[product.id]
        }]
      }
    });
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="product-page">
      <h2>商品列表</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="product-list">
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <img src={product.image_url || '/placeholder.jpg'} alt={product.name} />
            <h3>{product.name}</h3>
            <p>{product.description}</p>
            <p className="price">NT$ {product.price}</p>
            <p>庫存: {product.stock || '不限'}</p>
            
            <div className="quantity-control">
              <button 
                onClick={() => handleQuantityChange(product.id, quantities[product.id] - 1)}
                disabled={quantities[product.id] <= 1}
              >-</button>
              <input
                type="number"
                min="1"
                value={quantities[product.id]}
                onChange={(e) => handleQuantityChange(product.id, e.target.value)}
                onBlur={(e) => {
                  const value = parseInt(e.target.value);
                  if (isNaN(value) || value < 1) {
                    handleQuantityChange(product.id, 1);
                  }
                }}
              />
              <button 
                onClick={() => handleQuantityChange(product.id, quantities[product.id] + 1)}
                disabled={product.stock && quantities[product.id] >= product.stock}
              >+</button>
            </div>

            <div className="product-actions">
              <button 
                className="add-to-cart"
                onClick={() => handleAddToCart(product)}
                disabled={product.stock === 0}
              >
                加入購物車
              </button>
              <button 
                className="buy-now"
                onClick={() => handlePurchase(product)}
                disabled={product.stock === 0}
              >
                立即購買
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductPage;