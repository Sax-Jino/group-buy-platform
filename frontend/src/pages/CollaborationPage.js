import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/CollaborationPage.css';

const CollaborationPage = () => {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProposals = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/collaboration/proposals');
        const data = await response.json();
        setProposals(data);
      } catch (err) {
        console.error('Failed to fetch proposals:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProposals();
  }, []);

  return (
    <div className="collaboration-page">
      <h2>協作提案</h2>
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="proposal-list">
          {proposals.map((proposal) => (
            <div key={proposal.id} className="proposal-card">
              <h3>{proposal.title}</h3>
              <p>{proposal.description}</p>
              <p>目標金額: NT$ {proposal.target_amount}</p>
              <p>目前金額: NT$ {proposal.current_amount}</p>
              <p>截止日期: {new Date(proposal.deadline).toLocaleDateString()}</p>
              <p>狀態: {proposal.status}</p>
              <button>參與協作</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CollaborationPage;