from extensions import db
from models.product import Product
from models.user import User

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
        return Product.query.filter_by(id=product_id, is_active=True).first()

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