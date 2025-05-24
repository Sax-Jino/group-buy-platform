import { setLanguage } from '../reducers/languageReducer';

export const changeLanguage = (language) => (dispatch) => {
    // 更新後端 API 請求的語言設置
    localStorage.setItem('language', language);
    // 更新 Redux store
    dispatch(setLanguage(language));
};
