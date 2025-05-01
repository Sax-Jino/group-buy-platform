import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Descriptions, Table, Typography, Row, Col, Tag, Divider, Statistic } from 'antd';
import { format } from 'date-fns';
import { fetchWithToken } from '../utils/api';

const { Title } = Typography;

const AuditReportDetailPage = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReport();
  }, [reportId]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const response = await fetchWithToken(`/api/audit/reports/${reportId}`);
      setReport(response.data);
    } catch (error) {
      console.error('載入報告失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>載入中...</div>;
  }

  if (!report) {
    return <div>找不到報告</div>;
  }

  const supplierColumns = [
    {
      title: '供應商ID',
      dataIndex: 'user_id',
      key: 'user_id',
    },
    {
      title: '期別',
      dataIndex: 'period',
      key: 'period',
    },
    {
      title: '金額',
      dataIndex: 'amount',
      key: 'amount',
      render: amount => `NT$ ${amount.toLocaleString()}`,
    },
  ];

  const momColumns = [
    {
      title: '團媽ID',
      dataIndex: 'user_id',
      key: 'user_id',
    },
    {
      title: '期別',
      dataIndex: 'period',
      key: 'period',
    },
    {
      title: '金額',
      dataIndex: 'amount',
      key: 'amount',
      render: amount => `NT$ ${amount.toLocaleString()}`,
    },
  ];

  return (
    <div className="audit-report-detail">
      <Card>
        <Title level={4}>審計報告詳情</Title>
        <Divider />
        
        <Descriptions title="基本資訊" column={2}>
          <Descriptions.Item label="報告期別">
            {report.period.slice(0, 4)}年{report.period.slice(4)}月
          </Descriptions.Item>
          <Descriptions.Item label="狀態">
            <Tag color={report.status === 'reviewed' ? 'green' : 'gold'}>
              {report.status === 'reviewed' ? '已審核' : '待審核'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="生成時間">
            {format(new Date(report.generated_at), 'yyyy-MM-dd HH:mm:ss')}
          </Descriptions.Item>
          {report.reviewed_at && (
            <Descriptions.Item label="審核時間">
              {format(new Date(report.reviewed_at), 'yyyy-MM-dd HH:mm:ss')}
            </Descriptions.Item>
          )}
        </Descriptions>

        <Divider />
        <Title level={5}>財務摘要</Title>
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="總營收"
                value={report.report_data.total_revenue}
                precision={2}
                prefix="NT$"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="總手續費"
                value={report.report_data.total_commission}
                precision={2}
                prefix="NT$"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="總稅金"
                value={report.report_data.total_tax}
                precision={2}
                prefix="NT$"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="結算筆數"
                value={report.report_data.settlement_count}
              />
            </Card>
          </Col>
        </Row>

        <Divider />
        <Title level={5}>供應商結算明細</Title>
        <Table
          columns={supplierColumns}
          dataSource={report.report_data.supplier_settlements}
          rowKey="user_id"
          pagination={false}
        />

        <Divider />
        <Title level={5}>團媽結算明細</Title>
        <Table
          columns={momColumns}
          dataSource={report.report_data.mom_settlements}
          rowKey="user_id"
          pagination={false}
        />

        {report.review_notes && (
          <>
            <Divider />
            <Card title="審核意見">
              <p>{report.review_notes}</p>
            </Card>
          </>
        )}
      </Card>
    </div>
  );
};

export default AuditReportDetailPage;