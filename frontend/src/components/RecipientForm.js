import React, { useState, useEffect } from 'react';
import '../styles/RecipientForm.css';

const RecipientForm = ({ onSubmit, onCancel, initialData }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form className="recipient-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="name">收貨人姓名</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          maxLength={100}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="phone">手機號碼</label>
        <input
          type="tel"
          id="phone"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          required
          pattern="09[0-9]{8}"
          maxLength={10}
          placeholder="09xxxxxxxx"
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="address">收貨地址</label>
        <input
          type="text"
          id="address"
          name="address"
          value={formData.address}
          onChange={handleChange}
          required
          maxLength={200}
        />
      </div>
      
      <div className="form-actions">
        <button type="submit">{initialData ? '更新' : '新增'}</button>
        <button type="button" onClick={onCancel}>取消</button>
      </div>
    </form>
  );
};

export default RecipientForm;