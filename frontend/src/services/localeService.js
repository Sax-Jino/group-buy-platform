import api from './api';

export const getLocales = async () => {
    try {
        const response = await api.get('/locale');
        return response.data;
    } catch (error) {
        console.error('Failed to get locales:', error);
        throw error;
    }
};

export const setLocale = async (locale) => {
    try {
        const response = await api.post('/locale', { locale });
        return response.data;
    } catch (error) {
        console.error('Failed to set locale:', error);
        throw error;
    }
};
