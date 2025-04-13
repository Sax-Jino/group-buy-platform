from extensions import db
from models.collaboration_vote import CollaborationVote
from models.collaboration_group import CollaborationGroup
from models.collaboration_investment import CollaborationInvestment
from models.collaboration_proposal import CollaborationProposal
from config import Config
from flask import current_app
from services.notification_service import NotificationService

class VoteService:
    def cast_vote(self, group_id, user_id, data):
        required_fields = ['proposal_option']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        allowed_options = ['yes', 'no']
        if data['proposal_option'] not in allowed_options:
            raise ValueError(f"Invalid proposal option. Allowed: {allowed_options}")
        
        group = CollaborationGroup.query.get_or_404(group_id)
        if not db.session.query(CollaborationInvestment).filter_by(group_id=group_id, user_id=user_id).first():
            raise ValueError("User is not a member of this group")
        
        proposal = group.proposal
        if proposal.status != 'funded':
            raise ValueError("Voting is only allowed for funded proposals")
        
        existing_vote = CollaborationVote.query.filter_by(group_id=group_id, user_id=user_id).first()
        if existing_vote:
            raise ValueError("User has already voted in this group")
        
        try:
            vote = CollaborationVote(
                group_id=group_id,
                user_id=user_id,
                proposal_option=data['proposal_option']
            )
            db.session.add(vote)
            db.session.commit()
            
            from extensions import event_emitter
            event_emitter.emit('vote_cast', group_id=group_id, user_id=user_id, proposal_option=data['proposal_option'])
            current_app.logger.info(f"Vote cast in group {group_id} by user {user_id}: {data['proposal_option']}")
            
            self._check_vote_result(group_id, proposal)
            return vote
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to cast vote in group {group_id}: {e}")
            raise

    def get_votes_by_group(self, group_id, user_id):
        try:
            group = CollaborationGroup.query.get_or_404(group_id)
            if not db.session.query(CollaborationInvestment).filter_by(group_id=group_id, user_id=user_id).first():
                raise ValueError("User is not a member of this group")
            votes = CollaborationVote.query.filter_by(group_id=group_id).all()
            current_app.logger.info(f"Fetched votes for group {group_id} by user {user_id}")
            return votes
        except Exception as e:
            current_app.logger.error(f"Failed to fetch votes for group {group_id}: {e}")
            raise

    def _check_vote_result(self, group_id, proposal):
        try:
            total_members = CollaborationInvestment.query.filter_by(group_id=group_id).count()
            votes = CollaborationVote.query.filter_by(group_id=group_id).all()
            yes_votes = sum(1 for v in votes if v.proposal_option == 'yes')
            
            if len(votes) == total_members:
                if yes_votes / total_members >= Config.VOTE_PASS_THRESHOLD:
                    old_status = proposal.status
                    proposal.status = 'production'
                    db.session.commit()
                    from extensions import event_emitter
                    event_emitter.emit('proposal_status_updated', proposal_id=proposal.id, status='production')
                    NotificationService().notify_group_members(
                        group_id,
                        f"Proposal {proposal.title} has entered production phase!"
                    )
                    current_app.logger.info(f"Proposal {proposal.id} status updated to production (yes: {yes_votes}/{total_members})")
                else:
                    current_app.logger.info(f"Proposal {proposal.id} voting completed but not enough yes votes (yes: {yes_votes}/{total_members})")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to check vote result for group {group_id}: {e}")
            raise