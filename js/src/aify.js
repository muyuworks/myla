import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { useState } from 'react'
import { Layout, List, Avatar, Space, Typography, Button, Card, Modal, Form, Input } from 'antd'
import { MenuUnfoldOutlined, MenuFoldOutlined, MessageFilled, RobotOutlined,CloseCircleOutlined,EditOutlined } from '@ant-design/icons'
import {

} from '@ant-design/icons';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm'
import { Chat } from './chat'
import Link from 'antd/es/typography/Link';
import TextArea from 'antd/es/input/TextArea';

const { Sider } = Layout
const { Text } = Typography
const { Meta } = Card

let welcome_message = `
# Welcome!
`

export const Aify = (props) => {
    const [leftCollapsed, setLeftCollapsed] = useState(false);
    const [rightCollapsed, setRightCollapsed] = useState(false);
    const [assistants, setAssistants] = useState();
    const [assistantMap, setAssistantMap] = useState({});
    const [currentAssistantId, setCurrentAsistantId] = useState(null);
    const [currentThreadId, setCurrentThreadId] = useState(null);
    const [threads, setThreads] = useState();
    
    const [welcomMessage, setWelcomeMessage] = useState();
    const [user, setUser] = useState();

    const [openCreateAssistantModal, setOpenCreateAssistantModal] = useState(false);
    const [assistantToModify, setAssistantToModify] = useState(false);
    const [createAssistantForm] = Form.useForm();

    const createAssistant = (assistant_id) => {
        let name = createAssistantForm.getFieldValue("name");
        let desc = createAssistantForm.getFieldValue("desc");
        let instructions = createAssistantForm.getFieldValue("instructions");
        let model = createAssistantForm.getFieldValue("model");
        let icon = createAssistantForm.getFieldValue("icon");
        let tools = createAssistantForm.getFieldValue("tools");
        let file_ids = createAssistantForm.getFieldValue("file_ids");
        var metadata = createAssistantForm.getFieldValue("metadata");
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

        fetch(assistant_id ? `/api/v1/assistants/${assistant_id}` : "/api/v1/assistants", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }).then(r => {
            loadAsistants();
            setOpenCreateAssistantModal(false);
            createAssistantForm.resetFields();
        });
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
    
    const loadUser = () => {
        fetch('/api/user')
            .then(r => r.json())
            .then(user => setUser(user))
    }

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
                breakpoint="lg"
                theme="light"
                style={{
                    overflow: 'auto',
                    height: '100vh',
                    backgroundColor: 'whitesmoke'
                }}
                width={250}
                collapsedWidth={65}
                trigger={null}
            >
                <List
                    size='small'
                    itemLayout="horizontal"
                    dataSource={threads}
                    renderItem={(thread => (
                        assistantMap[thread.metadata.assistant_id] != null? (
                        <List.Item style={currentThreadId === thread.id ? {backgroundColor: 'white'} : {}}>
                            <Space>
                                <Link
                                    onClick={() => switchThread(thread.metadata.assistant_id, thread.id)}
                                >
                                    <Space>
                                        <Avatar style={{ backgroundColor: '#fff' }}>{(assistantMap[thread.metadata.assistant_id].metadata.icon) ?? '🤖'}</Avatar>
                                        {!leftCollapsed ? (
                                            <Space direction='horizontal' size={0}>
                                                <Text type="secondary"
                                                    ellipsis={{
                                                        rows: 1,
                                                    }}
                                                    style={{ width: '160px' }}
                                                >
                                                    <div id={`last-msg-${thread.id}`}>{assistantMap[thread.metadata.assistant_id].name}</div>
                                                </Text>
                                            </Space>
                                        ) : null}

                                    </Space>
                                </Link>
                                {!leftCollapsed ? (
                                <Link onClick={() => deleteThread(thread.id)}><CloseCircleOutlined style={{color: '#ccc', marginTop: 15}}/></Link>
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
                    overflow: 'scroll',
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
                    overflow: 'auto',
                    height: '100vh',
                    backgroundColor: 'whitesmoke'
                }}
                width={250}
                collapsedWidth={0}
                trigger={null}
                reverseArrow
            >
                <div style={{marginLeft: 18, marginRight: 18, marginTop: 20}}>
                    <Button type="primary" block onClick={() => {setOpenCreateAssistantModal(true);setAssistantToModify(null)}}>
                        <RobotOutlined /> Build Assistant
                    </Button>
                </div>
                <List
                    split={false}
                    size='small'
                    itemLayout="horizontal"
                    dataSource={assistants}
                    renderItem={(assistant) => (
                        <List.Item>
                            <Card
                                style={{
                                    width: 268,
                                    marginTop: 16,
                                }}
                                actions={[
                                    <MessageFilled key="createSession" onClick={() => createThread(assistant.id, assistant.name)} />,
                                    <EditOutlined onClick={() => {setAssistantToModify(assistant); setOpenCreateAssistantModal(true); }}/>,
                                    <CloseCircleOutlined onClick={() => deleteAssistant(assistant.id)}/>,
                                ]}
                            >
                                <Meta
                                    avatar={<Avatar style={{ backgroundColor: '#eee' }}>{assistant.metadata.icon ?? '🤖'}</Avatar>}
                                    title={assistant.name}
                                />
                                <div className='pt-3'>
                                    <Text type="secondary">
                                        {assistant.description}
                                    </Text>
                                </div>
                            </Card>
                        </List.Item>
                    )}

                />

            <Modal
                    title="Build your assistant"
                    //centered
                    open={openCreateAssistantModal}
                    onOk={() => {createAssistant(assistantToModify ? assistantToModify.id : null)}}
                    onCancel={() => {createAssistantForm.resetFields();setOpenCreateAssistantModal(false); setAssistantToModify(null)}}
                    afterOpenChange={() => createAssistantForm.resetFields()}
                >
                    <Form form={createAssistantForm} layout="vertical">
                        <Form.Item label="Name" name='name' initialValue={assistantToModify ? assistantToModify.name : null}>
                            <Input
                                type='text'
                                placeholder="Name"
                            />
                        </Form.Item>
                        <Form.Item label='Description' name='desc' initialValue={assistantToModify ? assistantToModify.description : null} >
                            <Input
                                type='text'
                                //style={{width: 200}}
                                placeholder="Description"
                            />
                        </Form.Item>
                        <Form.Item label='Instructions' name='instructions' initialValue={assistantToModify ? assistantToModify.instructions : null}>
                            <TextArea
                                autoSize
                                //style={{width: 200}}
                                placeholder="Instructions"
                            />
                        </Form.Item>
                        <Form.Item label="Model" name='model' initialValue={assistantToModify ? assistantToModify.model : null}>
                            <Input
                                type='text'
                                placeholder="Model name"
                            />
                        </Form.Item>
                        <Form.Item label='Tools' name='tools' initialValue={assistantToModify ? JSON.stringify(assistantToModify.tools) : null}>
                            <TextArea
                                autoSize
                                //style={{width: 200}}
                                placeholder='tools settings, like: [{"type": "$iur"}, {"type": "retrieval"}]'
                            />
                        </Form.Item>
                        <Form.Item label='Files' name='file_ids' initialValue={assistantToModify ? JSON.stringify(assistantToModify.file_ids) : null}>
                            <TextArea
                                autoSize
                                placeholder='file_ids, like: ["file_1", "file_2"]'
                            />
                        </Form.Item>
                        <Form.Item label='Metadata' name='metadata' initialValue={assistantToModify ? JSON.stringify(assistantToModify.metadata) : null}>
                            <TextArea
                                autoSize
                                //style={{width: 200}}
                                placeholder='metadata, like: {"retrieval_collection": "default"}'
                            />
                        </Form.Item>
                        <Form.Item label='Avatar' name='icon' initialValue={assistantToModify ? assistantToModify.metadata.icon : "🤖"}>
                            <Input
                                type='text'
                                style={{width: 50, height: 50, fontSize: 24}}
                            />
                        </Form.Item>
                    </Form>
                </Modal>
            </Sider>
        </Layout>
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