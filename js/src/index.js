import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { create, Aify } from './aify'

import 'bootstrap/dist/css/bootstrap.css'
import './index.css'

const root = ReactDOM.createRoot(document.getElementById("aify"));
root.render(
    <React.StrictMode>
        <Aify />
    </React.StrictMode>
);