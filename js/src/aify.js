import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { useState } from 'react'
import { Layout, List, Avatar, Space, Typography, Button, Form, Input, Skeleton, Tabs, Alert, Popover, Tag, message, Upload, Spin, Select } from 'antd'
import {
    MenuUnfoldOutlined,
    MenuFoldOutlined,
    PlusOutlined,
    CloseCircleOutlined,
    SettingOutlined,
    DeleteOutlined,
    UploadOutlined,
    ReloadOutlined
} from '@ant-design/icons'
import {

} from '@ant-design/icons';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm'
import { Chat } from './chat'
import Link from 'antd/es/typography/Link';
import TextArea from 'antd/es/input/TextArea';
import { SecretKeySettings } from './secret_key';
import { UserAdmin } from './user_admin';
import { Settings } from './settings';

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

        let tools_cfg = [];
        for (let i = 0; tools && i < tools.length; i ++) {
            tools_cfg.push({
                "type": tools[i]
            });
        }
        var body = {
            "name": name,
            "description": desc,
            "instructions": instructions,
            "model": model,
            "tools": tools ? tools_cfg : [],
            "file_ids": file_ids ? file_ids : [],
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
                //theme="light"
                style={{
                    height: '100vh',
                    borderRight: '1px solid #eee',
                    backgroundColor: '#FBFCFC'
                }}
                className='overflow-auto scrollbar-none'
                width={280}
                collapsedWidth={threads && threads.length > 0 ? 65 : 0}
                trigger={null}
            >
                <List
                    size='small'
                    itemLayout="horizontal"
                    locale={{ emptyText: ' ' }}
                    dataSource={threads}
                    renderItem={(thread => (
                        thread.metadata != null && assistantMap[thread.metadata.assistant_id] != null && (props.assistantId === null || (props.assistantId != null && props.assistantId === thread.metadata.assistant_id)) ? (
                            <List.Item style={currentThreadId === thread.id ? { backgroundColor: 'white' } : {}}>
                                <Space>
                                    <Link
                                        onClick={() => switchThread(thread.metadata.assistant_id, thread.id)}
                                    >
                                        <Space>
                                            <Avatar style={{ backgroundColor: '#eee', color: '#999' }}>{(assistantMap[thread.metadata.assistant_id].metadata != null && assistantMap[thread.metadata.assistant_id].metadata.icon) ?? '🤖'}</Avatar>
                                            {!leftCollapsed ? (
                                                <Space direction='horizontal' size={0}>
                                                    <Text type="secondary"
                                                        ellipsis={{
                                                            rows: 1,
                                                        }}
                                                        style={{ width: '190px', fontSize: '0.8rem' }}
                                                    >
                                                        <div id={`last-msg-${thread.id}`}>{assistantMap[thread.metadata.assistant_id].name}</div>
                                                    </Text>
                                                </Space>
                                            ) : null}

                                        </Space>
                                    </Link>
                                    {!leftCollapsed ? (
                                        <Link onClick={() => deleteThread(thread.id)}><CloseCircleOutlined style={{ color: '#ccc', marginTop: 15 }} className='thread-close' /></Link>
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
                //breakpoint="lg"
                theme="light"
                style={{
                    height: '100vh',
                    backgroundColor: '#FBFCFC',
                    borderLeft: '1px solid #eee',
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
                            label: <span>Assistants</span>,
                            children: <Assistants assistantId={props.assistantId} chatMode={props.chatMode} assistants={assistants} onCreate={createAssistant} onDelete={deleteAssistant} createThread={createThread} />
                        },
                        {
                            key: '2',
                            label: props.chatMode ? '' : <span>Files</span>,
                            children: <Files chatMode={props.chatMode}/>
                        },
                        {
                            key: '3',
                            label: props.chatMode ? '' : <span>API Keys</span>,
                            children: <SecretKeySettings/>
                        },
                        /*{
                            key: '4',
                            label: props.chatMode ? '' : <span>Users</span>,
                            children: <UserAdmin />
                        },
                        {
                            key: '5',
                            label: props.chatMode ? '' : <span>Settings</span>,
                            children: <Settings />
                        }*/
                    ]}
                    style={{paddingLeft: 15, paddingRight: 15}}
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
    const [msg, msgContextHolder] = message.useMessage();

    const [fileIdsOptions, setFileIdsOptions] = useState([]);
    const [toolsOptions, setToolsOptions] = useState();
    const [modelsOptions, setModelsOptions] = useState();

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

        props.onCreate(assistant)
            .then(() => {
                if (assistant.id != null) {
                    msg.open({
                        type: 'success',
                        content: "Success"
                    });
                } else {
                    onCancel();
                }
            })
            .catch(err => setError(err.message));

    }

    const onModify = (assistant) => {
        createAssistantForm.setFieldValue('name', assistant.name);
        createAssistantForm.setFieldValue('desc', assistant.desc);
        createAssistantForm.setFieldValue('instructions', assistant.instructions);
        createAssistantForm.setFieldValue('model', assistant.model);
        createAssistantForm.setFieldValue('icon', assistant.metadata.icon);
        createAssistantForm.setFieldValue('file_ids', assistant.file_ids);
        createAssistantForm.setFieldValue('metadata', JSON.stringify(assistant.metadata, null, 4));

        let tools = [];
        for (let i = 0; assistant.tools && i < assistant.tools.length; i ++) {
            tools.push(assistant.tools[i].type);
        }
        createAssistantForm.setFieldValue('tools', tools);

        setAssistantToModify(assistant);
        setFormView(true);
    }

    const listFiles = () => {
        fetch('/api/v1/files')
            .then(r => r.json())
            .then(data => {
                let options = []
                for (let i = 0; i < data.data.length; i ++) {
                    options.push({
                        label: data.data[i].filename,
                        value: data.data[i].id
                    });
                }
                setFileIdsOptions(options);
            });
    }

    const listTools = () => {
        fetch('/api/v1/tools')
            .then(r => r.json())
            .then(data => {
                let options = []
                for (let i = 0; i < data.length; i ++) {
                    options.push({
                        label: data[i],
                        value: data[i]
                    });
                }
                setToolsOptions(options);
            });
    }

    const listModels = () => {
        fetch('/api/v1/models')
            .then(r => r.json())
            .then(data => {
                let options = []
                for (let i = 0; data && i < data.data.length; i ++) {
                    options.push({
                        label: data.data[i].id,
                        value: data.data[i].id
                    });
                }
                setModelsOptions(options);
            });
    }

    useEffect(() => {
        listFiles();
        listTools();
        listModels();
    }, [formView])

    return (
        <div>
            {!formView ? (
                <div>
                    {!props.chatMode ? (
                        <Button
                            type="dashed"
                            shape="circle"
                            style={{ marginLeft: 15, marginBottom: 10 }}
                            onClick={() => setFormView(true)}
                        >
                            <PlusOutlined />
                        </Button>
                    ) : null}

                    <List
                        //split={false}
                        size='small'
                        itemLayout="horizontal"
                        locale={{ emptyText: ' ' }}
                        dataSource={props.assistants}
                        renderItem={(assistant) => (
                            props.assistantId == null || (props.assistantId != null && assistant.id === props.assistantId) ? (
                                <List.Item
                                    actions={[
                                        props.chatMode ? null : <SettingOutlined onClick={() => { onModify(assistant) }} />,
                                        props.chatMode ? null : <DeleteOutlined onClick={() => props.onDelete(assistant.id)} />,
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
                            ) : null
                        )}
                    />
                </div>
            ) : (
                <div>
                    {msgContextHolder}
                    <Link onClick={onCancel} style={{ marginBottom: 20, display: 'block' }}>&lt; Back</Link>
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
                            <Select
                                allowClear
                                placeholder="Select a model"
                                options={modelsOptions}
                            />
                        </Form.Item>
                        <Form.Item label='Tools' name='tools'>
                            <Select
                                mode="multiple"
                                allowClear
                                placeholder="Select tools"
                                options={toolsOptions}
                            />
                        </Form.Item>

                        <Form.Item label='Files' name='file_ids' extra={<Button onClick={listFiles} style={{marginTop: 10}} size='small'><ReloadOutlined /> Reload</Button>}>
                            <Select
                                mode="multiple"
                                allowClear
                                placeholder="Select files"
                                options={fileIdsOptions}
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

                        {assistantToModify ? (
                            <div style={{marginBottom: 10}}>
                                <Link href={`/assistants/${assistantToModify.id}`} target='_blank'>Share this assistant with others.</Link>
                            </div>
                        ) : null}

                        {error ? (<Alert message={error} type="error" showIcon style={{ marginBottom: 10 }} />) : null}

                        <Space style={{ marginBottom: 20 }}>
                            <Button type='default' onClick={() => { onCancel() }}>Cancel</Button>
                            <Button type='primary' onClick={onCreate}>{assistantToModify ? 'Save' : 'Create'}</Button>
                        </Space>
                    </Form>
                </div>
            )}
        </div>
    );
}

const Files = (props) => {
    const [uploadFileForm] = Form.useForm();
    const [formView, setFormView] = useState(false);
    const [error, setError] = useState();

    const [files, setFiles] = useState();
    const [uploading, setUploading] = useState(false);

    const listFiles = () => {
        fetch('/api/v1/files')
            .then(r => r.json())
            .then(data => {
                setFiles(data.data);
            });
    }

    const deleteFile = (id) => {
        fetch(`/api/v1/files/${id}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json"
            }
        }).then(r => {
            listFiles();
        })
    }

    useEffect(() => {
        listFiles();
    }, []);

    const onCancel = () => {
        uploadFileForm.resetFields();
        setFormView(false);
        setError(null);
    }

    const uploadFile = (upload) => {
        const formData = new FormData();
        formData.append('file', upload.file);
        formData.append('purpose', 'assistants');

        let embeddings = uploadFileForm.getFieldValue('embeddings');
        if (embeddings != null) {
            formData.append('embeddings', embeddings);
        }
        let metadata = uploadFileForm.getFieldValue('metadata');
        if (metadata != null) {
            try {
                metadata = JSON.parse(metadata);
                for (let k of Object.keys(metadata)) {
                    formData.append(k, metadata[k]);
                }
            } catch (err) {
                setError(err.message);
                return;
            }
        }

        setUploading(true);
        fetch('/api/v1/files', {
            method: 'POST',
            body: formData
        }).then(r => {
            if (r.status === 200) {
                return r.json();
            } else {
                throw new Error("Status: " + r.status);
            }
        }).then(data => {
            upload.onSuccess(data);
            setUploading(false);
            listFiles();
            onCancel();
        }).catch(err => {
            setUploading(false);
            upload.onError(err.message);
            setError(err.message);
        });
    }

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
                        dataSource={files}
                        renderItem={(file) => (
                            <List.Item
                                key={file.id}
                                actions={[
                                    //<CheckCircleOutlined onClick={() => props.selectFile(file)} style={{color: props.selectedFiles[file.id] ? 'green' : ''}} />,
                                    <DeleteOutlined onClick={() => {deleteFile(file.id)}} />,
                                ]}
                            >
                                <Skeleton title={false} loading={file.loading} active>
                                    <Popover
                                        trigger="click"
                                        content={
                                            <Space direction='vertical'>
                                                <div><strong>Purpose: </strong><Tag color='blue'>{file.purpose}</Tag></div>
                                                <div><strong>Id: </strong>{file.id}</div>
                                                <div><strong>Bytes: </strong>{file.bytes}</div>
                                                <div><strong>Created: </strong>{new Date(file.created_at * 1000).toLocaleString()}</div>
                                                <div><strong>Metadata: </strong>{JSON.stringify(file.metadata)}</div>
                                            </Space>
                                        }
                                    >
                                        <Link style={{ fontSize: '0.85rem', fontWeight: 'normal', color: '#666' }}>{file.filename}</Link>
                                    </Popover>
                                </Skeleton>
                            </List.Item>
                        )}
                    />
                </div>
            ) : (
                <div>
                    <Link onClick={onCancel} style={{ marginBottom: 20, display: 'block' }}>&lt; Back</Link>
                    <Form form={uploadFileForm} layout="vertical">
                        <Form.Item label='Embedding Columns' name='embeddings'>
                            <TextArea
                                autoSize
                                placeholder="Embedding columns, like: column1,column2"
                            />
                        </Form.Item>
                        <Form.Item label='Metadata' name='metadata'>
                            <TextArea
                                rows={5}
                                placeholder='metadata, like: {"metadata1": "value"}'
                            />
                        </Form.Item>

                        {error ? (<Alert message={error} type="error" showIcon style={{ marginBottom: 10 }} />) : null}

                        <div style={{marginBottom: 10, color: 'gray'}}>Available formats: csv, xsl, xlsx, pdf, json</div>
                        <Space style={{ marginBottom: 20 }}>
                            <Upload
                                name='file'
                                customRequest={uploadFile}
                                showUploadList={false}
                            >
                                <Button icon={<UploadOutlined />} type='primary' onClick={() => { }}>Upload</Button>
                            </Upload>
                            {uploading ? <Spin /> : null}
                        </Space>
                    </Form>
                </div>
            )}
        </div>
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