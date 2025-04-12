from extensions import db
from models.collaboration_vote import CollaborationVote
from models.collaboration_group import CollaborationGroup
from models.collaboration_investment import CollaborationInvestment
from models.collaboration_proposal import CollaborationProposal
from config import Config

class VoteService:
    def cast_vote(self, group_id, user_id, data):
        required_fields = ['proposal_option']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")
        
        group = CollaborationGroup.query.get_or_404(group_id)
        if not db.session.query(CollaborationInvestment).filter_by(group_id=group_id, user_id=user_id).first():
            raise ValueError("User is not a member of this group")
        
        proposal = group.proposal
        if proposal.status != 'funded':
            raise ValueError("Voting is only allowed for funded proposals")
        
        # 檢查是否已投票
        existing_vote = CollaborationVote.query.filter_by(group_id=group_id, user_id=user_id).first()
        if existing_vote:
            raise ValueError("User has already voted in this group")
        
        vote = CollaborationVote(
            group_id=group_id,
            user_id=user_id,
            proposal_option=data['proposal_option']
        )
        db.session.add(vote)
        db.session.commit()
        
        # 檢查投票結果並更新提案狀態
        self._check_vote_result(group_id, proposal)
        return vote

    def get_votes_by_group(self, group_id, user_id):
        group = CollaborationGroup.query.get_or_404(group_id)
        if not db.session.query(CollaborationInvestment).filter_by(group_id=group_id, user_id=user_id).first():
            raise ValueError("User is not a member of this group")
        return CollaborationVote.query.filter_by(group_id=group_id).all()

    def _check_vote_result(self, group_id, proposal):
        total_members = CollaborationInvestment.query.filter_by(group_id=group_id).count()
        votes = CollaborationVote.query.filter_by(group_id=group_id).all()
        yes_votes = sum(1 for v in votes if v.proposal_option == 'yes')  # 假設'yes'表示同意生產
        
        if len(votes) == total_members:  # 所有人投票完成
            if yes_votes / total_members >= Config.VOTE_PASS_THRESHOLD:
                proposal.status = 'production'
                db.session.commit()