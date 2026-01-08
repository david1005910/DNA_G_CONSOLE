# filename: src/components/RecordDetail.js
import React from 'react';
import { transcribeToRna } from '../utils/geneticRecordModel.js'; // .js 확장자 명시

function RecordDetail({ record }) {
    if (!record) {
        return (
            <div className="section record-detail">
                <h2>기록 상세 정보</h2>
                <p className="no-records">왼쪽 목록에서 기록을 선택해주세요.</p>
            </div>
        );
    }

    const rnaSequence = transcribeToRna(record.dna_sequence);

    return (
        <div className="section record-detail">
            <h2>기록 상세 정보</h2>
            <dl>
                <dt>기록 ID:</dt>
                <dd>{record.record_id}</dd>

                <dt>현재 상태:</dt>
                <dd>
                    <span className={`status-tag ${record.death_time ? 'deceased' : 'alive'}`}>
                        {record.death_time ? '소멸됨' : '활성'}
                    </span>
                </dd>

                <dt>DNA 서열:</dt>
                <dd>{record.dna_sequence}</dd>

                <dt>RNA 서열:</dt>
                <dd>{rnaSequence}</dd>

                <dt>생성 시간:</dt>
                <dd>{record.birth_time.toLocaleString()}</dd>

                {record.death_time && (
                    <>
                        <dt>소멸 시간:</dt>
                        <dd>{record.death_time.toLocaleString()}</dd>
                    </>
                )}
            </dl>
        </div>
    );
}

export default RecordDetail;
