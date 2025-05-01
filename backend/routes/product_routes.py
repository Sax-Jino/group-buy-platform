from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.product_service import ProductService
from extensions import csrf

bp = Blueprint('product_routes', __name__)

product_service = ProductService()

@bp.route('', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_product():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        product = product_service.create_product(user_id, data)
        return jsonify({"message": "Product created successfully", "product_id": product.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('', methods=['GET'])
def get_products():
    products = product_service.get_all_products()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "market_price": p.market_price,
        "stock": p.stock,
        "supplier_id": p.supplier_id,
        "category": p.category,
        "image_url": p.image_url,
        "created_at": p.created_at.isoformat()
    } for p in products]), 200

@bp.route('/hot', methods=['GET'])
def get_hot_products():
    """獲取熱賣商品"""
    limit = request.args.get('limit', 5, type=int)
    products = product_service.get_hot_products(limit)
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "market_price": p.market_price,
        "stock": p.stock,
        "supplier_id": p.supplier_id,
        "category": p.category,
        "image_url": p.image_url,
        "created_at": p.created_at.isoformat()
    } for p in products]), 200

@bp.route('/latest', methods=['GET'])
def get_latest_products():
    """獲取最新商品"""
    limit = request.args.get('limit', 10, type=int)
    products = product_service.get_latest_products(limit)
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "market_price": p.market_price,
        "stock": p.stock,
        "supplier_id": p.supplier_id,
        "category": p.category,
        "image_url": p.image_url,
        "created_at": p.created_at.isoformat()
    } for p in products]), 200

@bp.route('/category/<category>', methods=['GET'])
def get_products_by_category(category):
    """獲取分類商品"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    exclude_id = request.args.get('exclude_id', None, type=int)
    
    paginated_products = product_service.get_products_by_category(
        category=category,
        page=page,
        per_page=per_page,
        exclude_id=exclude_id
    )
    
    return jsonify({
        'products': [{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "market_price": p.market_price,
            "stock": p.stock,
            "supplier_id": p.supplier_id,
            "category": p.category,
            "image_url": p.image_url,
            "created_at": p.created_at.isoformat()
        } for p in paginated_products.items],
        'total': paginated_products.total,
        'pages': paginated_products.pages,
        'current_page': paginated_products.page
    }), 200

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """獲取商品詳情"""
    product = product_service.get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # 獲取相關商品
    related_products = product_service.get_related_products(product_id)
    
    return jsonify({
        **product,
        "created_at": product["created_at"].isoformat(),
        "related_products": related_products
    }), 200

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@csrf.exempt
def update_product(product_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        product = product_service.update_product(product_id, user_id, data)
        return jsonify({"message": "Product updated successfully", "product_id": product.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """獲取搜尋建議"""
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 5, type=int)
    
    suggestions = product_service.search_suggestions(query, limit)
    return jsonify({
        'suggestions': [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'image_url': p.image_url
        } for p in suggestions]
    }), 200

@bp.route('/search', methods=['GET'])
def search_products():
    """搜尋商品"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category')
    sort_by = request.args.get('sort', 'relevance')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not query:
        return jsonify({
            'message': '請輸入搜尋關鍵字'
        }), 400
        
    result = product_service.search_products(
        query=query,
        category=category,
        sort_by=sort_by,
        page=page,
        per_page=per_page
    )
    
    if not result:
        return jsonify({
            'message': '沒有找到相關商品',
            'products': [],
            'total': 0,
            'pages': 0,
            'current_page': page
        }), 200
        
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'market_price': p.market_price,
            'stock': p.stock,
            'category': p.category,
            'image_url': p.image_url,
            'created_at': p.created_at.isoformat()
        } for p in result.items],
        'total': result.total,
        'pages': result.pages,
        'current_page': result.page
    }), 200