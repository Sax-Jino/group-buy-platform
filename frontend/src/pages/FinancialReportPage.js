import React, { useState, useEffect } from 'react';
import { Card, Tabs, Row, Col, Statistic, Button, DatePicker, Table, message } from 'antd';
import { DownloadOutlined, LineChartOutlined } from '@ant-design/icons';
import { Line } from '@ant-design/charts';
import moment from 'moment';
import { fetchWithToken } from '../utils/api';

const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

const FinancialReportPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [revenueData, setRevenueData] = useState([]);
  const [profitData, setProfitData] = useState([]);
  const [momData, setMomData] = useState([]);
  const [productData, setProductData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState([
    moment().subtract(30, 'days'),
    moment()
  ]);
  
  useEffect(() => {
    fetchMetrics();
    fetchAnalytics();
  }, []);
  
  const fetchMetrics = async () => {
    try {
      const response = await fetchWithToken('/api/financial/analysis/metrics');
      setMetrics(response.data);
    } catch (error) {
      message.error('載入財務指標失敗');
    }
  };
  
  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      const [start, end] = dateRange;
      const params = new URLSearchParams({
        start_date: start.toISOString(),
        end_date: end.toISOString()
      });
      
      // 並行請求所有分析數據
      const [revenue, profit, mom, product] = await Promise.all([
        fetchWithToken(`/api/financial/analysis/revenue?${params}`),
        fetchWithToken(`/api/financial/analysis/profit?${params}`),
        fetchWithToken('/api/financial/analysis/mom-performance'),
        fetchWithToken('/api/financial/analysis/product-performance')
      ]);
      
      setRevenueData(revenue.data);
      setProfitData(profit.data);
      setMomData(mom.data);
      setProductData(product.data);
    } catch (error) {
      message.error('載入分析數據失敗');
    } finally {
      setLoading(false);
    }
  };
  
  const handleExport = async (type) => {
    try {
      const [start, end] = dateRange;
      let url = '';
      let period = moment().format('YYYYMM') + (moment().date() <= 15 ? 'a' : 'b');
      
      switch (type) {
        case 'financial':
          url = `/api/financial/export/financial-report?start_date=${start.toISOString()}&end_date=${end.toISOString()}`;
          break;
        case 'settlement':
          url = `/api/financial/export/settlement-report/${period}`;
          break;
        default:
          return;
      }
      
      const response = await fetchWithToken(url, { responseType: 'blob' });
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = type === 'financial' 
        ? `financial_report_${start.format('YYYYMMDD')}_${end.format('YYYYMMDD')}.xlsx`
        : `settlement_report_${period}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      message.error('導出報表失敗');
    }
  };
  
  // 營收趨勢圖配置
  const revenueConfig = {
    data: revenueData,
    height: 400,
    xField: 'date',
    yField: 'revenue',
    seriesField: 'type',
    point: {
      size: 5,
      shape: 'diamond'
    },
    label: {
      style: {
        fill: '#aaa'
      }
    }
  };
  
  // 利潤趨勢圖配置
  const profitConfig = {
    data: profitData.map(d => ([
      { type: '平台利潤', value: d.platform_profit, date: d.date },
      { type: '供應商費用', value: d.supplier_fees, date: d.date },
      { type: '平台費用', value: d.platform_fees, date: d.date }
    ])).flat(),
    height: 400,
    xField: 'date',
    yField: 'value',
    seriesField: 'type',
    point: {
      size: 5,
      shape: 'diamond'
    }
  };
  
  // 團媽績效表格列設定
  const momColumns = [
    {
      title: '團媽ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '用戶名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '等級',
      dataIndex: 'group_mom_level',
      key: 'group_mom_level',
      render: level => `Level ${level}`,
    },
    {
      title: '訂單數',
      dataIndex: 'order_count',
      key: 'order_count',
      sorter: (a, b) => a.order_count - b.order_count,
    },
    {
      title: '總銷售額',
      dataIndex: 'total_sales',
      key: 'total_sales',
      render: amount => `NT$ ${amount.toLocaleString()}`,
      sorter: (a, b) => a.total_sales - b.total_sales,
    },
    {
      title: '總傭金',
      dataIndex: 'total_commission',
      key: 'total_commission',
      render: amount => `NT$ ${amount.toLocaleString()}`,
      sorter: (a, b) => a.total_commission - b.total_commission,
    },
  ];
  
  // 商品績效表格列設定
  const productColumns = [
    {
      title: '商品ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '名稱',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '訂單數',
      dataIndex: 'order_count',
      key: 'order_count',
      sorter: (a, b) => a.order_count - b.order_count,
    },
    {
      title: '總數量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      sorter: (a, b) => a.total_quantity - b.total_quantity,
    },
    {
      title: '總營收',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
      render: amount => `NT$ ${amount.toLocaleString()}`,
      sorter: (a, b) => a.total_revenue - b.total_revenue,
    },
    {
      title: '平均訂購數量',
      dataIndex: 'avg_quantity_per_order',
      key: 'avg_quantity_per_order',
      render: value => value.toFixed(2),
      sorter: (a, b) => a.avg_quantity_per_order - b.avg_quantity_per_order,
    },
  ];

  return (
    <div className="financial-report">
      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <RangePicker
              value={dateRange}
              onChange={setDateRange}
              onBlur={fetchAnalytics}
              style={{ marginRight: 16 }}
            />
            <Button 
              type="primary" 
              icon={<DownloadOutlined />}
              onClick={() => handleExport('financial')}
            >
              導出財務報表
            </Button>
            <Button 
              style={{ marginLeft: 8 }}
              icon={<DownloadOutlined />}
              onClick={() => handleExport('settlement')}
            >
              導出結算報表
            </Button>
          </Col>
        </Row>

        {metrics && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Card>
                <Statistic
                  title="總訂單數"
                  value={metrics.total_orders}
                  prefix={<LineChartOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="總營收"
                  value={metrics.total_revenue}
                  precision={2}
                  prefix="NT$"
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="平均訂單金額"
                  value={metrics.avg_order_value}
                  precision={2}
                  prefix="NT$"
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="總利潤"
                  value={metrics.total_profit}
                  precision={2}
                  prefix="NT$"
                />
              </Card>
            </Col>
          </Row>
        )}

        <Tabs defaultActiveKey="revenue">
          <TabPane tab="營收分析" key="revenue">
            <Card title="營收趨勢" loading={loading}>
              <Line {...revenueConfig} />
            </Card>
          </TabPane>
          
          <TabPane tab="利潤分析" key="profit">
            <Card title="利潤趨勢" loading={loading}>
              <Line {...profitConfig} />
            </Card>
          </TabPane>
          
          <TabPane tab="團媽績效" key="mom">
            <Card title="團媽績效排名" loading={loading}>
              <Table
                columns={momColumns}
                dataSource={momData}
                rowKey="id"
                pagination={{ pageSize: 10 }}
              />
            </Card>
          </TabPane>
          
          <TabPane tab="商品績效" key="product">
            <Card title="商品績效排名" loading={loading}>
              <Table
                columns={productColumns}
                dataSource={productData}
                rowKey="id"
                pagination={{ pageSize: 10 }}
              />
            </Card>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default FinancialReportPage;