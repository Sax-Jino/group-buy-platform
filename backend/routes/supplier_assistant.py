from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.supplier_assistant import SupplierAssistant
from models.user import User
from services.supplier_assistant_service import SupplierAssistantService
from decorators.auth import supplier_required
from extensions import db, csrf

bp = Blueprint('supplier_assistant', __name__)
supplier_assistant_service = SupplierAssistantService()

@bp.route('/api/supplier-assistant', methods=['POST'])
@jwt_required()
@supplier_required
def create_assistant():
    """建立供應商副手帳號"""
    supplier_id = get_jwt_identity()
    data = request.get_json()

    try:
        assistant = supplier_assistant_service.create_assistant(supplier_id, data)
        return jsonify({
            'message': '成功建立供應商副手帳號',
            'assistant_id': assistant.id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/api/supplier-assistant', methods=['GET'])
@jwt_required()
@supplier_required
def list_assistants():
    """列出供應商的所有副手"""
    supplier_id = get_jwt_identity()
    assistants = supplier_assistant_service.get_assistants_by_supplier(supplier_id)
    
    return jsonify({
        'assistants': [{
            'id': a.id,
            'username': a.username,
            'name': a.name,
            'phone': a.phone,
            'permissions': a.permissions,
            'created_at': a.created_at.isoformat()
        } for a in assistants]
    })

@bp.route('/<assistant_id>/permissions', methods=['PUT'])
@jwt_required()
@supplier_required
def update_permissions(assistant_id):
    """更新供應商副手權限"""
    supplier_id = get_jwt_identity()
    data = request.get_json()

    try:
        assistant = supplier_assistant_service.update_permissions(
            supplier_id, 
            assistant_id, 
            data.get('permissions', {})
        )
        return jsonify({
            'message': '成功更新權限',
            'permissions': assistant.permissions
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<assistant_id>', methods=['DELETE'])
@jwt_required()
@supplier_required
def delete_assistant(assistant_id):
    """刪除供應商副手帳號"""
    supplier_id = get_jwt_identity()
    try:
        supplier_assistant_service.delete_assistant(supplier_id, assistant_id)
        return jsonify({'message': '成功刪除供應商副手帳號'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400