import { DeleteOutlined, PlusOutlined } from "@ant-design/icons"
import { Button, Form, Input, Select, Space, Table, message } from "antd"
import Link from "antd/es/typography/Link"
import { useEffect, useState } from "react"

export const Members = () => {
    const [members, setMembers] = useState()
    const [msg, msgContext] = message.useMessage()
    const [formView, setFormView] = useState(false)
    const [inviteMemberForm] = Form.useForm()

    const invite = () => {
        let username = inviteMemberForm.getFieldValue('username');
    }

    const loadMembers = () => {
        fetch(`/api/v1/orgnizations/${localStorage.getItem('org_id')}/members`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'OpenAI-Organization': `${localStorage.getItem('org_id')}`
            }
        }).then(r => r.json()).then(members => {
            setMembers(members.data);
        })
    }

    const onCancel = () => {
        setFormView(false);
        inviteMemberForm.resetFields();
    }


    const onInvite = () => {
        let username = inviteMemberForm.getFieldValue('username');
        let role = inviteMemberForm.getFieldValue('role');

        fetch(`/api/v1/orgnizations/${localStorage.getItem('org_id')}/members`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'OpenAI-Organization': `${localStorage.getItem('org_id')}`
            },
            body: JSON.stringify({
                username: username,
                role: role || "reader"
            })
        }).then(r => {
            if (r.status === 200) {
                onCancel();
                loadMembers();
            } else {
                throw new Error('Stauts: ' + r.status);
            }
        }).catch(err => {
            msg.error(err.message)
        })
    }

    useEffect(() => {
        loadMembers();
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
                                dataIndex: 'username',
                                render: (text, r) => r.user.username
                            },
                            {
                                title: 'Display Name',
                                key: 'display_name',
                                dataIndex: 'display_name',
                                render: (text, r) => r.user.display_name
                            },
                            {
                                title: 'Role',
                                key: 'role',
                                dataIndex: 'role',
                                render: (text, r) => r.role
                            },
                            {
                                title: '',
                                key: 'actions',
                                render: (_, r) => (
                                    <DeleteOutlined />
                                )
                            }
                        ]}
                        locale={{ emptyText: ' ' }}
                        dataSource={members}
                        pagination={false}
                    />
                </div>
            ) : (
                <div>
                    <Link onClick={onCancel} style={{ marginBottom: 20, display: 'block' }}>&lt; Back</Link>
                    <Form
                        form={inviteMemberForm}
                        layout="vertical"
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
                                style={{width: 200}}
                            />
                        </Form.Item>

                        <Form.Item label="Role" name="role"
                            rules={[
                                {
                                    required: true
                                }
                            ]}
                        >
                            <Select
                                defaultValue="reader"
                                options={[
                                    {value: 'reader', label: 'Reader'},
                                    {value: 'owner', label: 'Owner'}
                                ]}
                                style={{width: 150}}
                            />
                        </Form.Item>

                        <Space style={{ marginBottom: 20 }}>
                            <Button type='default' onClick={() => { onCancel() }} >Cancel</Button>
                            <Button type='primary' onClick={onInvite} >Invite</Button>
                        </Space>
                    </Form>
                </div>
            )}
        </div>
    )
}