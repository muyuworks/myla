import { Button, Form, Input, message } from "antd"
import { getUser } from "./user"

export const Settings = () => {
    const [changePasswordForm] = Form.useForm()
    const [msg, msgContext] = message.useMessage()

    const changePassword = () => {
        let user = getUser();

        let password = changePasswordForm.getFieldValue('password');
        let confirm_pwd = changePasswordForm.getFieldValue("confirm_pwd");

        if (password != confirm_pwd) {
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

    return (
        <div>
            {msgContext}
            <strong>Change password</strong>
            <Form
                form={changePasswordForm}
                layout='vertical'
                onFinish={changePassword}
            >
                <Form.Item label="Password" name='password'
                    rules={[
                        {
                            required: true
                        }
                    ]}
                >
                    <Input.Password style={{width: 200}}/>
                </Form.Item>
                <Form.Item label="Confirm your password" name='confirm_pwd'
                    rules={[
                        {
                            required: true
                        }
                    ]}
                >
                    <Input.Password style={{width: 200}} />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit">
                        Change password
                    </Button>
                </Form.Item>
            </Form>
        </div>
    )
}