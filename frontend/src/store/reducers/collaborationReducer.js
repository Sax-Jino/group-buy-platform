import { createSlice } from '@reduxjs/toolkit';

const collaborationSlice = createSlice({
    name: 'collaboration',
    initialState: {
        notifications: [],
        proposals: [],
        groups: []
    },
    reducers: {
        setNotification(state, action) {
            state.notifications.push(action.payload);
        },
        setProposals(state, action) {
            state.proposals = action.payload;
        },
        setGroups(state, action) {
            state.groups = action.payload;
        }
    }
});

export const { setNotification, setProposals, setGroups } = collaborationSlice.actions;
export default collaborationSlice.reducer;