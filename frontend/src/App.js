import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './store';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import ProductPage from './pages/ProductPage';
import OrderPage from './pages/OrderPage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import CollaborationPage from './pages/CollaborationPage';
import RecipientPage from './pages/RecipientPage';
import CheckoutPage from './pages/CheckoutPage';
import PaymentPage from './pages/PaymentPage';
import CartPage from './pages/CartPage';
import Register from './pages/Register';
import NotificationHandler from './components/NotificationHandler';
import './styles/global.css';

function App() {
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
                            <Route path="/orders" element={<OrderPage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/register" element={<Register />} />
                            <Route path="/profile" element={<ProfilePage />} />
                            <Route path="/collaborations" element={<CollaborationPage />} />
                            <Route path="/recipients" element={<RecipientPage />} />
                            <Route path="/checkout" element={<CheckoutPage />} />
                            <Route path="/orders/:orderId/payment" element={<PaymentPage />} />
                            <Route path="/cart" element={<CartPage />} />
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </Router>
        </Provider>
    );
}

export default App;