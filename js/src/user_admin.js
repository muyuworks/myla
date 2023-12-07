import { DeleteOutlined, PlusOutlined } from "@ant-design/icons"
import { Button, Form, Input, Space, Table, message } from "antd"
import Link from "antd/es/typography/Link"
import { useEffect, useState } from "react"
import { getUser } from "./user"

export const UserAdmin = () => {
    const [users, setUsers] = useState()
    const [msg, msgContext] = message.useMessage()
    const [formView, setFormView] = useState(false)
    const [createUserForm] = Form.useForm()

    let user = getUser()

    const loadUsers = () => {
        fetch('/api/v1/users').then(r => {
            if (r.status === 200) {
                return r.json();
            } else {
                throw new Error("Status: " + r.status)
            }
        }).then(data => {
            setUsers(data.data);
        }).catch(err => {
            msg.error(err.message);
        })
    }

    const onDelete = (username) => {
        fetch(`/api/v1/users/${username}`, {
            method: 'DELETE'
        }).then(r => {
            if (r.status === 200) {
                msg.success("OK");
                loadUsers();
            } else {
                throw new Error("Status: " + r.status)
            }
        }).catch(err => {
            msg.error(err.message);
        })
    }

    const onCreate = () => {
        let username = createUserForm.getFieldValue('username');
        let password = createUserForm.getFieldValue('password');

        fetch('/api/v1/users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: username,
                password: password
            })
        }).then(r => {
            if (r.status === 200) {
                onCancel();
                loadUsers();
            } else {
                throw new Error('Stauts: ' + r.status);
            }
        }).catch(err => {
            msg.error(err.message)
        })
    }

    const onCancel = () => {
        setFormView(false);
        createUserForm.resetFields();
    }

    useEffect(() => {
        loadUsers();
    }, [])

    return (
        <div>
            {msgContext}
            {!formView ? (
                <div>
                    <Button
                        type="dashed"
                        shape="circle"
                        style={{ marginLeft: 15, marginBottom: 10 }}
                        onClick={() => setFormView(true)}
                    >
                        <PlusOutlined />
                    </Button>
                    <Table
                        size='small'
                        columns={[
                            {
                                title: 'Username',
                                key: 'username',
                                dataIndex: 'username'
                            },
                            {
                                title: '',
                                key: 'actions',
                                render: (_, r) => (
                                    user.username !== r.username ? <DeleteOutlined onClick={() => onDelete(r.username)} /> : null
                                )
                            }
                        ]}
                        locale={{ emptyText: ' ' }}
                        dataSource={users}
                        pagination={false}
                    />
                </div>
            ) : (
                <div>
                    <Link onClick={onCancel} style={{ marginBottom: 20, display: 'block' }}>&lt; Back</Link>
                    <Form
                        form={createUserForm}
                        layout="vertical"
                        onFinish={onCreate}
                    >
                        <Form.Item label="Username" name='username'
                            rules={[
                                {
                                    required: true
                                }
                            ]}
                        >
                            <Input
                                type='text'
                            />
                        </Form.Item>

                        <Form.Item label="Password" name='password'
                            rules={[
                                {
                                    required: true
                                }
                            ]}
                        >
                            <Input.Password
                                type='text'
                            />
                        </Form.Item>

                        <Space style={{ marginBottom: 20 }}>
                            <Button type='default' onClick={() => { onCancel() }}>Cancel</Button>
                            <Button type='primary' onClick={onCreate}>Create</Button>
                        </Space>
                    </Form>
                </div>
            )}
        </div>
    )
}