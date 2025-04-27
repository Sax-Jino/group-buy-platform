import React, { useState, useEffect } from 'react';
import '../styles/TrackingDialog.css';

const TrackingDialog = ({ orderId, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [trackingInfo, setTrackingInfo] = useState(null);

  useEffect(() => {
    const fetchTrackingInfo = async () => {
      const token = localStorage.getItem('token');
      try {
        const response = await fetch(
          `http://localhost:5000/api/orders/${orderId}/tracking`,
          { headers: { 'Authorization': `Bearer ${token}` } }
        );
        if (!response.ok) {
          throw new Error('無法載入物流資訊');
        }
        const data = await response.json();
        setTrackingInfo(data);
      } catch (err) {
        console.error('Failed to fetch tracking info:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (orderId) {
      fetchTrackingInfo();
    }
  }, [orderId]);

  if (loading) {
    return (
      <div className="tracking-dialog">
        <div className="tracking-content">
          <div className="loading">載入中...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tracking-dialog">
        <div className="tracking-content">
          <div className="error-message">{error}</div>
          <button className="close-button" onClick={onClose}>關閉</button>
        </div>
      </div>
    );
  }

  return (
    <div className="tracking-dialog">
      <div className="tracking-content">
        <button className="close-button" onClick={onClose}>&times;</button>
        
        <div className="tracking-header">
          <h3>物流追蹤</h3>
          <div className="tracking-info">
            <p>物流公司：{trackingInfo.logistics_company}</p>
            <p>追蹤編號：{trackingInfo.tracking_number}</p>
          </div>
        </div>

        <div className="tracking-timeline">
          {trackingInfo.history.map((event, index) => (
            <div 
              key={index} 
              className={`timeline-item ${index === trackingInfo.history.length - 1 ? 'current' : ''}`}
            >
              <div className="timeline-point"></div>
              <div className="timeline-content">
                <div className="timeline-info">
                  <span className="timeline-status">{event.status}</span>
                  <span className="timeline-time">
                    {new Date(event.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="timeline-location">{event.location}</div>
                <div className="timeline-description">{event.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TrackingDialog;