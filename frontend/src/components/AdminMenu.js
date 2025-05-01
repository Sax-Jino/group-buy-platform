import React from 'react';
import { Menu } from 'antd';
import { Link } from 'react-router-dom';
import {
  DashboardOutlined,
  UserOutlined,
  ShopOutlined,
  DollarOutlined,
  AuditOutlined,
  SettingOutlined,
  LineChartOutlined
} from '@ant-design/icons';

const AdminMenu = () => {
  return (
    <Menu mode="inline">
      <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
        <Link to="/admin/dashboard">儀表板</Link>
      </Menu.Item>
      <Menu.Item key="users" icon={<UserOutlined />}>
        <Link to="/admin/users">用戶管理</Link>
      </Menu.Item>
      <Menu.Item key="products" icon={<ShopOutlined />}>
        <Link to="/admin/products">商品管理</Link>
      </Menu.Item>
      <Menu.Item key="settlements" icon={<DollarOutlined />}>
        <Link to="/settlements">結算管理</Link>
      </Menu.Item>
      <Menu.Item key="audit" icon={<AuditOutlined />}>
        <Link to="/audit">審計管理</Link>
      </Menu.Item>
      <Menu.Item key="financial-reports" icon={<LineChartOutlined />}>
        <Link to="/financial-reports">財務報表</Link>
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        <Link to="/admin/settings">系統設置</Link>
      </Menu.Item>
    </Menu>
  );
};

export default AdminMenu;