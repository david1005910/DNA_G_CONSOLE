import React from 'react';

const RecordList = ({ records, onSelectRecord, onTerminateRecord, selectedRecordId }) => {
    return (
        <div>
            <h2>📚 Genetic Records ({records.length})</h2>
            <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #ddd' }}>
                <ul style={{ margin: 0 }}>
                    {records.map(record => (
                        <li 
                            key={record.record_id} 
                            style={{ 
                                background: selectedRecordId === record.record_id ? '#e3f2fd' : '#fff',
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px'
                            }}
                        >
                            <div onClick={() => onSelectRecord(record.record_id)} style={{ cursor: 'pointer', flex: 1 }}>
                                <strong>{record.record_id.slice(0, 8)}...</strong>
                                <span className={`status-${record.status}`} style={{ marginLeft: '10px' }}>{record.status}</span>
                                <br/>
                                <small>{new Date(record.birth_time).toLocaleString()}</small>
                            </div>
                            {record.status === 'ALIVE' && (
                                <button 
                                    onClick={(e) => { e.stopPropagation(); onTerminateRecord(record.record_id); }}
                                    style={{ background: '#dc3545', padding: '5px 10px' }}
                                >
                                    Terminate
                                </button>
                            )}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default RecordList;
