import React, { useEffect } from 'react';

import { useState } from 'react'

import {
    Layout,
    Form,
    Input,
    Button,
    Row,
    Col,
    Avatar,
    Alert,
    Spin
} from 'antd';

import { BulbOutlined } from '@ant-design/icons'

import { fetchEventSource } from '@microsoft/fetch-event-source'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const { TextArea } = Input;

let abortController = null;

export const Chat = (props) => {

    const [form] = Form.useForm();
    const [error, setError] = useState(null);
    const [generating, setGenerating] = useState(false);
    const [currentReply, setCurrentReply] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    const onKeyDown = (e) => {
        if (e.keyCode === 13/*enter*/ && (e.ctrlKey || e.metaKey)) {
            onSubmit();
        }
    }

    const setHistoryScroll = () => {
        let history_div = document.getElementById('history');
        if (history_div) {
            setTimeout(() => {
                history_div.scrollTop = history_div.scrollHeight;
            }, 0);
        }
    }

    const onSubmit = () => {
        setError(null);
        setGenerating(true);
        abortController = new AbortController();

        let values = form.getFieldsValue();
        if (!values.prompt) {
            //setError("Prompt required!");
            setGenerating(false);
            return;
        }

        let prompt_variable = props.prompt_variable;
        if (!prompt_variable) {
            prompt_variable = 'prompt';
        }

        createMesage(props.thread_id, values.prompt);
        //createRun(props.name, props.thread_id)
        createRunStream(props.name, props.thread_id);

        //let req = {}
        //req[prompt_variable] = values.prompt;

        history.push({ role: 'user', message: values.prompt });
        setHistoryScroll();
        form.setFieldValue('prompt', '');
        //getReply(req);
    }

    const createMesage = (thread_id, content) => {
        fetch(`/api/v1/threads/${thread_id}/messages`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                'role': 'user',
                'content': content
            })
        });
    }

    const createRun = (assistant_id, thread_id) => {
        fetch(`/api/v1/threads/${thread_id}/runs`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                'assistant_id': assistant_id
            })
        })
        .then(r => r.json())
        .then(run => {
            //getReply(thread_id, run.id);
        });
    }

    const loadHistory = () => {
        let name = props.name;
        let thread_id = props.thread_id;

        if (name && thread_id) {
            setLoading(true);
            fetch(`/api/v1/threads/${thread_id}/messages`)
                .then(r => r.json())
                .then(messages => {
                    setLoading(false);
                    let t_history = [];
                    for (let i = messages.data.length - 1; i >= 0; i--) {
                        let msg = messages.data[i];

                        let content = msg.content[0].text[0].value;
                        if (msg.extra) {
                            content += '\n\n' + msg.extra;
                        }

                        t_history.push({
                            role: msg.role,
                            message: content
                        });
                    }
                    setHistory(t_history);

                    setHistoryScroll();
                });
        }
    }

    const createRunStream = (assistant_id, thread_id) => {
        var reply = '';

        fetchEventSource(`/api/v1/threads/${thread_id}/runs?stream=true`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'assistant_id': assistant_id
            }),
            signal: abortController.signal,
            onopen(response) {
                if (response.ok /*&& response.headers.get('content-type') === EventStreamContentType*/) {
                    return; // everything's good
                } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
                    // client-side errors are usually non-retriable:

                    setError('Something wrong! ERR: ' + response.statusText);
                    abortController.abort();
                    setGenerating(false);

                    //throw new FatalError();
                } else {
                    abortController.abort();// don't retry
                    setGenerating(false);
                    //throw new RetriableError();
                }
            },
            onmessage(msg) {
                if (msg.event === 'error') {
                    let j = JSON.parse(msg.data);
                    let e = j['error'];
                    setError(e);
                    setGenerating(false);
                } else if (msg.event === 'message') {
                    let j = JSON.parse(msg.data);
                    let c = j['c'];
                    //let vname = j['variable'];

                    if (c) {
                        //if (variable_name !== '' && variable_name !== vname) {
                        //    reply = reply + '\n\n';
                        //}
                        //variable_name = vname;

                        reply = reply + c;
                        setCurrentReply(reply + "▁");
                        setHistoryScroll();
                    }
                } else {
                    console.log("Unkow event: " + msg.data);
                }
            },
            onerror(err) {
                setGenerating(false);
                throw err;
            },
            onclose() {
                history.push({ role: 'ai', message: reply });
                setCurrentReply(null);
                setGenerating(false);

                if (props.onMessageReceived) {
                    props.onMessageReceived(thread_id, reply);
                }
            }
        });
    };

    const abort = () => {
        abortController.abort();
        setGenerating(false);
    };

    useEffect(() => {
        loadHistory();
    }, [props.name, props.thread_id]);

    return (
        <Layout
            style={{
                width: props.width ? props.width : '800px',
                height: props.height ? props.height : '600px',
            }}
            className="p-0 bg-white"
        >
            <div id="history" className='mb-auto overflow-auto scrollbar-none px-3'>
                {loading ? <div className='text-center'><Spin size="small" /></div> : null}
                <MessageHistory history={history} icon={props.icon} user={props.user}/>
                <div>
                    {currentReply ? (
                        <Message role='ai' message={currentReply} />
                    ) : null}
                    {generating ? (
                        <div className="text-center mt-2 mb-3">
                            <Button onClick={abort}><Spin size="small" style={{marginRight: 10}}/> <strong>Cancel</strong></Button>
                        </div>
                    ) : null}
                </div>

                {error ? (
                    <Alert message={error} type="error" showIcon style={{ marginTop: '10px' }} />
                ) : null}
            </div>
            <Form
                form={form}
                layout='horizontal'
                onFinish={onSubmit}
                style={{
                }}
                className='mb-0 p-3 border-top border-light'
            >
                <Row wrap={false} align="bottom">
                    <Col flex="auto">
                        <Form.Item
                            name="prompt"
                            style={{ marginBottom: 0 }}
                        >
                            <TextArea autoSize onKeyDown={onKeyDown} placeholder="" disabled={generating} />
                        </Form.Item>
                    </Col>
                    <Col flex='none'>
                        <Form.Item style={{ marginLeft: '15px', marginBottom: 0 }}>
                            <Button htmlType='submit' type="primary" shape="circle"  disabled={generating}>
                                <BulbOutlined />
                            </Button>
                        </Form.Item>
                    </Col>
                </Row>
                <div className='d-none d-lg-block small text-secondary mt-2'>CTRL + ENTER / ⌘ + ENTER</div>
            </Form>
        </Layout>
    );
}

