import React, { useState } from 'react';
import { Rate } from 'antd';
import '../styles/ReviewDialog.css';

const ReviewDialog = ({ orderId, productId, productName, onClose, onSubmit }) => {
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5000/api/reviews', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    order_id: orderId,
                    product_id: productId,
                    rating,
                    comment
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit review');
            }

            onSubmit();
        } catch (error) {
            console.error('Error submitting review:', error);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="review-dialog">
            <div className="review-content">
                <button className="close-button" onClick={onClose}>&times;</button>
                
                <div className="review-header">
                    <h3>商品評價</h3>
                    <p className="product-name">{productName}</p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="rating-section">
                        <label>評分：</label>
                        <Rate 
                            value={rating} 
                            onChange={setRating} 
                        />
                    </div>

                    <div className="comment-section">
                        <label>評價內容：</label>
                        <textarea
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            placeholder="請分享您的使用心得..."
                            rows={4}
                            required
                        />
                    </div>

                    <div className="action-buttons">
                        <button 
                            type="button" 
                            className="cancel-button"
                            onClick={onClose}
                        >
                            取消
                        </button>
                        <button 
                            type="submit" 
                            className="submit-button"
                            disabled={submitting}
                        >
                            {submitting ? '提交中...' : '提交評價'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ReviewDialog;