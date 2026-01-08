# filename: src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.js'; // .js 확장자 명시 (브라우저에서 직접 로드 시 필요)

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
