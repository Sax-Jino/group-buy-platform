import { createStore, combineReducers, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import collaborationReducer from './reducers/collaborationReducer';

const rootReducer = combineReducers({
    collaboration: collaborationReducer
});

const store = createStore(rootReducer, applyMiddleware(thunk));

export default store;