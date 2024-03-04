import { Button, Divider, Form, Input, message } from "antd"
import { getUser, logout } from "./user"

export const Settings = () => {
    const [changePasswordForm] = Form.useForm()
    const [msg, msgContext] = message.useMessage()

    const changePassword = () => {
        let user = getUser();

        let password = changePasswordForm.getFieldValue('password');
        let confirm_pwd = changePasswordForm.getFieldValue("confirm_pwd");

        if (password !== confirm_pwd) {
            msg.error("Password conflict.");
            return
        }

        fetch(`/api/v1/users/${user.username}/password`, {
            method: 'PUT',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({"password": password})
        }).then(r => {
            if (r.status === 200) {
                msg.success("OK");
                changePasswordForm.resetFields();
            } else {
                throw new Error("Status: " + r.status);
            }
        }).catch(err => {
            msg.error(err.message);
        })
    }

    const changeProfile = () => {
        
    }

    return (
        <div>
            {msgContext}
            <div style={{marginBottom: 15}}><strong>Profile</strong></div>
            <Form>
                <Form.Item name='icon' initialValue={'🐼'}>
                    <Input
                        type='text'
                        style={{ width: 50, height: 50, fontSize: 24 }}
                    />
                </Form.Item>
            </Form>

            <Divider />
            <div style={{marginBottom: 15}}><strong>Change password</strong></div>
            <Form
                form={changePasswordForm}
                labelCol={{ flex: '120px' }}
                colon={false}
                onFinish={changePassword}
            >
                <Form.Item label="New password" name='password'
                    rules={[
                        {
                            required: true
                        }
                    ]}
                >
                    <Input.Password style={{width: 200}}/>
                </Form.Item>
                <Form.Item label="Confirm" name='confirm_pwd'
                    rules={[
                        {
                            required: true
                        }
                    ]}
                >
                    <Input.Password style={{width: 200}} />
                </Form.Item>
                <Form.Item label=' '>
                    <Button type="primary" htmlType="submit">
                        Change password
                    </Button>
                </Form.Item>
            </Form>

            <Divider />
            <div style={{textAlign: 'center'}}>
                <Button type="primary" danger onClick={logout}>
                    Logout
                </Button>
            </div>
        </div>
    )
}