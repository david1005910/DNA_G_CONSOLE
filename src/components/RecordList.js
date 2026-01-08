# filename: src/components/RecordList.js
import React from 'react';

function RecordList({ records, onSelectRecord, onTerminateRecord, selectedRecordId }) {
    if (records.length === 0) {
        return (
            <div className="section record-list section-full">
                <h2>유전 기록 목록</h2>
                <p className="no-records">아직 생성된 유전 기록이 없습니다.</p>
            </div>
        );
    }

    return (
        <div className="section record-list section-full">
            <h2>유전 기록 목록</h2>
            <ul>
                {records.map(record => (
                    <li key={record.record_id} className={record.record_id === selectedRecordId ? 'selected' : ''}>
                        <div className="record-list-item-header">
                            <strong>ID: {record.record_id.substring(0, 8)}...</strong>
                            <div>
                                <span className={`status-tag ${record.death_time ? 'deceased' : 'alive'}`}>
                                    {record.death_time ? '소멸됨' : '활성'}
                                </span>
                                <span style={{ marginLeft: '10px' }}>
                                    생성: {record.birth_time.toLocaleString()}
                                </span>
                            </div>
                        </div>
                        <p>DNA 서열: {record.dna_sequence.substring(0, 40)}{record.dna_sequence.length > 40 ? '...' : ''}</p>
                        <div className="record-actions">
                            <button className="secondary" onClick={() => onSelectRecord(record.record_id)}>
                                상세 보기
                            </button>
                            {!record.death_time && (
                                <button className="danger" onClick={() => onTerminateRecord(record.record_id)}>
                                    소멸 처리
                                </button>
                            )}
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default RecordList;
