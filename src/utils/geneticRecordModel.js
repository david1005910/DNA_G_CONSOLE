# filename: src/utils/geneticRecordModel.js
import { v4 as uuidv4 } from 'https://jspm.dev/uuid'; // CDN을 통한 UUID 모듈 로드

/**
 * DNA 서열을 RNA 서열로 변환합니다. (T -> U)
 * @param {string} dnaSequence
 * @returns {string}
 */
export function transcribeToRna(dnaSequence) {
    if (typeof dnaSequence !== 'string') {
        return '';
    }
    return dnaSequence.toUpperCase().replace(/T/g, 'U');
}

/**
 * GeneticRecord 객체를 생성하는 팩토리 함수.
 * @param {string} dnaSequence
 * @returns {object} GeneticRecord 객체
 */
export function createGeneticRecord(dnaSequence) {
    if (!dnaSequence || !/^[ATCG]+$/i.test(dnaSequence)) {
        throw new Error("유효하지 않은 DNA 서열입니다. 'A', 'T', 'C', 'G'만 포함해야 합니다.");
    }

    const now = new Date();
    return {
        record_id: uuidv4(),
        dna_sequence: dnaSequence.toUpperCase(),
        birth_time: now.toISOString(), // ISO 8601 문자열 형식
        death_time: null, // 사망 시간은 초기에는 null
    };
}

/**
 * 저장된 데이터를 GeneticRecord 객체 형태로 변환합니다.
 * @param {object} rawData
 * @returns {object} GeneticRecord 객체
 */
export function parseGeneticRecord(rawData) {
    return {
        record_id: rawData.record_id,
        dna_sequence: rawData.dna_sequence,
        birth_time: new Date(rawData.birth_time),
        death_time: rawData.death_time ? new Date(rawData.death_time) : null,
    };
}
