import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Select } from 'antd';
import { changeLanguage } from '../store/actions/languageActions';
import { setLocale } from '../services/localeService';

const { Option } = Select;

const LanguageSelector = () => {
    const dispatch = useDispatch();
    const currentLanguage = useSelector(state => state.language.currentLanguage);    const handleLanguageChange = async (value) => {
        try {
            await setLocale(value);
            dispatch(changeLanguage(value));
        } catch (error) {
            console.error('Failed to change language:', error);
        }
    };

    return (
        <Select
            value={currentLanguage}
            onChange={handleLanguageChange}
            style={{ width: 120 }}
            className="language-selector"
        >
            <Option value="zh_TW">繁體中文</Option>
            <Option value="zh_CN">简体中文</Option>
            <Option value="en">English</Option>
        </Select>
    );
};

export default LanguageSelector;
