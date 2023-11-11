import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { useState } from 'react'
import { Layout, List, Avatar, Space, Typography, Button, Card, Modal, Form, Input } from 'antd'
import { MenuUnfoldOutlined, MenuFoldOutlined, MessageFilled, PlusCircleOutlined } from '@ant-design/icons'
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
    const [asistants, setAsistants] = useState();
    const [assistantMap, setAsistantMap] = useState({});
    const [currentAssistantId, setCurrentAsistantId] = useState(null);
    const [currentThreadId, setCurrentThreadId] = useState(null);
    const [threads, setThreads] = useState();
    
    const [welcomMessage, setWelcomeMessage] = useState();
    const [user, setUser] = useState();

    const [openCreateAssistantModal, setOpenCreateAssistantModal] = useState(false);
    const [createAssistantForm] = Form.useForm();

    const createAssistant = () => {
        let name = createAssistantForm.getFieldValue("name");
        let desc = createAssistantForm.getFieldValue("desc");
        let instructions = createAssistantForm.getFieldValue("instructions");
        let icon = createAssistantForm.getFieldValue("icon");
        let tools = createAssistantForm.getFieldValue("tools");
        var metadata = createAssistantForm.getFieldValue("metadata");
        metadata = metadata ? JSON.parse(metadata) : {}
        metadata.icon = icon

        fetch("/api/v1/assistants", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "name": name,
                "description": desc,
                "model": '',
                "instructions": instructions,
                "tools": JSON.parse(tools ? tools : []),
                "metadata": metadata
            })
        }).then(r => {
            loadAsistants();
            setOpenCreateAssistantModal(false);
        });
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
                setAsistants(asis.data);
                setAsistantMap(m);
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
                    backgroundColor: '#eee'
                }}
                width={300}
                collapsedWidth={65}
                trigger={null}
            >
                <List
                    size='small'
                    itemLayout="horizontal"
                    dataSource={threads}
                    renderItem={(thread => (
                        <List.Item>
                            <Link
                                onClick={() => switchThread(thread.metadata.assistant_id, thread.id)}
                            >
                                <Space>
                                    <Avatar style={{ backgroundColor: '#fff' }}>{(assistantMap[thread.metadata.assistant_id] && assistantMap[thread.metadata.assistant_id].metadata.icon) ?? '🤖'}</Avatar>
                                    {!leftCollapsed ? (
                                        <Space direction='vertical' size={0}>
                                            <Text type="secondary"
                                                ellipsis={{
                                                    rows: 1,
                                                }}
                                                style={{ width: '220px' }}
                                            >
                                                <div id={`last-msg-${thread.id}`}>{assistantMap[thread.metadata.assistant_id].name}</div>
                                            </Text>
                                        </Space>
                                    ) : null}

                                </Space>
                            </Link>
                        </List.Item>
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
                        icon={leftCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => setLeftCollapsed(!leftCollapsed)}
                        style={{
                            fontSize: '14px',
                        }}
                        className='me-auto'
                    />
                    <Button
                        type="text"
                        icon={rightCollapsed ? <MenuFoldOutlined /> : <MenuUnfoldOutlined />}
                        onClick={() => setRightCollapsed(!rightCollapsed)}
                        style={{
                            fontSize: '14px',
                        }}
                        className='ms-auto'
                    />
                </div>
                {(currentAssistantId != null && currentThreadId != null) ? (
                    <Chat
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
                    backgroundColor: '#eee'
                }}
                width={300}
                collapsedWidth={0}
                trigger={null}
                reverseArrow
            >
                <div style={{marginLeft: 15, marginRight: 15, marginTop: 20}}>
                    <Button type="dashed" block onClick={() => setOpenCreateAssistantModal(true)}>
                        <PlusCircleOutlined />
                    </Button>
                </div>
                <List
                    split={false}
                    size='small'
                    itemLayout="horizontal"
                    dataSource={asistants}
                    renderItem={(asistant) => (
                        <List.Item>
                            <Card
                                style={{
                                    width: 268,
                                    marginTop: 16,
                                }}
                                actions={[
                                    <span><MessageFilled key="createSession" onClick={() => createThread(asistant.id, asistant.name)} /></span>,
                                ]}
                            >
                                <Meta
                                    avatar={<Avatar style={{ backgroundColor: '#eee' }}>{asistant.metadata.icon ?? '🤖'}</Avatar>}
                                    title={asistant.name}
                                />
                                <div className='pt-3'>
                                    <Text type="secondary">
                                        {asistant.description}
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
                    onOk={() => createAssistant()}
                    onCancel={() => setOpenCreateAssistantModal(false)}
                >
                    <Form form={createAssistantForm}>
                        <Form.Item name='name' >
                            <Input
                                type='text'
                                style={{width: 200}}
                                placeholder="Name"
                            />
                        </Form.Item>
                        <Form.Item name='desc' >
                            <Input
                                type='text'
                                //style={{width: 200}}
                                placeholder="Description"
                            />
                        </Form.Item>
                        <Form.Item name='instructions' >
                            <TextArea
                                rows={3}
                                //style={{width: 200}}
                                placeholder="Instructions"
                            />
                        </Form.Item>
                        <Form.Item name='tools'>
                            <TextArea
                                rows={3}
                                //style={{width: 200}}
                                placeholder='tools settings, like: [{"type": "$iur"}, {"type": "retrieval"}]'
                            />
                        </Form.Item>
                        <Form.Item name='metadata'>
                            <TextArea
                                rows={3}
                                //style={{width: 200}}
                                placeholder='metadata, like: {"retrieval_collection_name": "uco"}'
                            />
                        </Form.Item>
                        <Form.Item name='icon' initialValue={"🤖"}>
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