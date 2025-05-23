from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.collaboration_service import CollaborationService
from services.chat_service import ChatService
from services.vote_service import VoteService
from extensions import csrf
from flask import current_app

bp = Blueprint('collaboration_routes', __name__)

collaboration_service = CollaborationService()
chat_service = ChatService()
vote_service = VoteService()

@bp.route('/proposals', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_proposal():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        proposal = collaboration_service.create_proposal(user_id, data)
        return jsonify({"message": "Proposal created successfully", "proposal_id": proposal.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to create proposal for user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/proposals', methods=['GET'])
def get_proposals():
    try:
        proposals = collaboration_service.get_all_proposals()
        return jsonify([{
            "id": p.id,
            "initiator_id": p.initiator_id,
            "title": p.title,
            "description": p.description,
            "target_amount": p.target_amount,
            "current_amount": p.current_amount,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
            "deadline": p.deadline.isoformat()
        } for p in proposals]), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch proposals: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/proposals/<int:proposal_id>', methods=['GET'])
def get_proposal(proposal_id):
    try:
        proposal = collaboration_service.get_proposal_by_id(proposal_id)
        if not proposal:
            return jsonify({"error": "Proposal not found"}), 404
        return jsonify({
            "id": proposal.id,
            "initiator_id": proposal.initiator_id,
            "title": proposal.title,
            "description": proposal.description,
            "target_amount": proposal.target_amount,
            "current_amount": proposal.current_amount,
            "status": proposal.status,
            "created_at": proposal.created_at.isoformat(),
            "deadline": proposal.deadline.isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch proposal {proposal_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/proposals/<int:proposal_id>/groups', methods=['POST'])
@jwt_required()
@csrf.exempt
def create_group(proposal_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        group = collaboration_service.create_group(proposal_id, user_id, data)
        return jsonify({"message": "Group created successfully", "group_id": group.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to create group for proposal {proposal_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/proposals/<int:proposal_id>/groups', methods=['GET'])
def get_groups(proposal_id):
    try:
        groups = collaboration_service.get_groups_by_proposal(proposal_id)
        return jsonify([{
            "id": g.id,
            "proposal_id": g.proposal_id,
            "name": g.name,
            "created_at": g.created_at.isoformat()
        } for g in groups]), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch groups for proposal {proposal_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/groups/<int:group_id>/invest', methods=['POST'])
@jwt_required()
@csrf.exempt
def invest_in_group(group_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        investment = collaboration_service.create_investment(group_id, user_id, data)
        return jsonify({"message": "Investment successful", "investment_id": investment.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to invest in group {group_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/groups/<int:group_id>/investments', methods=['GET'])
def get_investments(group_id):
    try:
        investments = collaboration_service.get_investments_by_group(group_id)
        return jsonify([{
            "id": i.id,
            "group_id": i.group_id,
            "user_id": i.user_id,
            "amount": i.amount,
            "created_at": i.created_at.isoformat()
        } for i in investments]), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch investments for group {group_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/groups/<int:group_id>/chat', methods=['GET'])
@jwt_required()
def get_chat_history(group_id):
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    try:
        messages = chat_service.get_chat_history(group_id, user_id, page, per_page)
        return jsonify([{
            "id": m.id,
            "group_id": m.group_id,
            "user_id": m.user_id,
            "message_type": m.message_type,
            "message": m.message,
            "sent_at": m.sent_at.isoformat()
        } for m in messages]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to fetch chat history for group {group_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/groups/<int:group_id>/chat', methods=['POST'])
@jwt_required()
@csrf.exempt
def send_chat_message(group_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        message = chat_service.send_message(group_id, user_id, data)
        return jsonify({"message": "Message sent successfully", "message_id": message.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to send chat message in group {group_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/groups/<int:group_id>/vote', methods=['POST'])
@jwt_required()
@csrf.exempt
def cast_vote(group_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        vote = vote_service.cast_vote(group_id, user_id, data)
        return jsonify({"message": "Vote cast successfully", "vote_id": vote.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to cast vote in group {group_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/groups/<int:group_id>/votes', methods=['GET'])
@jwt_required()
def get_votes(group_id):
    user_id = get_jwt_identity()
    try:
        votes = vote_service.get_votes_by_group(group_id, user_id)
        return jsonify([{
            "id": v.id,
            "group_id": v.group_id,
            "user_id": v.user_id,
            "proposal_option": v.proposal_option,
            "created_at": v.created_at.isoformat()
        } for v in votes]), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch votes for group {group_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500