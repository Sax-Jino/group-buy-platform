from extensions import db
from models.product_review import ProductReview
from models.order import Order
from datetime import datetime

class ReviewService:
    def create_review(self, user_id, data):
        required_fields = ['order_id', 'product_id', 'rating', 'comment']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")

        if not isinstance(data['rating'], int) or not 1 <= data['rating'] <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # 驗證訂單存在且屬於該用戶
        order = Order.query.get(data['order_id'])
        if not order or str(order.user_id) != str(user_id):
            raise ValueError("Order not found or not owned by user")
        
        # 驗證訂單狀態為已完成
        if order.status != 'completed':
            raise ValueError("Can only review completed orders")

        # 檢查是否已經評價過
        existing_review = ProductReview.query.filter_by(
            product_id=data['product_id'],
            user_id=user_id,
            order_id=data['order_id']
        ).first()
        
        if existing_review:
            raise ValueError("You have already reviewed this order")

        review = ProductReview(
            product_id=data['product_id'],
            user_id=user_id,
            order_id=data['order_id'],
            rating=data['rating'],
            comment=data['comment']
        )
        
        db.session.add(review)
        db.session.commit()
        return review

    def get_reviews_by_product(self, product_id):
        return ProductReview.query.filter_by(product_id=product_id)\
            .order_by(ProductReview.created_at.desc())\
            .all()

    def get_reviews_by_user(self, user_id):
        return ProductReview.query.filter_by(user_id=user_id)\
            .order_by(ProductReview.created_at.desc())\
            .all()

    def get_product_rating_summary(self, product_id):
        reviews = ProductReview.query.filter_by(product_id=product_id).all()
        if not reviews:
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }

        total_rating = sum(review.rating for review in reviews)
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1

        return {
            'average_rating': round(total_rating / len(reviews), 1),
            'total_reviews': len(reviews),
            'rating_distribution': rating_distribution
        }