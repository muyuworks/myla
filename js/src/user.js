import { Button, Form, Input, message } from "antd"

import Cookies from 'js-cookie'

export const getUser = () => {
    let user = Cookies.get('user');
    return user
}

export const getSecretKey = () => {
    let sk = Cookies.get('secret_key');
    fetch('/api/v1/models').then(r => {
        if (r.status === 403) {
            Cookies.remove('user');
            Cookies.remove('secret_key');
        }
    })
    return sk
}

export const Login = (props) => {
    const [loginForm] = Form.useForm();
    const [msg, msgContextHolder] = message.useMessage();

    const login = () => {
        let username = loginForm.getFieldValue('username');
        let password = loginForm.getFieldValue('password');
        
        fetch(`/api/v1/users/${username}/login`, {
            method: 'POST',
            body: JSON.stringify({
                username: username,
                password: password
            }),
            headers: {"Content-Type": "application/json"}
        }).then(r => {
            if (r.status === 200) {
                return r.json();
            } else  if (r.status === 403) {
                throw new Error("Login faield");
            }
        }).then(data => {
            Cookies.set('user', JSON.stringify(data.user));
            Cookies.set('secret_key', data.secret_key.id);
            window.location.href = '/';
        }).catch(err => {
            msg.error(err.message);
        });
    }

    return (
        <Form
            form={loginForm}
            onFinish={login}
            style={{
                width: 500,
                margin: 'auto',
                marginTop: 50
            }}
        >
            {msgContextHolder}
            <Form.Item
                label="Username"
                name="username"
                rules={[
                    {
                        required: true
                    }
                ]}
            >
                <Input />
            </Form.Item>

            <Form.Item
                label="Password"
                name="password"
                rules={[
                    {
                        required: true
                    }
                ]}
            >
                <Input.Password autoComplete="true"/>
            </Form.Item>
            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Login
                </Button>
            </Form.Item>
        </Form>
    )
}