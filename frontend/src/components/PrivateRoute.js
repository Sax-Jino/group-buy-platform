import React from 'react';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';

// 這個元件會根據登入狀態與角色權限決定是否渲染子元件
const PrivateRoute = ({ children, requiredRole }) => {
  const user = useSelector((state) => state.auth.user);
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (requiredRole && (!user || user.role !== requiredRole)) {
    return <Navigate to="/" replace />;
  }
  return children;
};

export default PrivateRoute;
