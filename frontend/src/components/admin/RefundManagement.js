import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Space, Tag, Image, message } from 'antd';
import moment from 'moment';

const RefundManagement = () => {
    const [refunds, setRefunds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedRefund, setSelectedRefund] = useState(null);
    const [modalVisible, setModalVisible] = useState(false);

    const fetchRefunds = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5000/api/admin/refunds', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            setRefunds(data);
        } catch (error) {
            console.error('Failed to fetch refunds:', error);
            message.error('無法載入退換貨申請列表');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRefunds();
    }, []);

    const handleStatusChange = async (refundId, status) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://localhost:5000/api/admin/refunds/${refundId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status })
            });

            if (!response.ok) {
                throw new Error('更新狀態失敗');
            }

            message.success('退換貨申請狀態已更新');
            fetchRefunds();
            setModalVisible(false);
        } catch (error) {
            console.error('Failed to update refund status:', error);
            message.error('更新狀態失敗');
        }
    };

    const columns = [
        {
            title: '申請編號',
            dataIndex: 'id',
            key: 'id',
        },
        {
            title: '訂單編號',
            dataIndex: 'order_id',
            key: 'order_id',
        },
        {
            title: '申請類型',
            dataIndex: 'refund_type',
            key: 'refund_type',
            render: type => (
                <Tag color={type === 'refund' ? 'blue' : 'green'}>
                    {type === 'refund' ? '退貨退款' : '換貨'}
                </Tag>
            )
        },
        {
            title: '申請時間',
            dataIndex: 'created_at',
            key: 'created_at',
            render: date => moment(date).format('YYYY-MM-DD HH:mm:ss')
        },
        {
            title: '狀態',
            dataIndex: 'status',
            key: 'status',
            render: status => {
                const statusMap = {
                    'pending': { color: 'gold', text: '待處理' },
                    'approved': { color: 'green', text: '已批准' },
                    'rejected': { color: 'red', text: '已拒絕' },
                    'processing': { color: 'blue', text: '處理中' },
                    'completed': { color: 'green', text: '已完成' }
                };
                const { color, text } = statusMap[status] || { color: 'default', text: status };
                return <Tag color={color}>{text}</Tag>;
            }
        },
        {
            title: '操作',
            key: 'action',
            render: (_, record) => (
                <Space size="middle">
                    <Button 
                        type="link" 
                        onClick={() => {
                            setSelectedRefund(record);
                            setModalVisible(true);
                        }}
                    >
                        查看詳情
                    </Button>
                </Space>
            ),
        },
    ];

    return (
        <div>
            <Table 
                loading={loading}
                columns={columns} 
                dataSource={refunds}
                rowKey="id"
            />
            
            <Modal
                title="退換貨申請詳情"
                visible={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={[
                    <Button key="reject" type="danger" onClick={() => handleStatusChange(selectedRefund?.id, 'rejected')}>
                        拒絕
                    </Button>,
                    <Button key="approve" type="primary" onClick={() => handleStatusChange(selectedRefund?.id, 'approved')}>
                        批准
                    </Button>,
                ]}
                width={800}
            >
                {selectedRefund && (
                    <div>
                        <p><strong>申請原因：</strong> {selectedRefund.reason}</p>
                        {selectedRefund.refund_type === 'refund' && (
                            <p><strong>退款金額：</strong> ${selectedRefund.amount}</p>
                        )}
                        {selectedRefund.images && selectedRefund.images.length > 0 && (
                            <div>
                                <p><strong>相關圖片：</strong></p>
                                <Image.PreviewGroup>
                                    {selectedRefund.images.map((image, index) => (
                                        <Image
                                            key={index}
                                            width={200}
                                            src={image}
                                            style={{ marginRight: 8, marginBottom: 8 }}
                                        />
                                    ))}
                                </Image.PreviewGroup>
                            </div>
                        )}
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default RefundManagement;