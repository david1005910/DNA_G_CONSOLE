import React, { useState } from 'react';

const RecordForm = ({ onAddRecord }) => {
    const [dnaSequence, setDnaSequence] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (dnaSequence.trim()) {
            onAddRecord(dnaSequence);
            setDnaSequence('');
        }
    };

    return (
        <div>
            <h2>🧬 Create DNA Record</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Enter DNA Sequence (e.g., ATCG...)"
                    value={dnaSequence}
                    onChange={(e) => setDnaSequence(e.target.value.toUpperCase().replace(/[^ATCG]/g, ''))}
                />
                <button type="submit">Analyze & Save</button>
            </form>
            <div style={{marginTop: '10px'}}>
                <button onClick={() => setDnaSequence('ATCG'.repeat(5) + 'GCG'.repeat(5))} style={{background: '#6c757d', marginRight: '5px'}}>Example Type A</button>
                <button onClick={() => setDnaSequence('ATCG'.repeat(10))} style={{background: '#6c757d'}}>Example Type B</button>
            </div>
        </div>
    );
};

export default RecordForm;
