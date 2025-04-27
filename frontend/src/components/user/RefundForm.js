import React, { useState } from 'react';
import { Form, Input, Select, Upload, Button, InputNumber, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import '../../styles/RefundForm.css';

const { Option } = Select;
const { TextArea } = Input;

const RefundForm = ({ order, onSuccess, onCancel }) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [fileList, setFileList] = useState([]);

    const handleSubmit = async (values) => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('order_id', order.id);
            formData.append('refund_type', values.refund_type);
            formData.append('reason', values.reason);
            formData.append('amount', values.amount || 0);

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
                throw new Error('申請提交失敗');
            }

            message.success('退換貨申請已提交');
            onSuccess();
        } catch (error) {
            console.error('Failed to submit refund:', error);
            message.error('退換貨申請提交失敗');
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = ({ fileList }) => {
        setFileList(fileList.slice(-5)); // 最多允許5張圖片
    };

    return (
        <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            className="refund-form"
            initialValues={{
                refund_type: 'refund',
                amount: order.total_amount
            }}
        >
            <Form.Item
                label="申請類型"
                name="refund_type"
                rules={[{ required: true, message: '請選擇申請類型' }]}
            >
                <Select>
                    <Option value="refund">退貨退款</Option>
                    <Option value="exchange">換貨</Option>
                </Select>
            </Form.Item>

            <Form.Item
                noStyle
                shouldUpdate={(prevValues, currentValues) => 
                    prevValues.refund_type !== currentValues.refund_type
                }
            >
                {({ getFieldValue }) => 
                    getFieldValue('refund_type') === 'refund' && (
                        <Form.Item
                            label="退款金額"
                            name="amount"
                            rules={[
                                { required: true, message: '請輸入退款金額' },
                                {
                                    type: 'number',
                                    max: order.total_amount,
                                    message: `退款金額不能超過訂單金額 $${order.total_amount}`
                                }
                            ]}
                        >
                            <InputNumber
                                style={{ width: '100%' }}
                                formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                                parser={value => value.replace(/\$\s?|(,*)/g, '')}
                                max={order.total_amount}
                            />
                        </Form.Item>
                    )
                }
            </Form.Item>

            <Form.Item
                label="申請原因"
                name="reason"
                rules={[{ required: true, message: '請輸入申請原因' }]}
            >
                <TextArea rows={4} maxLength={500} showCount />
            </Form.Item>

            <Form.Item
                label="相關圖片"
                name="images"
                extra="最多可上傳5張圖片，每張不超過5MB"
            >
                <Upload
                    listType="picture"
                    fileList={fileList}
                    onChange={handleFileChange}
                    beforeUpload={() => false}
                    accept="image/*"
                    maxCount={5}
                >
                    {fileList.length < 5 && (
                        <Button icon={<UploadOutlined />}>上傳圖片</Button>
                    )}
                </Upload>
            </Form.Item>

            <Form.Item className="form-actions">
                <Button onClick={onCancel} style={{ marginRight: 8 }}>
                    取消
                </Button>
                <Button type="primary" htmlType="submit" loading={loading}>
                    提交申請
                </Button>
            </Form.Item>
        </Form>
    );
};

export default RefundForm;