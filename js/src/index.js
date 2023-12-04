import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Aify } from './aify'
import { getSecretKey, Login } from './user';

import 'bootstrap/dist/css/bootstrap.css'
import './index.css'

export const createAify = (elementId, chatMode = false, assistantId = null) => {
    const root = ReactDOM.createRoot(document.getElementById(elementId));
    root.render(
        <React.StrictMode>
            {getSecretKey() ? (
                <Aify chatMode={chatMode} assistantId={assistantId} />
            ) : (
                <Login />
            )}
        </React.StrictMode>
    );
}
window.createAify = createAify;
//export default createAify;