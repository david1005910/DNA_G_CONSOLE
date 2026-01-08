export const parseGeneticRecord = (data) => {
    // 튜플 데이터 [id, dna, birth, death] 또는 이미 객체인 경우 처리
    if (Array.isArray(data)) {
        return {
            record_id: data[0],
            dna_sequence: data[1],
            birth_time: data[2],
            death_time: data[3],
            status: data[3] ? 'DECEASED' : 'ALIVE'
        };
    }
    // API에서 JSON 객체로 반환된 경우 (records.py 수정 필요 가능성 있음, 현재는 튜플로 반환될 수 있음)
    // records.py의 get_records는 현재 튜플 리스트를 반환함.
    // 하지만 get_record(id) 등은 객체를 반환하도록 수정되었을 수 있음.
    // 안전하게 처리:
    return {
        ...data,
        status: data.death_time ? 'DECEASED' : 'ALIVE'
    };
};
