import { configureStore } from '@reduxjs/toolkit';
import collaborationReducer from './reducers/collaborationReducer';
import cartReducer from './reducers/cartReducer';

const store = configureStore({
    reducer: {
        collaboration: collaborationReducer,
        cart: cartReducer
    }
});

export default store;