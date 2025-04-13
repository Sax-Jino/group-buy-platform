const initialState = {
    notifications: [],
    proposals: [],
    groups: []
};

const collaborationReducer = (state = initialState, action) => {
    switch (action.type) {
        case 'SET_NOTIFICATION':
            return {
                ...state,
                notifications: [...state.notifications, action.payload]
            };
        case 'SET_PROPOSALS':
            return {
                ...state,
                proposals: action.payload
            };
        case 'SET_GROUPS':
            return {
                ...state,
                groups: action.payload
            };
        default:
            return state;
    }
};

export default collaborationReducer;