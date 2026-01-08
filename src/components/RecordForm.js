# filename: src/components/RecordForm.js
import React, { useState } from 'react';

function RecordForm({ onAddRecord }) {
    const [dnaInput, setDnaInput] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(''); // 에러 초기화
        if (!dnaInput.trim()) {
            setError('DNA 서열을 입력해주세요.');
            return;
        }
        if (!/^[ATCGatcg]+$/.test(dnaInput)) {
            setError("'A', 'T', 'C', 'G' 문자만 입력 가능합니다.");
            return;
        }
        onAddRecord(dnaInput.trim().toUpperCase());
        setDnaInput('');
    };

    return (
        <div className="section">
            <h2>새로운 유전 기록 생성</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="dnaSequence">DNA 서열:</label>
                    <textarea
                        id="dnaSequence"
                        rows="5"
                        value={dnaInput}
                        onChange={(e) => setDnaInput(e.target.value)}
                        placeholder="예: ATCGATCGATCG..."
                        required
                    ></textarea>
                </div>
                {error && <p style={{ color: 'red', fontSize: '0.9em' }}>{error}</p>}
                <button type="submit" className="primary">기록 생성</button>
            </form>
        </div>
    );
}

export default RecordForm;
