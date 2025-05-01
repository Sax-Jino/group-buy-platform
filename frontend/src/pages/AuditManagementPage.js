import React, { useState, useEffect } from 'react';
import { Table, Card, Tabs, Modal, Button, Form, Input, DatePicker, Tag, message } from 'antd';
import { FileSearchOutlined, AuditOutlined } from '@ant-design/icons';
import { format } from 'date-fns';
import { fetchWithToken } from '../utils/api';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { RangePicker } = DatePicker;

const AuditManagementPage = () => {
  const [reports, setReports] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reviewModalVisible, setReviewModalVisible] = useState(false);
  const [reviewNotes, setReviewNotes] = useState('');
  const [dateRange, setDateRange] = useState(null);
  
  // 載入審計報告
  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await fetchWithToken('/api/audit/reports');
      setReports(response.data);
    } catch (error) {
      message.error('載入審計報告失敗');
    } finally {
      setLoading(false);
    }
  };
  
  // 載入審計日誌
  const fetchLogs = async (params = {}) => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('from_date', params.fromDate);
      if (params.toDate) queryParams.append('to_date', params.toDate);
      if (params.action) queryParams.append('action', params.action);
      if (params.targetType) queryParams.append('target_type', params.targetType);
      
      const response = await fetchWithToken(`/api/audit/logs?${queryParams}`);
      setLogs(response.data);
    } catch (error) {
      message.error('載入審計日誌失敗');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchReports();
  }, []);
  
  // 審核報告
  const handleReviewSubmit = async () => {
    if (!reviewNotes) {
      message.error('請輸入審核意見');
      return;
    }
    
    try {
      await fetchWithToken(`/api/audit/reports/${selectedReport.id}/review`, {
        method: 'POST',
        body: JSON.stringify({ notes: reviewNotes })
      });
      
      message.success('審核完成');
      setReviewModalVisible(false);
      setReviewNotes('');
      fetchReports();
    } catch (error) {
      message.error('審核失敗');
    }
  };
  
  // 報告列表欄位
  const reportColumns = [
    {
      title: '期別',
      dataIndex: 'period',
      key: 'period',
      render: period => `${period.slice(0, 4)}年${period.slice(4)}月`,
    },
    {
      title: '總營收',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
      render: amount => `NT$ ${amount.toLocaleString()}`,
    },
    {
      title: '總手續費',
      dataIndex: 'total_commission',
      key: 'total_commission',
      render: amount => `NT$ ${amount.toLocaleString()}`,
    },
    {
      title: '總稅額',
      dataIndex: 'total_tax',
      key: 'total_tax',
      render: amount => `NT$ ${amount.toLocaleString()}`,
    },
    {
      title: '結算筆數',
      dataIndex: 'settlement_count',
      key: 'settlement_count',
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      render: status => (
        <Tag color={status === 'reviewed' ? 'green' : 'gold'}>
          {status === 'reviewed' ? '已審核' : '待審核'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <span>
          <Button
            type="link"
            icon={<FileSearchOutlined />}
            onClick={() => window.open(`/audit/reports/${record.id}`)}
          >
            查看詳情
          </Button>
          {record.status === 'pending' && (
            <Button
              type="link"
              icon={<AuditOutlined />}
              onClick={() => {
                setSelectedReport(record);
                setReviewModalVisible(true);
              }}
            >
              審核
            </Button>
          )}
        </span>
      ),
    },
  ];
  
  // 日誌列表欄位
  const logColumns = [
    {
      title: '時間',
      dataIndex: 'created_at',
      key: 'created_at',
      render: date => format(new Date(date), 'yyyy-MM-dd HH:mm:ss'),
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
    },
    {
      title: '目標類型',
      dataIndex: 'target_type',
      key: 'target_type',
    },
    {
      title: '目標ID',
      dataIndex: 'target_id',
      key: 'target_id',
    },
    {
      title: '原因',
      dataIndex: 'reason',
      key: 'reason',
    },
    {
      title: 'IP位址',
      dataIndex: 'ip_address',
      key: 'ip_address',
    },
  ];

  return (
    <div className="audit-management">
      <Tabs defaultActiveKey="reports">
        <TabPane tab="審計報告" key="reports">
          <Table
            columns={reportColumns}
            dataSource={reports}
            rowKey="id"
            loading={loading}
          />
        </TabPane>
        <TabPane tab="審計日誌" key="logs">
          <Card style={{ marginBottom: 16 }}>
            <Form layout="inline">
              <Form.Item label="時間範圍">
                <RangePicker
                  onChange={(dates) => {
                    if (dates) {
                      fetchLogs({
                        fromDate: dates[0].toISOString(),
                        toDate: dates[1].toISOString()
                      });
                    }
                  }}
                />
              </Form.Item>
            </Form>
          </Card>
          <Table
            columns={logColumns}
            dataSource={logs}
            rowKey="id"
            loading={loading}
          />
        </TabPane>
      </Tabs>
      
      <Modal
        title="審核報告"
        visible={reviewModalVisible}
        onOk={handleReviewSubmit}
        onCancel={() => {
          setReviewModalVisible(false);
          setReviewNotes('');
        }}
      >
        <Form>
          <Form.Item label="審核意見" required>
            <TextArea
              rows={4}
              value={reviewNotes}
              onChange={e => setReviewNotes(e.target.value)}
              placeholder="請輸入審核意見..."
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AuditManagementPage;