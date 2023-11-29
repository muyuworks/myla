import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { useState } from 'react'
import { Layout, List, Avatar, Space, Typography, Button, Form, Input, Skeleton, Tabs, Alert } from 'antd'
import { MenuUnfoldOutlined, MenuFoldOutlined, PlusOutlined, CloseCircleOutlined, SettingOutlined, DeleteOutlined } from '@ant-design/icons'
import {

} from '@ant-design/icons';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm'
import { Chat } from './chat'
import Link from 'antd/es/typography/Link';
import TextArea from 'antd/es/input/TextArea';

const { Sider } = Layout
const { Text } = Typography

let welcome_message = `
# Welcome!
`

export const Aify = (props) => {
    const [leftCollapsed, setLeftCollapsed] = useState(true);
    const [rightCollapsed, setRightCollapsed] = useState(true);
    const [assistants, setAssistants] = useState();
    const [assistantMap, setAssistantMap] = useState({});
    const [currentAssistantId, setCurrentAsistantId] = useState(null);
    const [currentThreadId, setCurrentThreadId] = useState(null);
    const [threads, setThreads] = useState();

    const [welcomMessage, setWelcomeMessage] = useState();
    const [user, setUser] = useState();

    const createAssistant = async (assistant) => {
        let name = assistant.name;
        let desc = assistant.desc;
        let instructions = assistant.instructions;
        let model = assistant.model;
        let icon = assistant.icon;
        let tools = assistant.tools;
        let file_ids = assistant.file_ids;
        var metadata = assistant.metadata;
        metadata = metadata ? JSON.parse(metadata) : {}
        metadata.icon = icon

        var body = {
            "name": name,
            "description": desc,
            "instructions": instructions,
            "model": model,
            "tools": tools ? JSON.parse(tools) : [],
            "file_ids": file_ids ? JSON.parse(file_ids) : [],
            "metadata": metadata
        };
        if (model == null) {
            body.model = '';
        }

        const r = await fetch(assistant.id ? `/api/v1/assistants/${assistant.id}` : "/api/v1/assistants", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });
        if (r.status !== 200) {
            throw new Error("Bad request status: " + r.status);
        }
        loadAsistants();
    }

    const deleteAssistant = (assistant_id) => {
        fetch(`/api/v1/assistants/${assistant_id}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json"
            }
        })
            .then(r => r.json())
            .then(thread => {
                loadAsistants();
            })
    }

    const loadAsistants = () => {
        fetch('/api/v1/assistants')
            .then(r => r.json())
            .then(asis => {
                let m = {};

                asis.data.forEach(a => {
                    if (!a.name) {
                        a.name = a.id
                    }
                    if (!a.metadata) {
                        a.metadata = {}
                    }
                    m[a.id] = a;
                });
                setAssistants(asis.data);
                setAssistantMap(m);
            })
    }

    const loadThreads = () => {
        fetch('/api/v1/threads')
            .then(r => r.json())
            .then(threads => {
                threads.data.forEach(t => {
                    if (!t.metadata) {
                        t.metadata = {}
                    }
                });
                setThreads(threads.data)
            });
    }

    const loadWelcomeMessage = () => {
        fetch('/static/welcome.md')
            .then(r => {
                if (r.status === 200) {
                    return r.text();
                } else {
                    return welcome_message
                }
            })
            .then(data => setWelcomeMessage(data))
    }
    /*
    const loadUser = () => {
        fetch('/api/user')
            .then(r => r.json())
            .then(user => setUser(user))
    }*/

    useEffect(() => {
        loadAsistants();
        loadThreads();
        loadWelcomeMessage();
        //loadUser();
    }, [])

    const createThread = (assistant_id, assistant_name) => {
        fetch('/api/v1/threads', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                'metadata': {
                    "assistant_id": assistant_id,
                    "assistant_name": assistant_name
                }
            })
        })
            .then(r => r.json())
            .then(thread => {
                loadThreads();
                switchThread(assistant_id, thread.id);
            })

    }

    const deleteThread = (thread_id) => {
        fetch(`/api/v1/threads/${thread_id}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json"
            }
        })
            .then(r => r.json())
            .then(thread => {
                loadThreads();
                if (currentThreadId === thread_id) {
                    setCurrentThreadId(null);
                }
            })
    }

    const switchThread = (assistant_id, thread_id) => {
        setCurrentAsistantId(assistant_id);
        setCurrentThreadId(thread_id);
    }

    const onMessageReceived = (thread_id, content) => {
        let e = document.getElementById(`last-msg-${thread_id}`);
        if (e) {
            e.innerHTML = content;
        }
    }

    return (
        <Layout
            hasSider
            style={{
                minHeight: '100vh',
            }}
        >
            <Sider
                collapsible
                collapsed={leftCollapsed}
                onCollapse={(value) => setLeftCollapsed(value)}
                //breakpoint="lg"
                theme="light"
                style={{
                    height: '100vh',
                    backgroundColor: '#FBFCFC'
                }}
                className='overflow-auto scrollbar-none'
                width={280}
                collapsedWidth={65}
                trigger={null}
            >
                <List
                    size='small'
                    itemLayout="horizontal"
                    locale={{ emptyText: ' ' }}
                    dataSource={threads}
                    renderItem={(thread => (
                        assistantMap[thread.metadata.assistant_id] != null ? (
                            <List.Item style={currentThreadId === thread.id ? { backgroundColor: 'white' } : {}}>
                                <Space>
                                    <Link
                                        onClick={() => switchThread(thread.metadata.assistant_id, thread.id)}
                                    >
                                        <Space>
                                            <Avatar style={{ backgroundColor: '#eee', color: '#999' }}>{(assistantMap[thread.metadata.assistant_id].metadata.icon) ?? '🤖'}</Avatar>
                                            {!leftCollapsed ? (
                                                <Space direction='horizontal' size={0}>
                                                    <Text type="secondary"
                                                        ellipsis={{
                                                            rows: 1,
                                                        }}
                                                        style={{ width: '190px' }}
                                                    >
                                                        <div id={`last-msg-${thread.id}`}>{assistantMap[thread.metadata.assistant_id].name}</div>
                                                    </Text>
                                                </Space>
                                            ) : null}

                                        </Space>
                                    </Link>
                                    {!leftCollapsed ? (
                                        <Link onClick={() => deleteThread(thread.id)}><CloseCircleOutlined style={{ color: '#ccc', marginTop: 15 }} /></Link>
                                    ) : null}
                                </Space>
                            </List.Item>
                        ) : null
                    ))}
                />
            </Sider>
            <Layout
                id="content"
                style={{
                    height: '100vh',
                    overflow: 'hidden',
                }}
                className='bg-white'
            >
                <div className='d-flex p-2'>
                    <Button
                        type="text"
                        onClick={() => setLeftCollapsed(!leftCollapsed)}
                        style={{
                            fontSize: '14px',
                            padding: 5
                        }}
                        className='me-auto'
                    >
                        {leftCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                    </Button>
                    <Button
                        type="text"
                        onClick={() => setRightCollapsed(!rightCollapsed)}
                        style={{
                            fontSize: '14px',
                            padding: 5
                        }}
                        className='ms-auto'
                    >
                        {rightCollapsed ? <MenuFoldOutlined /> : <MenuUnfoldOutlined />}
                    </Button>
                </div>
                {(currentAssistantId != null && currentThreadId != null) ? (
                    <Chat
                        key={currentThreadId}
                        name={currentAssistantId}
                        thread_id={currentThreadId}
                        width="100%"
                        onMessageReceived={onMessageReceived}
                        icon={(assistantMap[currentAssistantId] && assistantMap[currentAssistantId].metadata.icon) ?? '🤖'}
                        user={user}
                    />
                ) : (
                    <div className='p-5'>
                        <Markdown children={props.message} remarkPlugins={[remarkGfm]} className='p-0 m-0'>
                            {welcomMessage}
                        </Markdown>
                    </div>
                )}

            </Layout>

            <Sider
                collapsible
                collapsed={rightCollapsed}
                onCollapse={(value) => setRightCollapsed(value)}
                breakpoint="lg"
                theme="light"
                style={{
                    height: '100vh',
                    backgroundColor: '#FBFCFC',
                    padding: 10
                }}
                className='overflow-auto'
                width={500}
                collapsedWidth={0}
                trigger={null}
                reverseArrow
            >
                <Tabs
                    defaultActiveKey="1"
                    items={[
                        {
                            key: '1',
                            label: ' Assistants',
                            children: <Assistants assistants={assistants} onCreate={createAssistant} onDelete={deleteAssistant} createThread={createThread} />
                        },
                        {
                            key: '2',
                            label: 'Files',
                            children: <Files />
                        }
                    ]}
                />
            </Sider>
        </Layout>
    );
}