const Message = (props) => {
    return (
        <div className='mb-3'>
            <div className={props.role === 'user' ? 'd-flex flex-row-reverse' : 'd-flex flex-row'}>
                <div style={{ width: '32px' }}>
                    <Avatar
                        style={{
                            color: '#666',
                            backgroundColor: props.role === 'user' ? '#eee' : '#eee',
                            verticalAlign: 'middle',
                        }}
                    >
                        {props.role === 'user' ? (props.user && props.user.username) ? props.user.username.substring(0,2) : '🦤' : props.icon ?? 'AI'}
                    </Avatar>
                </div>
                <div className='card mx-3 border-0'
                    style={{
                        backgroundColor: props.role === 'user' ? '#E8F8F5' : '#f8f9fa'
                    }}
                >
                    <div className='px-3 pt-3 pb-0'>
                        <ReactMarkdown children={props.message} remarkPlugins={[remarkGfm]} className='p-0 m-0'>

                        </ReactMarkdown>
                    </div>
                </div>
            </div>
        </div>
    );
}

const MessageHistory = (props) => {
    return (
        <div>
            {Object.keys(props.history).map((k, i) => {
                let h = props.history[i];
                return <Message role={h.role} message={h.message} key={i} icon={props.icon} user={props.user}/>;
            })}
        </div>
    );
}