import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { addToCart } from '../store/reducers/cartReducer';
import LoadingSpinner from '../components/LoadingSpinner';
import CartNotification from '../components/CartNotification';
import '../styles/ProductDetailPage.css';

const ProductDetailPage = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [showNotification, setShowNotification] = useState(false);

  useEffect(() => {
    const fetchProductDetail = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/products/${productId}`);
        if (!response.ok) throw new Error('商品不存在');
        const data = await response.json();
        setProduct(data);

        // 獲取相關商品
        const relatedResponse = await fetch(
          `http://localhost:5000/api/products/category/${data.category}?limit=5`
        );
        const relatedData = await relatedResponse.json();
        setRelatedProducts(
          relatedData.products.filter(p => p.id !== parseInt(productId)).slice(0, 4)
        );
      } catch (err) {
        console.error('Failed to fetch product:', err);
        setError(err.message || '載入商品資訊失敗');
      } finally {
        setLoading(false);
      }
    };

    fetchProductDetail();
  }, [productId]);

  const handleQuantityChange = (value) => {
    const newValue = parseInt(value);
    if (!isNaN(newValue) && newValue > 0 && (!product.stock || newValue <= product.stock)) {
      setQuantity(newValue);
    }
  };

  const handleAddToCart = () => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
      return;
    }
    
    dispatch(addToCart({
      product,
      quantity
    }));

    setShowNotification(true);
  };

  const handleBuyNow = () => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
      return;
    }

    navigate('/checkout', {
      state: {
        items: [{
          productId: product.id,
          product,
          quantity
        }]
      }
    });
  };

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="product-detail-page">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!product) return null;

  const images = [
    product.image_url || 'https://via.placeholder.com/600x400?text=商品主圖',
    ...(product.additional_images || []).map(
      img => img || 'https://via.placeholder.com/600x400?text=商品圖'
    )
  ];

  return (
    <div className="product-detail-page">
      <CartNotification 
        show={showNotification}
        message={`已將 ${quantity} ${product?.unit || '件'} ${product?.name} 加入購物車`}
        onHide={() => setShowNotification(false)}
      />

      <div className="product-main">
        <div className="product-gallery">
          <div className="main-image">
            <img 
              src={images[currentImageIndex]} 
              alt={product.name}
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = 'https://via.placeholder.com/600x400?text=無商品圖片';
              }}
            />
          </div>
          <div className="thumbnail-list">
            {images.map((img, index) => (
              <div 
                key={index}
                className={`thumbnail ${index === currentImageIndex ? 'active' : ''}`}
                onClick={() => setCurrentImageIndex(index)}
              >
                <img 
                  src={img} 
                  alt={`${product.name} - 圖${index + 1}`}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'https://via.placeholder.com/100x100?text=無圖片';
                  }}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="product-info">
          <h1>{product.name}</h1>
          <div className="price-section">
            <div className="market-price">市價：NT$ {product.market_price}</div>
            <div className="group-price">團購價：NT$ {product.price}</div>
            {product.stock !== null && (
              <div className="stock">
                庫存：{product.stock} {product.unit || '件'}
              </div>
            )}
          </div>

          <div className="description">
            <h2>商品說明</h2>
            <p>{product.description}</p>
          </div>

          <div className="quantity-section">
            <label>數量：</label>
            <div className="quantity-control">
              <button 
                onClick={() => handleQuantityChange(quantity - 1)}
                disabled={quantity <= 1}
              >-</button>
              <input
                type="number"
                min="1"
                max={product.stock || 999}
                value={quantity}
                onChange={(e) => handleQuantityChange(e.target.value)}
              />
              <button 
                onClick={() => handleQuantityChange(quantity + 1)}
                disabled={product.stock && quantity >= product.stock}
              >+</button>
            </div>
          </div>

          <div className="action-buttons">
            <button 
              className="add-to-cart"
              onClick={handleAddToCart}
              disabled={product.stock === 0}
            >
              加入購物車
            </button>
            <button 
              className="buy-now"
              onClick={handleBuyNow}
              disabled={product.stock === 0}
            >
              立即購買
            </button>
          </div>
        </div>
      </div>

      {relatedProducts.length > 0 && (
        <div className="related-products">
          <h2>相關商品</h2>
          <div className="related-list">
            {relatedProducts.map(related => (
              <div 
                key={related.id} 
                className="related-item"
                onClick={() => navigate(`/products/${related.id}`)}
              >
                <img 
                  src={related.image_url || 'https://via.placeholder.com/200x200?text=商品圖片'} 
                  alt={related.name}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'https://via.placeholder.com/200x200?text=無商品圖片';
                  }}
                />
                <div className="related-info">
                  <h3>{related.name}</h3>
                  <p className="price">NT$ {related.price}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetailPage;