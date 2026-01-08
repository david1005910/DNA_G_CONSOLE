import React, { useState } from 'react';

const ApiTester = () => {
    const [method, setMethod] = useState('GET');
    const [endpoint, setEndpoint] = useState('/records');
    const [body, setBody] = useState('');
    const [response, setResponse] = useState(null);

    const handleTest = () => {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (method === 'POST' || method === 'PUT') {
            try {
                options.body = JSON.stringify(JSON.parse(body));
            } catch (e) {
                alert('Invalid JSON in body');
                return;
            }
        }

        fetch(`http://127.0.0.1:5001/api${endpoint}`, options)
            .then(res => res.json().then(data => ({ status: res.status, data })))
            .then(result => setResponse(result))
            .catch(err => setResponse({ error: err.message }));
    };

    return (
        <div style={{ padding: '20px', background: '#f9f9f9', border: '1px solid #ddd' }}>
            <h3>🔬 API Tester</h3>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <select value={method} onChange={e => setMethod(e.target.value)}>
                    <option>GET</option>
                    <option>POST</option>
                    <option>PUT</option>
                    <option>DELETE</option>
                </select>
                <input 
                    type="text" 
                    value={endpoint} 
                    onChange={e => setEndpoint(e.target.value)} 
                    placeholder="/records" 
                    style={{ flex: 1 }}
                />
                <button onClick={handleTest}>Send Request</button>
            </div>
            {(method === 'POST' || method === 'PUT') && (
                <textarea 
                    value={body} 
                    onChange={e => setBody(e.target.value)} 
                    placeholder='{"key": "value"}'
                    style={{ width: '100%', height: '100px', marginBottom: '10px' }}
                />
            )}
            {response && (
                <pre style={{ background: '#333', color: '#fff', padding: '10px', overflowX: 'auto' }}>
                    {JSON.stringify(response, null, 2)}
                </pre>
            )}
        </div>
    );
};

export default ApiTester;
