import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    currentLanguage: localStorage.getItem('language') || 'zh_TW'
};

const languageSlice = createSlice({
    name: 'language',
    initialState,
    reducers: {
        setLanguage: (state, action) => {
            state.currentLanguage = action.payload;
            localStorage.setItem('language', action.payload);
        }
    }
});

export const { setLanguage } = languageSlice.actions;
export default languageSlice.reducer;
