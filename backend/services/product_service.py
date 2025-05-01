from extensions import db
from models.product import Product
from models.user import User
from models.order import Order
from sqlalchemy import func, desc, or_
from datetime import datetime, timedelta

class ProductService:
    def create_product(self, user_id, data):
        required_fields = ['name', 'price', 'stock']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        user = User.query.get(user_id)
        if not user or user.role != 'supplier':
            raise ValueError("Only suppliers can create products")
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=float(data['price']),
            stock=int(data['stock']),
            supplier_id=user_id,
            category=data.get('category'),
            image_url=data.get('image_url')
        )
        db.session.add(product)
        db.session.commit()
        return product

    def get_all_products(self):
        return Product.query.filter_by(is_active=True).all()

    def get_product_by_id(self, product_id):
        """獲取商品詳情，包含額外圖片"""
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return None

        # 獲取訂單數量
        order_count = Order.query.filter(
            Order.product_id == product_id,
            Order.created_at >= datetime.now() - timedelta(days=30)
        ).count()

        # 產生商品詳情
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "market_price": product.market_price,
            "stock": product.stock,
            "supplier_id": product.supplier_id,
            "category": product.category,
            "unit": product.unit,
            "image_url": product.image_url,
            "additional_images": product.additional_images or [],
            "specifications": product.specifications or {},
            "created_at": product.created_at,
            "order_count": order_count
        }

    def update_product(self, product_id, user_id, data):
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")
        if product.supplier_id != user_id:
            raise ValueError("Only the supplier can update this product")
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price)) if 'price' in data else product.price
        product.stock = int(data.get('stock', product.stock)) if 'stock' in data else product.stock
        product.category = data.get('category', product.category)
        product.image_url = data.get('image_url', product.image_url)
        db.session.commit()
        return product

    def get_hot_products(self, limit=5):
        """獲取熱賣商品，根據訂單數量排序"""
        subquery = db.session.query(
            Order.product_id,
            func.count(Order.id).label('order_count')
        ).filter(
            Order.created_at >= datetime.now() - timedelta(days=30)
        ).group_by(Order.product_id).subquery()

        return Product.query.join(
            subquery,
            Product.id == subquery.c.product_id
        ).filter(
            Product.is_active == True
        ).order_by(
            desc(subquery.c.order_count)
        ).limit(limit).all()

    def get_latest_products(self, limit=10):
        """獲取最新上架商品"""
        return Product.query.filter(
            Product.is_active == True,
            Product.on_shelf_date <= datetime.now(),
            Product.off_shelf_date > datetime.now()
        ).order_by(
            desc(Product.created_at)
        ).limit(limit).all()

    def get_products_by_category(self, category, page=1, per_page=20, exclude_id=None):
        """獲取指定分類的商品，可以排除特定商品"""
        query = Product.query.filter(
            Product.is_active == True,
            Product.category == category
        )
        
        if exclude_id:
            query = query.filter(Product.id != exclude_id)
            
        return query.order_by(desc(Product.created_at)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    def get_related_products(self, product_id, limit=4):
        """獲取相關商品（同類別的其他商品）"""
        product = Product.query.get(product_id)
        if not product:
            return []
            
        related = Product.query.filter(
            Product.is_active == True,
            Product.category == product.category,
            Product.id != product_id
        ).order_by(
            desc(Product.created_at)
        ).limit(limit).all()
        
        return [{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "market_price": p.market_price,
            "stock": p.stock,
            "image_url": p.image_url,
            "created_at": p.created_at
        } for p in related]

    def search_suggestions(self, query, limit=5):
        """獲取搜尋建議"""
        if not query or len(query.strip()) < 2:
            return []
            
        search_query = f"%{query}%"
        return Product.query.filter(
            Product.is_active == True,
            or_(
                Product.name.ilike(search_query),
                Product.description.ilike(search_query),
                Product.category.ilike(search_query)
            )
        ).order_by(
            desc(Product.order_count),
            desc(Product.created_at)
        ).limit(limit).all()

    def search_products(self, query, category=None, sort_by='relevance', page=1, per_page=20):
        """搜尋商品"""
        if not query.strip():
            return None
            
        search_query = f"%{query}%"
        base_query = Product.query.filter(
            Product.is_active == True,
            or_(
                Product.name.ilike(search_query),
                Product.description.ilike(search_query)
            )
        )
        
        if category:
            base_query = base_query.filter(Product.category == category)
        
        # 根據排序方式調整查詢
        if sort_by == 'price_asc':
            base_query = base_query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            base_query = base_query.order_by(Product.price.desc())
        elif sort_by == 'newest':
            base_query = base_query.order_by(desc(Product.created_at))
        else:  # relevance - default
            base_query = base_query.order_by(
                desc(Product.order_count),
                desc(Product.created_at)
            )
            
        return base_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )