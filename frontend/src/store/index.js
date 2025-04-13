import { configureStore } from '@reduxjs/toolkit';
import collaborationReducer from './reducers/collaborationReducer';

const store = configureStore({
    reducer: {
        collaboration: collaborationReducer
    }
});

export default store;