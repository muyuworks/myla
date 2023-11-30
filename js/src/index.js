import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Aify } from './aify'

import 'bootstrap/dist/css/bootstrap.css'
import './index.css'

export const createAify = (elementId, chatMode=false, assistantId=null) => {
    const root = ReactDOM.createRoot(document.getElementById(elementId));
    root.render(
        <React.StrictMode>
            <Aify chatMode={chatMode} assistantId={assistantId}/>
        </React.StrictMode>
    );
}
window.createAify = createAify;
//export default createAify;