import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null, // { id, username, role, ... }
  userRole: null // 方便直接取用
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
      state.userRole = action.payload?.role || null;
    },
    clearUser: (state) => {
      state.user = null;
      state.userRole = null;
    }
  }
});

export const { setUser, clearUser } = authSlice.actions;
export default authSlice.reducer;
