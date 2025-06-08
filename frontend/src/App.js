import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Provider, useDispatch } from 'react-redux';
import store from './store';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import ProductPage from './pages/ProductPage';
import ProductDetailPage from './pages/ProductDetailPage';
import OrderPage from './pages/OrderPage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import CollaborationPage from './pages/CollaborationPage';
import RecipientPage from './pages/RecipientPage';
import CheckoutPage from './pages/CheckoutPage';
import PaymentPage from './pages/PaymentPage';
import CartPage from './pages/CartPage';
import Register from './pages/Register';
import SettlementManagementPage from './pages/SettlementManagementPage';
import NotificationHandler from './components/NotificationHandler';
import AuditManagementPage from './pages/AuditManagementPage';
import AuditReportDetailPage from './pages/AuditReportDetailPage';
import FinancialReportPage from './pages/FinancialReportPage';
import PrivateRoute from './components/PrivateRoute';
import { setUser, clearUser } from './store/reducers/authReducer';
import { getProfile } from './api';
import './styles/global.css';

function App() {
    const dispatch = useDispatch();
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            getProfile(token)
                .then(user => {
                    dispatch(setUser(user));
                })
                .catch(() => {
                    dispatch(clearUser());
                    localStorage.removeItem('token');
                });
        } else {
            dispatch(clearUser());
        }
    }, [dispatch]);

    return (
        <Provider store={store}>
            <Router>
                <div className="app">
                    <Header />
                    <NotificationHandler />
                    <main>
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/products" element={<ProductPage />} />
                            <Route path="/products/:productId" element={<ProductDetailPage />} />
                            <Route path="/orders" element={<OrderPage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/register" element={<Register />} />
                            <Route path="/profile" element={<ProfilePage />} />
                            <Route path="/collaborations" element={<CollaborationPage />} />
                            <Route path="/recipients" element={<RecipientPage />} />
                            <Route path="/checkout" element={<CheckoutPage />} />
                            <Route path="/orders/:orderId/payment" element={<PaymentPage />} />
                            <Route path="/cart" element={<CartPage />} />
                            <Route 
                                path="/settlements" 
                                element={
                                    <PrivateRoute>
                                        <SettlementManagementPage />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="/audit" 
                                element={
                                    <PrivateRoute requiredRole="admin">
                                        <AuditManagementPage />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="/audit/reports/:reportId" 
                                element={
                                    <PrivateRoute requiredRole="admin">
                                        <AuditReportDetailPage />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="/financial-reports" 
                                element={
                                    <PrivateRoute requiredRole="admin">
                                        <FinancialReportPage />
                                    </PrivateRoute>
                                } 
                            />
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </Router>
        </Provider>
    );
}

export default App;