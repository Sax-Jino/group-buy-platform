from extensions import db
from models.collaboration_proposal import CollaborationProposal
from models.collaboration_group import CollaborationGroup
from models.collaboration_investment import CollaborationInvestment
from models.user import User
from config import Config
from datetime import datetime
from flask import current_app
from services.notification_service import NotificationService

class CollaborationService:
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
        
        try:
            proposal = CollaborationProposal(
                initiator_id=user_id,
                title=data['title'],
                description=data['description'],
                target_amount=target_amount,
                deadline=deadline
            )
            db.session.add(proposal)
            db.session.commit()
            from extensions import event_emitter
            event_emitter.emit('proposal_created', proposal_id=proposal.id, user_id=user_id)
            current_app.logger.info(f"Proposal {proposal.id} created by user {user_id}")
            return proposal
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create proposal: {e}")
            raise

    def get_all_proposals(self):
        try:
            proposals = CollaborationProposal.query.filter_by(status='open').order_by(CollaborationProposal.created_at.desc()).all()
            current_app.logger.info("Fetched all open proposals")
            return proposals
        except Exception as e:
            current_app.logger.error(f"Failed to fetch proposals: {e}")
            raise

    def get_proposal_by_id(self, proposal_id):
        try:
            proposal = CollaborationProposal.query.get(proposal_id)
            if not proposal:
                current_app.logger.warning(f"Proposal {proposal_id} not found")
                raise ValueError("Proposal not found")
            current_app.logger.info(f"Fetched proposal {proposal_id}")
            return proposal
        except Exception as e:
            current_app.logger.error(f"Failed to fetch proposal {proposal_id}: {e}")
            raise

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
        
        try:
            group = CollaborationGroup(
                proposal_id=proposal_id,
                name=data['name']
            )
            db.session.add(group)
            db.session.commit()
            from extensions import event_emitter
            event_emitter.emit('group_created', proposal_id=proposal_id, group_id=group.id, user_id=user_id)
            current_app.logger.info(f"Group {group.id} created for proposal {proposal_id} by user {user_id}")
            return group
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create group for proposal {proposal_id}: {e}")
            raise

    def get_groups_by_proposal(self, proposal_id):
        try:
            if not CollaborationProposal.query.get(proposal_id):
                raise ValueError("Proposal not found")
            groups = CollaborationGroup.query.filter_by(proposal_id=proposal_id).all()
            current_app.logger.info(f"Fetched groups for proposal {proposal_id}")
            return groups
        except Exception as e:
            current_app.logger.error(f"Failed to fetch groups for proposal {proposal_id}: {e}")
            raise

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
        
        try:
            investment = CollaborationInvestment(
                group_id=group_id,
                user_id=user_id,
                amount=amount
            )
            proposal.current_amount += amount
            old_status = proposal.status
            if proposal.current_amount >= proposal.target_amount:
                proposal.status = 'funded'
            
            db.session.add(investment)
            db.session.commit()
            from extensions import event_emitter
            event_emitter.emit('investment_made', proposal_id=proposal.id, group_id=group_id, user_id=user_id, amount=amount)
            current_app.logger.info(f"Investment of {amount} made by user {user_id} in group {group_id}")
            
            if proposal.status != old_status:
                event_emitter.emit('proposal_status_updated', proposal_id=proposal.id, status=proposal.status)
                NotificationService().notify_group_members(
                    group_id,
                    f"Proposal {proposal.title} is now funded! Please vote on production."
                )
                current_app.logger.info(f"Proposal {proposal.id} status updated to funded")
            
            return investment
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create investment in group {group_id}: {e}")
            raise

    def get_investments_by_group(self, group_id):
        try:
            if not CollaborationGroup.query.get(group_id):
                raise ValueError("Group not found")
            investments = CollaborationInvestment.query.filter_by(group_id=group_id).all()
            current_app.logger.info(f"Fetched investments for group {group_id}")
            return investments
        except Exception as e:
            current_app.logger.error(f"Failed to fetch investments for group {group_id}: {e}")
            raise