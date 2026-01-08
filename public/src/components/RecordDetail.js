import React from 'react';

const RecordDetail = ({ record }) => {
    if (!record) return <div><h2>🔍 Detail View</h2><p>Select a record to view details.</p></div>;

    return (
        <div>
            <h2>🔍 Record Details</h2>
            <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '5px' }}>
                <p><strong>ID:</strong> {record.record_id}</p>
                <p><strong>Status:</strong> <span className={`status-${record.status}`}>{record.status}</span></p>
                <p><strong>Born:</strong> {new Date(record.birth_time).toLocaleString()}</p>
                {record.death_time && <p><strong>Died:</strong> {new Date(record.death_time).toLocaleString()}</p>}
                <hr/>
                <p><strong>DNA Sequence:</strong></p>
                <div style={{ background: '#333', color: '#0f0', padding: '10px', fontFamily: 'monospace', wordBreak: 'break-all', borderRadius: '3px' }}>
                    {record.dna_sequence}
                </div>
                <hr/>
                <p><strong>AI Prediction (Type):</strong> {record.predicted_type || 'N/A'}</p>
            </div>
        </div>
    );
};

export default RecordDetail;
