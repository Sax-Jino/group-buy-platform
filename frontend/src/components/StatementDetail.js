import React, { useState, useEffect } from 'react';
import { Table, Descriptions, Tag, Typography, Divider } from 'antd';
import { format } from 'date-fns';
import { fetchWithToken } from '../utils/api';

const { Title, Text } = Typography;

const StatementDetail = ({ settlementId }) => {
  const [loading, setLoading] = useState(false);
  const [statement, setStatement] = useState(null);

  useEffect(() => {
    if (settlementId) {
      fetchStatement();
    }
  }, [settlementId]);

  const fetchStatement = async () => {
    try {
      setLoading(true);
      const response = await fetchWithToken(`/api/settlements/${settlementId}/statement`);
      setStatement(response.data);
    } catch (error) {
      console.error('載入對帳單失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!statement) {
    return null;
  }

  const orderColumns = [
    {
      title: '訂單編號',
      dataIndex: 'order_id',
      key: 'order_id',
    },
    {
      title: '出貨日期',
      dataIndex: 'shipped_at',
      key: 'shipped_at',
      render: (date) => date ? format(new Date(date), 'yyyy-MM-dd') : '-',
    },
    {
      title: '物流單號',
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      render: (number) => number || '-',
    },
    {
      title: '金額',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => `NT$ ${amount.toLocaleString()}`,
    },
  ];

  return (
    <div className="statement-detail">
      <Title level={4}>對帳單 #{statement.id}</Title>
      <Divider />
      
      <Descriptions title="基本資訊" column={2}>
        <Descriptions.Item label="期別">{statement.period}</Descriptions.Item>
        <Descriptions.Item label="類型">
          <Tag color={statement.statement_type === 'supplier' ? 'blue' : 'green'}>
            {statement.statement_type === 'supplier' ? '供應商' : '團媽'}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="總訂單數">{statement.total_orders}</Descriptions.Item>
        <Descriptions.Item label="總金額">NT$ {statement.total_amount.toLocaleString()}</Descriptions.Item>
        <Descriptions.Item label="異議期限">
          {format(new Date(statement.dispute_deadline), 'yyyy-MM-dd HH:mm')}
        </Descriptions.Item>
        <Descriptions.Item label="狀態">
          <Tag color={statement.is_finalized ? 'green' : 'orange'}>
            {statement.is_finalized ? '已確認' : '待確認'}
          </Tag>
        </Descriptions.Item>
      </Descriptions>

      <Divider />
      <Title level={5}>費用明細</Title>
      <Descriptions column={2}>
        <Descriptions.Item label="手續費率">
          {(statement.commission_details.rate * 100).toFixed(1)}%
        </Descriptions.Item>
        <Descriptions.Item label="手續費總額">
          NT$ {statement.commission_details.amount.toLocaleString()}
        </Descriptions.Item>
        <Descriptions.Item label="稅金">
          NT$ {statement.tax_details.amount.toLocaleString()}
        </Descriptions.Item>
      </Descriptions>

      {statement.return_deductions.length > 0 && (
        <>
          <Divider />
          <Title level={5}>退貨扣款</Title>
          <Table
            size="small"
            dataSource={statement.return_deductions}
            columns={[
              {
                title: '訂單編號',
                dataIndex: 'order_id',
                key: 'order_id',
              },
              {
                title: '扣款金額',
                dataIndex: 'amount',
                key: 'amount',
                render: (amount) => `NT$ ${amount.toLocaleString()}`,
              },
              {
                title: '狀態',
                dataIndex: 'status',
                key: 'status',
                render: (status) => (
                  <Tag color={status === 'processed' ? 'green' : 'gold'}>
                    {status === 'processed' ? '已處理' : '處理中'}
                  </Tag>
                ),
              },
            ]}
            pagination={false}
          />
        </>
      )}

      <Divider />
      <Title level={5}>訂單明細</Title>
      <Table
        size="small"
        dataSource={statement.shipping_details}
        columns={orderColumns}
        pagination={false}
      />

      {statement.is_disputed && (
        <>
          <Divider />
          <Title level={5}>異議記錄</Title>
          <div className="dispute-record">
            <Text type="secondary">
              提交時間：{format(new Date(statement.dispute_details.created_at), 'yyyy-MM-dd HH:mm')}
            </Text>
            <p>{statement.dispute_details.content}</p>
          </div>
        </>
      )}
    </div>
  );
};

export default StatementDetail;