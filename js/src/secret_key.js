import React, { useEffect } from 'react';
import { useState } from 'react'
import { Alert, Button, Input, Table } from 'antd';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import Cookies from 'js-cookie';

export const SecretKeySettings = (props) => {
    const [keys, setKeys] = useState();
    const [createdKey, setCreatedKey] = useState();

    const loadSecretKeys = () => {
        fetch('/api/v1/secret_keys')
            .then(r => {
                if (r.status === 200) {
                    return r.json();
                } else if (r.status === 403) {
                    Cookies.remove('secret_key');
                    window.location.href = '/';
                }
            })
            .then(data => {
                let sks = data.data;
                for (let i = 0; i < sks.length; i ++) {
                    sks[i].key = i;
                }
                setKeys(sks);
            })
    }

    const onDelete = (id) => {
        fetch(`/api/v1/secret_keys/${id}`, {
            method: 'DELETE'
        }).then(r => {
            if (r.status === 200) {
                loadSecretKeys();
            } else {
                throw new Error("Status: " +r.status)
            }
        })
    }

    const onCreate = () => {
        fetch('/api/v1/secret_keys', {
            method: 'POST',
            headers: {"Content-Type": "application/json"}
        }).then(r => r.json())
        .then(data => {
            setCreatedKey(data.id);
        })
    }

    const onCloseCreatedResult = () => {
        setCreatedKey(null);
        loadSecretKeys();
    }

    useEffect(() => {
        loadSecretKeys();
    }, []);

    return (
        <div>
            <Button
                type="dashed"
                shape="circle"
                style={{ marginLeft: 15, marginBottom: 10 }}
                onClick={onCreate}
            >
                <PlusOutlined />
            </Button>
            {createdKey ? (
                <Alert
                    afterClose={onCloseCreatedResult}
                    message="Create new secret key"
                    description={<div>
                        <p>Please save this secret key somewhere safe and accessible. For security reasons, you won't be able to view it again through your account. If you lose this secret key, you'll need to generate a new one.</p>
                        <Input value={createdKey}/>
                    </div>}
                    type="warning" showIcon closable style={{marginBottom: 10}}/>
            ) : null}
            
            <Table
                size='small'
                columns={[
                    {
                        title: 'Key',
                        key: 'id',
                        dataIndex: 'id'
                    },
                    /*{
                        title: 'Name',
                        key: 'display_name',
                        dataIndex: 'display_name'
                    },*/
                    {
                        title: 'Tag',
                        key: 'tag',
                        dataIndex: 'tag'
                    },
                    {
                        title: '',
                        key: 'actions',
                        render: (_, r) => (
                            <DeleteOutlined onClick={() => onDelete(r.id)} />
                        )
                    }
                ]}
                locale={{ emptyText: ' ' }}
                dataSource={keys}
                pagination={false}
            />
            
        </div>
    )
}