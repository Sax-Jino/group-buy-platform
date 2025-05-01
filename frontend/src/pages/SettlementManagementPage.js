import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Tag, Modal, message, Tabs, Card, Statistic, Row, Col } from 'antd';
import { DollarOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { format } from 'date-fns';
import { fetchWithToken } from '../utils/api';
import StatementDetail from '../components/StatementDetail';

const { TabPane } = Tabs;

const SettlementManagementPage = () => {
  const [loading, setLoading] = useState(false);
  const [settlements, setSettlements] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedSettlement, setSelectedSettlement] = useState(null);
  const [statementModalVisible, setStatementModalVisible] = useState(false);
  const [disputeModalVisible, setDisputeModalVisible] = useState(false);
  const [disputeContent, setDisputeContent] = useState('');
  const navigate = useNavigate();

  // 獲取結算列表
  const fetchSettlements = async () => {
    try {
      setLoading(true);
      const response = await fetchWithToken('/api/settlements');
      setSettlements(response.data);
    } catch (error) {
      message.error('載入結算資料失敗');
    } finally {
      setLoading(false);
    }
  };

  // 獲取平台總覽
  const fetchSummary = async () => {
    try {
      const response = await fetchWithToken('/api/settlements/summary');
      setSummary(response.data);
    } catch (error) {
      message.error('載入平台總覽失敗');
    }
  };

  useEffect(() => {
    fetchSettlements();
    fetchSummary();
  }, []);

  // 確認對帳單
  const handleConfirm = async (settlementId) => {
    try {
      await fetchWithToken(`/api/settlements/${settlementId}/confirm`, {
        method: 'POST'
      });
      message.success('對帳單確認成功');
      fetchSettlements();
    } catch (error) {
      message.error('對帳單確認失敗');
    }
  };

  // 提交異議
  const handleDispute = async () => {
    if (!disputeContent) {
      message.error('請輸入異議內容');
      return;
    }

    try {
      await fetchWithToken(`/api/settlements/${selectedSettlement.id}/dispute`, {
        method: 'POST',
        body: JSON.stringify({ content: disputeContent })
      });
      message.success('異議提交成功');
      setDisputeModalVisible(false);
      setDisputeContent('');
      fetchSettlements();
    } catch (error) {
      message.error('異議提交失敗');
    }
  };

  // 處理撥款
  const handlePayment = async (settlementId) => {
    Modal.confirm({
      title: '確認撥款',
      icon: <ExclamationCircleOutlined />,
      content: '確定要處理此筆撥款嗎？',
      onOk: async () => {
        try {
          await fetchWithToken('/api/settlements/process-payment', {
            method: 'POST',
            body: JSON.stringify({ settlement_id: settlementId })
          });
          message.success('撥款處理成功');
          fetchSettlements();
        } catch (error) {
          message.error('撥款處理失敗');
        }
      }
    });
  };

  const columns = [
    {
      title: '期別',
      dataIndex: 'period',
      key: 'period',
    },
    {
      title: '類型',
      dataIndex: 'settlement_type',
      key: 'type',
      render: (type) => (
        <Tag color={type === 'supplier' ? 'blue' : 'green'}>
          {type === 'supplier' ? '供應商' : '團媽'}
        </Tag>
      ),
    },
    {
      title: '總金額',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount) => `NT$ ${amount.toLocaleString()}`,
    },
    {
      title: '淨額',
      dataIndex: 'net_amount',
      key: 'net_amount',
      render: (amount) => `NT$ ${amount.toLocaleString()}`,
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          pending: { text: '待確認', color: 'orange' },
          confirmed: { text: '已確認', color: 'blue' },
          paid: { text: '已撥款', color: 'green' },
          disputed: { text: '有異議', color: 'red' },
        };
        return (
          <Tag color={statusMap[status].color}>
            {statusMap[status].text}
          </Tag>
        );
      },
    },
    {
      title: '建立時間',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => format(new Date(date), 'yyyy-MM-dd HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <span>
          <Button 
            type="link" 
            onClick={() => {
              setSelectedSettlement(record);
              setStatementModalVisible(true);
            }}
          >
            查看明細
          </Button>
          {record.status === 'pending' && (
            <>
              <Button 
                type="link" 
                onClick={() => handleConfirm(record.id)}
              >
                確認
              </Button>
              <Button 
                type="link" 
                danger
                onClick={() => {
                  setSelectedSettlement(record);
                  setDisputeModalVisible(true);
                }}
              >
                異議
              </Button>
            </>
          )}
          {record.status === 'confirmed' && (
            <Button 
              type="link"
              onClick={() => handlePayment(record.id)}
            >
              撥款
            </Button>
          )}
        </span>
      ),
    },
  ];

  return (
    <div className="settlement-management">
      <Tabs defaultActiveKey="summary">
        <TabPane tab="平台總覽" key="summary">
          {summary && (
            <div className="summary-content">
              <Row gutter={16}>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="總營收"
                      value={summary.total_revenue}
                      prefix={<DollarOutlined />}
                      precision={2}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="已結算金額"
                      value={summary.settled_amount}
                      prefix={<DollarOutlined />}
                      precision={2}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="未結算金額"
                      value={summary.unsettled_amount}
                      prefix={<DollarOutlined />}
                      precision={2}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="平台利潤"
                      value={summary.platform_profit}
                      prefix={<DollarOutlined />}
                      precision={2}
                    />
                  </Card>
                </Col>
              </Row>
            </div>
          )}
        </TabPane>
        <TabPane tab="結算列表" key="list">
          <Table
            columns={columns}
            dataSource={settlements}
            loading={loading}
            rowKey="id"
          />
        </TabPane>
      </Tabs>

      <Modal
        title="對帳單明細"
        visible={statementModalVisible}
        onCancel={() => setStatementModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedSettlement && (
          <StatementDetail settlementId={selectedSettlement.id} />
        )}
      </Modal>

      <Modal
        title="提交異議"
        visible={disputeModalVisible}
        onOk={handleDispute}
        onCancel={() => {
          setDisputeModalVisible(false);
          setDisputeContent('');
        }}
      >
        <textarea
          rows={4}
          value={disputeContent}
          onChange={(e) => setDisputeContent(e.target.value)}
          placeholder="請輸入異議內容..."
          style={{ width: '100%' }}
        />
      </Modal>
    </div>
  );
};

export default SettlementManagementPage;