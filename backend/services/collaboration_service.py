from extensions import db
from models.collaboration_proposal import CollaborationProposal
from models.collaboration_group import CollaborationGroup
from models.collaboration_investment import CollaborationInvestment
from models.user import User
from config import Config
from datetime import datetime

class CollaborationService:
    # 提案相關方法（來自第8批）
    def create_proposal(self, user_id, data):
        required_fields = ['title', 'description', 'target_amount', 'deadline']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        target_amount = float(data['target_amount'])
        if target_amount <= 0:
            raise ValueError("Target amount must be positive")
        
        deadline = datetime.fromisoformat(data['deadline'])
        if deadline <= datetime.utcnow():
            raise ValueError("Deadline must be in the future")
        
        proposal = CollaborationProposal(
            initiator_id=user_id,
            title=data['title'],
            description=data['description'],
            target_amount=target_amount,
            deadline=deadline
        )
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def get_all_proposals(self):
        return CollaborationProposal.query.filter_by(status='open').order_by(CollaborationProposal.created_at.desc()).all()

    def get_proposal_by_id(self, proposal_id):
        return CollaborationProposal.query.get(proposal_id)

    # 小組相關方法（來自第9批）
    def create_group(self, proposal_id, user_id, data):
        required_fields = ['name']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        proposal = CollaborationProposal.query.get(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
        if proposal.initiator_id != user_id:
            raise ValueError("Only the proposal initiator can create groups")
        if proposal.status != 'open':
            raise ValueError("Cannot create groups for non-open proposals")
        
        group = CollaborationGroup(
            proposal_id=proposal_id,
            name=data['name']
        )
        db.session.add(group)
        db.session.commit()
        return group

    def get_groups_by_proposal(self, proposal_id):
        if not CollaborationProposal.query.get(proposal_id):
            raise ValueError("Proposal not found")
        return CollaborationGroup.query.filter_by(proposal_id=proposal_id).all()

    # 投資相關方法（新增）
    def create_investment(self, group_id, user_id, data):
        required_fields = ['amount']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        amount = float(data['amount'])
        if amount < Config.MIN_INVESTMENT_AMOUNT:
            raise ValueError(f"Investment amount must be at least {Config.MIN_INVESTMENT_AMOUNT}")
        
        group = CollaborationGroup.query.get(group_id)
        if not group:
            raise ValueError("Group not found")
        
        proposal = group.proposal
        if proposal.status != 'open':
            raise ValueError("Cannot invest in a non-open proposal")
        
        investment = CollaborationInvestment(
            group_id=group_id,
            user_id=user_id,
            amount=amount
        )
        proposal.current_amount += amount
        if proposal.current_amount >= proposal.target_amount:
            proposal.status = 'funded'
        
        db.session.add(investment)
        db.session.commit()
        return investment

    def get_investments_by_group(self, group_id):
        if not CollaborationGroup.query.get(group_id):
            raise ValueError("Group not found")
        return CollaborationInvestment.query.filter_by(group_id=group_id).all()