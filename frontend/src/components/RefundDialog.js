import React, { useState } from 'react';
import { Upload, Form, Input, Radio, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import '../styles/RefundDialog.css';

const RefundDialog = ({ orderId, orderAmount, onClose, onSubmit }) => {
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);
    const [fileList, setFileList] = useState([]);

    const handleSubmit = async (values) => {
        setSubmitting(true);
        try {
            const formData = new FormData();
            formData.append('order_id', orderId);
            formData.append('reason', values.reason);
            formData.append('refund_type', values.refund_type);
            formData.append('amount', values.amount || orderAmount);
            fileList.forEach(file => {
                formData.append('images[]', file.originFileObj);
            });

            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5000/api/refunds', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to submit refund request');
            }

            message.success('退換貨申請已提交');
            onSubmit();
        } catch (error) {
            console.error('Error submitting refund:', error);
            message.error('提交退換貨申請失敗');
        } finally {
            setSubmitting(false);
        }
    };

    const handleFileChange = ({ fileList: newFileList }) => {
        setFileList(newFileList.slice(0, 3));  // 最多3張圖片
    };

    return (
        <div className="refund-dialog">
            <div className="refund-content">
                <button className="close-button" onClick={onClose}>&times;</button>
                <h3>退換貨申請</h3>

                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                    initialValues={{
                        refund_type: 'refund',
                        amount: orderAmount
                    }}
                >
                    <Form.Item
                        name="refund_type"
                        label="申請類型"
                        rules={[{ required: true, message: '請選擇申請類型' }]}
                    >
                        <Radio.Group>
                            <Radio value="refund">退貨退款</Radio>
                            <Radio value="exchange">換貨</Radio>
                        </Radio.Group>
                    </Form.Item>

                    <Form.Item
                        name="reason"
                        label="退換貨原因"
                        rules={[{ required: true, message: '請填寫退換貨原因' }]}
                    >
                        <Input.TextArea rows={4} placeholder="請詳細說明退換貨原因..." />
                    </Form.Item>

                    <Form.Item
                        name="amount"
                        label="退款金額"
                        dependencies={['refund_type']}
                    >
                        <Input
                            type="number"
                            disabled={form.getFieldValue('refund_type') === 'exchange'}
                            max={orderAmount}
                            min={0}
                        />
                    </Form.Item>

                    <Form.Item
                        label="相關照片（最多3張）"
                        extra="請上傳商品照片或瑕疵照片"
                    >
                        <Upload
                            listType="picture"
                            fileList={fileList}
                            onChange={handleFileChange}
                            beforeUpload={() => false}
                            maxCount={3}
                        >
                            {fileList.length < 3 && (
                                <Button icon={<UploadOutlined />}>上傳照片</Button>
                            )}
                        </Upload>
                    </Form.Item>

                    <div className="action-buttons">
                        <Button onClick={onClose}>取消</Button>
                        <Button 
                            type="primary" 
                            htmlType="submit"
                            loading={submitting}
                        >
                            提交申請
                        </Button>
                    </div>
                </Form>
            </div>
        </div>
    );
};

export default RefundDialog;