import { configureStore } from '@reduxjs/toolkit';
import collaborationReducer from './reducers/collaborationReducer';
import cartReducer from './reducers/cartReducer';
import languageReducer from './reducers/languageReducer';

const store = configureStore({
    reducer: {
        collaboration: collaborationReducer,
        cart: cartReducer,
        language: languageReducer
    }
});

export default store;