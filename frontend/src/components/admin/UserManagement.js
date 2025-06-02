import React, { useState, useEffect } from 'react';
import { notification, Table, Button, Modal, Form, Input, Select, Tag } from 'antd';
import { UserOutlined, LockOutlined, WarningOutlined } from '@ant-design/icons';

const { Option } = Select;

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [form] = Form.useForm();
  
  // 檢查是否已有 SUPERADMIN
  const hasSuperAdmin = users.some(user => user.role === 'superadmin');
  
  useEffect(() => {
    fetchUsers();
  }, []);
  
  const fetchUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/admin/members', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data && data.data.members) {
          setUsers(data.data.members);
        }
      } else {
        notification.error({
          message: '載入失敗',
          description: '無法載入用戶列表'
        });
      }
    } catch (err) {
      console.error('載入用戶列表失敗:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleEdit = (user) => {
    setEditingUser(user);
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      name: user.name,
      role: user.role,
      phone: user.phone || '',
      line_id: user.line_id || '',
      is_active: user.is_active
    });
    setModalVisible(true);
  };
  
  const handleCreate = () => {
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };
  
  const handleCancel = () => {
    setModalVisible(false);
  };
  
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setConfirmLoading(true);
      
      // 檢查 SUPERADMIN 唯一性規則
      if (values.role === 'superadmin') {
        if (values.username !== 'JackeyChen') {
          notification.error({
            message: '錯誤',
            description: 'SUPERADMIN 角色僅允許唯一帳號 JackeyChen'
          });
          setConfirmLoading(false);
          return;
        }
        
        // 檢查是否已存在 SUPERADMIN（編輯自己除外）
        if (!editingUser || editingUser.role !== 'superadmin') {
          if (hasSuperAdmin) {
            notification.error({
              message: '錯誤',
              description: '系統已存在 SUPERADMIN，不可重複建立'
            });
            setConfirmLoading(false);
            return;
          }
        }
      }
      
      const token = localStorage.getItem('token');
      let url, method;
      
      if (editingUser) {
        url = `http://localhost:5000/api/admin/members/${editingUser.id}`;
        method = 'PUT';
      } else {
        url = 'http://localhost:5000/api/admin/members';
        method = 'POST';
      }
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        notification.success({
          message: '成功',
          description: editingUser ? '用戶更新成功' : '用戶創建成功'
        });
        setModalVisible(false);
        fetchUsers();
      } else {
        const data = await response.json();
        notification.error({
          message: '操作失敗',
          description: data.error || data.message || '請稍後再試'
        });
      }
    } catch (err) {
      console.error('表單提交出錯:', err);
    } finally {
      setConfirmLoading(false);
    }
  };
  
  const columns = [
    {
      title: '用戶名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role) => {
        let color = 'blue';
        if (role === 'admin') color = 'green';
        if (role === 'superadmin') color = 'red';
        if (role === 'supplier') color = 'purple';
        return <Tag color={color}>{role}</Tag>;
      }
    },
    {
      title: '狀態',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? '啟用' : '停用'}
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button type="link" onClick={() => handleEdit(record)}>
          編輯
        </Button>
      )
    }
  ];
  
  return (
    <div className="user-management">
      <div className="header-actions">
        <Button type="primary" onClick={handleCreate}>
          新增用戶
        </Button>
      </div>
      
      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
      />
      
      <Modal
        title={editingUser ? '編輯用戶' : '新增用戶'}
        visible={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCancel}
        confirmLoading={confirmLoading}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="username"
            label="用戶名"
            rules={[{ required: true, message: '請輸入用戶名' }]}
          >
            <Input prefix={<UserOutlined />} />
          </Form.Item>
          
          {!editingUser && (
            <Form.Item
              name="password"
              label="密碼"
              rules={[{ required: !editingUser, message: '請輸入密碼' }]}
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>
          )}
          
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: '請輸入Email' },
              { type: 'email', message: 'Email格式不正確' }
            ]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="name"
            label="姓名"
            rules={[{ required: true, message: '請輸入姓名' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '請選擇角色' }]}
          >
            <Select>
              <Option value="member">普通會員</Option>
              <Option value="admin">管理員</Option>
              <Option value="supplier">供應商</Option>
              <Option value="superadmin">SUPERADMIN</Option>
            </Select>
          </Form.Item>
          
          {form.getFieldValue('role') === 'superadmin' && (
            <div className="superadmin-warning">
              <WarningOutlined style={{ color: 'red', marginRight: '8px' }} />
              <span style={{ color: 'red' }}>
                SUPERADMIN 帳號必須為唯一的 JackeyChen，且系統只允許一個 SUPERADMIN
              </span>
            </div>
          )}
          
          <Form.Item
            name="phone"
            label="電話"
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="line_id"
            label="Line ID"
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="is_active"
            label="狀態"
            rules={[{ required: true, message: '請選擇狀態' }]}
            initialValue={true}
          >
            <Select>
              <Option value={true}>啟用</Option>
              <Option value={false}>停用</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;
