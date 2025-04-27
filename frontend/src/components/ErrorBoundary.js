import React from 'react';
import '../styles/ErrorBoundary.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('錯誤邊界捕獲到錯誤:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>很抱歉，發生了一些問題</h2>
          <p>請重新整理頁面或稍後再試</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;