const Assistants = (props) => {
    const [formView, setFormView] = useState(false);
    const [assistantToModify, setAssistantToModify] = useState(null);
    const [createAssistantForm] = Form.useForm();
    const [error, setError] = useState();

    const onCancel = () => {
        setAssistantToModify(null);
        setFormView(false);
        createAssistantForm.resetFields();
        setError(null);
    }

    const onCreate = () => {
        let assistant = {
            id: assistantToModify != null ? assistantToModify.id : null,
            name: createAssistantForm.getFieldValue("name"),
            desc: createAssistantForm.getFieldValue("desc"),
            instructions: createAssistantForm.getFieldValue("instructions"),
            model: createAssistantForm.getFieldValue("model"),
            icon: createAssistantForm.getFieldValue("icon"),
            tools: createAssistantForm.getFieldValue("tools"),
            file_ids: createAssistantForm.getFieldValue("file_ids"),
            metadata: createAssistantForm.getFieldValue("metadata")
        }

        props.onCreate(assistant).then(() => onCancel()).catch(err => setError(err.message));

    }

    const onModify = (assistant) => {
        createAssistantForm.setFieldValue('name', assistant.name);
        createAssistantForm.setFieldValue('desc', assistant.desc);
        createAssistantForm.setFieldValue('instructions', assistant.instructions);
        createAssistantForm.setFieldValue('model', assistant.model);
        createAssistantForm.setFieldValue('icon', assistant.metadata.icon);
        createAssistantForm.setFieldValue('tools', JSON.stringify(assistant.tools, null, 4));
        createAssistantForm.setFieldValue('file_ids', JSON.stringify(assistant.file_ids, null, 4));
        createAssistantForm.setFieldValue('metadata', JSON.stringify(assistant.metadata, null, 4));
        setAssistantToModify(assistant);
        setFormView(true);
    }

    useEffect(() => {
    }, [])

    return (
        <div>
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

                    <List
                        //split={false}
                        size='small'
                        itemLayout="horizontal"
                        locale={{ emptyText: ' ' }}
                        dataSource={props.assistants}
                        renderItem={(assistant) => (
                            <List.Item
                                actions={[
                                    <SettingOutlined onClick={() => { onModify(assistant) }} />,
                                    <DeleteOutlined onClick={() => props.onDelete(assistant.id)} />,
                                ]}
                            >
                                <Skeleton avatar title={false} loading={assistant.loading} active>
                                    <List.Item.Meta
                                        avatar={<Avatar style={{ backgroundColor: '#eee', color: '#999' }}>{assistant.metadata.icon ?? '🤖'}</Avatar>}
                                        title={<Link onClick={() => props.createThread(assistant.id, assistant.name)} style={{ fontSize: '0.85rem' }}>{assistant.name}</Link>}
                                        description={assistant.description}
                                    />
                                </Skeleton>
                            </List.Item>
                        )}
                    />
                </div>
            ) : (
                <Form form={createAssistantForm} layout="vertical">
                    <Form.Item label="Name" name='name'>
                        <Input
                            type='text'
                            placeholder="Name"
                        />
                    </Form.Item>
                    <Form.Item label='Description' name='desc' >
                        <Input
                            type='text'
                            //style={{width: 200}}
                            placeholder="Description"
                        />
                    </Form.Item>
                    <Form.Item label='Instructions' name='instructions'>
                        <TextArea
                            autoSize
                            //style={{width: 200}}
                            placeholder="Instructions"
                        />
                    </Form.Item>
                    <Form.Item label="Model" name='model'>
                        <Input
                            type='text'
                            placeholder="Model name"
                        />
                    </Form.Item>
                    <Form.Item label='Tools' name='tools'>
                        <TextArea
                            autoSize
                            //style={{width: 200}}
                            placeholder='tools settings, like: [{"type": "$iur"}, {"type": "retrieval"}]'
                        />
                    </Form.Item>
                    <Form.Item label='Files' name='file_ids'>
                        <TextArea
                            autoSize
                            placeholder='file_ids, like: ["file_1", "file_2"]'
                        />
                    </Form.Item>
                    <Form.Item label='Metadata' name='metadata'>
                        <TextArea
                            autoSize
                            //style={{width: 200}}
                            placeholder='metadata, like: {"retrieval_collection": "default"}'
                        />
                    </Form.Item>
                    <Form.Item label='Avatar' name='icon' initialValue={'🤖'}>
                        <Input
                            type='text'
                            style={{ width: 50, height: 50, fontSize: 24 }}
                        />
                    </Form.Item>

                    {error ? (<Alert message={error} type="error" showIcon style={{ marginBottom: 10 }} />) : null}

                    <Space style={{marginBottom: 20}}>
                        <Button type='default' onClick={() => { onCancel() }}>Cancel</Button>
                        <Button type='primary' onClick={onCreate}>{assistantToModify ? 'Modify' : 'Create'}</Button>
                    </Space>
                </Form>
            )}
        </div>
    );
}

const Files = (props) => {
    return (
        <div>Files</div>
    );
}

export const create = (elementId, height) => {
    const root = ReactDOM.createRoot(document.getElementById(elementId));
    root.render(
        <React.StrictMode>
            <Aify />
        </React.StrictMode>
    );
}