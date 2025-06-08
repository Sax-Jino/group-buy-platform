import { configureStore } from '@reduxjs/toolkit';
import collaborationReducer from './reducers/collaborationReducer';
import cartReducer from './reducers/cartReducer';
import languageReducer from './reducers/languageReducer';
import authReducer from './reducers/authReducer';

const store = configureStore({
    reducer: {
        collaboration: collaborationReducer,
        cart: cartReducer,
        language: languageReducer,
        auth: authReducer // 新增 auth reducer
    }
});

export default store;