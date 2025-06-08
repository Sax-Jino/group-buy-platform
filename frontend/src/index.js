import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/global.css';
import ErrorBoundary from './components/ErrorBoundary';
import ReduxProvider from './ReduxProvider';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <ReduxProvider>
            <ErrorBoundary>
                <App />
            </ErrorBoundary>
        </ReduxProvider>
    </React.StrictMode>
);