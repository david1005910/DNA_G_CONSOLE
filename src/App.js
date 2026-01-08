# filename: src/App.js
import React, { useState, useEffect } from 'react';
import RecordForm from './components/RecordForm.js';
import RecordList from './components/RecordList.js';
import RecordDetail from './components/RecordDetail.js';
import { createGeneticRecord, parseGeneticRecord } from './utils/geneticRecordModel.js'; // .js 확장자 명시

const LOCAL_STORAGE_KEY = 'dna_rna_records';

function App() {
    const [records, setRecords] = useState([]);
    const [selectedRecordId, setSelectedRecordId] = useState(null);

    // 컴포넌트 마운트 시 localStorage에서 기록 불러오기
    useEffect(() => {
        const storedRecords = localStorage.getItem(LOCAL_STORAGE_KEY);
        if (storedRecords) {
            const parsedRecords = JSON.parse(storedRecords).map(parseGeneticRecord);
            setRecords(parsedRecords);
        }
    }, []);

    // records 상태 변경 시 localStorage에 저장
    useEffect(() => {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(records));
    }, [records]);

    const handleAddRecord = (dnaSequence) => {
        try {
            const newRecord = createGeneticRecord(dnaSequence);
            setRecords(prevRecords => [newRecord, ...prevRecords]); // 최신 기록을 상단에 추가
            setSelectedRecordId(newRecord.record_id); // 새로 생성된 기록 선택
            console.log("새로운 기록 생성:", newRecord);
        } catch (error) {
            alert("기록 생성 오류: " + error.message);
        }
    };

    const handleSelectRecord = (id) => {
        setSelectedRecordId(id);
    };

    const handleTerminateRecord = (id) => {
        setRecords(prevRecords =>
            prevRecords.map(record =>
                record.record_id === id && record.death_time === null
                    ? { ...record, death_time: new Date().toISOString() }
                    : record
            )
        );
        console.log(`기록 ${id.substring(0, 8)}... 소멸 처리됨.`);
    };

    const selectedRecord = records.find(record => record.record_id === selectedRecordId) || null;

    return (
        <div>
            <h1>🧬 DNA/RNA 유전 정보 관리 시스템</h1>
            <div className="container">
                <RecordForm onAddRecord={handleAddRecord} />
                <RecordDetail record={selectedRecord} />
            </div>
            <div className="container">
                <RecordList
                    records={records}
                    onSelectRecord={handleSelectRecord}
                    onTerminateRecord={handleTerminateRecord}
                    selectedRecordId={selectedRecordId}
                />
            </div>
        </div>
    );
}

export default App;
