import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    notifications: [],
    proposals: [],
    groups: []
};

const collaborationSlice = createSlice({
    name: 'collaboration',
    initialState,
    reducers: {
        setNotification: (state, action) => {
            state.notifications = [...state.notifications, action.payload];
        },
        setProposals: (state, action) => {
            state.proposals = action.payload;
        },
        setGroups: (state, action) => {
            state.groups = action.payload;
        }
    }
});

export const { setNotification, setProposals, setGroups } = collaborationSlice.actions;
export default collaborationSlice.reducer;