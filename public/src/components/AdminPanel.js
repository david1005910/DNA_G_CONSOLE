import React, { useState, useEffect } from 'react';
import ReadmeViewer from './ReadmeViewer.js';
import ApiTester from './ApiTester.js';
import RecordForm from './RecordForm.js';
import RecordList from './RecordList.js';
import RecordDetail from './RecordDetail.js';

const AdminPanel = ({ 
    records, 
    selectedRecord, 
    onAddRecord, 
    onSelectRecord, 
    onTerminateRecord, 
    selectedRecordId 
}) => {
    const [activeTab, setActiveTab] = useState('readme'); // Default to README for "instruction first" approach
    const [systemStatus, setSystemStatus] = useState(null);

    useEffect(() => {
        if (activeTab === 'system') {
            fetch('http://127.0.0.1:5001/api/system/status')
                .then(res => res.json())
                .then(data => setSystemStatus(data))
                .catch(err => console.error(err));
        }
    }, [activeTab]);

    const tabs = [
        { id: 'readme', label: '📖 README' },
        { id: 'records', label: '🧬 Records' },
        { id: 'api', label: '🔬 API Tester' },
        { id: 'system', label: '⚙️ System' }
    ];

    return (
        <div className="admin-panel" style={{ margin: '20px 0', fontFamily: 'Noto Sans KR, sans-serif' }}>
            <div className="tabs" style={{ display: 'flex', borderBottom: '2px solid #ddd', marginBottom: '20px' }}>
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        style={{
                            padding: '12px 24px',
                            border: 'none',
                            background: activeTab === tab.id ? '#007bff' : 'transparent',
                            color: activeTab === tab.id ? '#fff' : '#555',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            fontSize: '1rem',
                            borderTopLeftRadius: '5px',
                            borderTopRightRadius: '5px',
                            transition: 'all 0.2s'
                        }}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="tab-content" style={{ padding: '0 10px' }}>
                {activeTab === 'readme' && <ReadmeViewer />}
                
                {activeTab === 'records' && (
                    <div className="records-dashboard">
                        <div className="container" style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
                            <div style={{ flex: 1 }}>
                                <RecordForm onAddRecord={onAddRecord} />
                            </div>
                            <div style={{ flex: 1 }}>
                                <RecordDetail record={selectedRecord} />
                            </div>
                        </div>
                        <div className="container">
                            <RecordList
                                records={records}
                                onSelectRecord={onSelectRecord}
                                onTerminateRecord={onTerminateRecord}
                                selectedRecordId={selectedRecordId}
                            />
                        </div>
                    </div>
                )}

                {activeTab === 'api' && <ApiTester />}
                
                {activeTab === 'system' && (
                    <div style={{ padding: '20px', background: '#eef', borderRadius: '5px', border: '1px solid #ccd' }}>
                        <h3>System Status</h3>
                        {systemStatus ? (
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                <li style={{ marginBottom: '10px' }}>
                                    <strong>Database:</strong> <span style={{ color: 'green' }}>●</span> {systemStatus.database}
                                </li>
                                <li style={{ marginBottom: '10px' }}>
                                    <strong>ML Model:</strong> <span style={{ color: systemStatus.ml_model === 'Loaded' ? 'green' : 'red' }}>●</span> {systemStatus.ml_model}
                                </li>
                                <li style={{ marginBottom: '10px' }}>
                                    <strong>XAI Service:</strong> <span style={{ color: 'green' }}>●</span> {systemStatus.xai_service}
                                </li>
                            </ul>
                        ) : (
                            <p>Loading status...</p>
                        )}
                        <hr />
                        <h4>Actions</h4>
                        <p>ℹ️ To retrain the model, run <code>python train_model.py</code> in the terminal.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminPanel;
