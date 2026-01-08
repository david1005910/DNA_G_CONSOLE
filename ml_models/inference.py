
import joblib
import numpy as np
import math
from collections import Counter

class BiologicalFeatureExtractor:
    """Standalone extractor for GenetiForest (RandomForest)"""
    def __init__(self, kmer_size=3):
        self.kmer_size = kmer_size
        self.kmers = self._generate_kmers(kmer_size)
    
    def _generate_kmers(self, k):
        bases = ['A', 'C', 'G', 'T']
        if k == 1: return bases
        return [b + s for b in bases for s in self._generate_kmers(k-1)]

    def transform(self, X):
        features = []
        for seq in X:
            seq = seq.upper().replace('U', 'T') 
            row = []
            length = len(seq)
            # 1. GC Content
            gc_content = (seq.count('G') + seq.count('C')) / length if length > 0 else 0
            row.append(gc_content)
            # 2. Shannon Entropy
            row.append(self._calculate_entropy(seq))
            # 3. K-mer Frequency
            total_kmers = length - self.kmer_size + 1
            if total_kmers > 0:
                counts = Counter([seq[i:i+self.kmer_size] for i in range(total_kmers)])
                for kmer in self.kmers:
                    row.append(counts.get(kmer, 0) / total_kmers)
            else:
                row.extend([0] * len(self.kmers))
            features.append(row)
        return np.array(features)

    def _calculate_entropy(self, seq):
        if not seq: return 0
        counts = Counter(seq)
        total = len(seq)
        entropy = 0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

class SequenceFeatureExtractor:
    """Standalone extractor for ViralBoost (GradientBoosting)"""
    def __init__(self, kmer_size=5):
        self.kmer_size = kmer_size
        self.kmers = self._generate_kmers(kmer_size)
        self.dinucleotides = ['AA', 'AT', 'AG', 'AC', 'TA', 'TT', 'TG', 'TC',
                              'GA', 'GT', 'GG', 'GC', 'CA', 'CT', 'CG', 'CC']
    
    def _generate_kmers(self, k):
        bases = ['A', 'C', 'G', 'T']
        if k == 1: return bases
        return [b + s for b in bases for s in self._generate_kmers(k-1)]

    def transform(self, X):
        features = []
        for seq in X:
            seq = seq.upper().replace('U', 'T')
            row = []
            length = len(seq)
            row.append((seq.count('G') + seq.count('C')) / length if length > 0 else 0) # GC
            row.append(self._calc_skew(seq, 'G', 'C')) # GC Skew
            row.append(self._calc_skew(seq, 'A', 'T')) # AT Skew
            row.append(self._calc_entropy(seq)) # Entropy
            # 5-mer (Top 20)
            t_kmers = length - self.kmer_size + 1
            if t_kmers > 0:
                k_counts = Counter([seq[i:i+self.kmer_size] for i in range(t_kmers)])
                row.extend([k_counts.get(k, 0) / t_kmers for k in self.kmers[:20]])
            else:
                row.extend([0] * 20)
            # Dinucleotides
            t_di = length - 1
            if t_di > 0:
                d_counts = Counter([seq[i:i+2] for i in range(t_di)])
                row.extend([d_counts.get(d, 0) / t_di for d in self.dinucleotides])
            else:
                row.extend([0] * 16)
            row.append(self._calc_repeat(seq)) # repeat score
            row.append(self._calc_cpg(seq, length)) # CpG
            row.extend(self._calc_codon_bias(seq)) # Codon Pos Bias
            features.append(row)
        return np.array(features)

    def _calc_skew(self, seq, b1, b2):
        c1, c2 = seq.count(b1), seq.count(b2)
        return (c1 - c2) / (c1 + c2) if (c1 + c2) > 0 else 0
    def _calc_entropy(self, seq):
        if not seq: return 0
        c = Counter(seq); t = len(seq); e = 0
        for v in c.values():
            p = v/t
            if p > 0: e -= p * math.log2(p)
        return e
    def _calc_repeat(self, seq):
        if len(seq) < 6: return 0
        cnt = 0
        for l in [2, 3, 4]:
            for i in range(len(seq) - l*2):
                if seq[i:i+l] == seq[i+l:i+l*2]: cnt += 1
        return cnt / len(seq)
    def _calc_cpg(self, seq, length):
        if length < 2: return 0
        obs = seq.count('CG')
        exp = (seq.count('C') * seq.count('G')) / length
        return obs / exp if exp > 0 else 0
    def _calc_codon_bias(self, seq):
        if len(seq) < 3: return [0] * 12
        p_c = [{}, {}, {}]
        for i in range(0, len(seq)-2, 3):
            for j in range(3):
                b = seq[i+j]
                if b in 'ATGC': p_c[j][b] = p_c[j].get(b, 0) + 1
        res = []
        for p in range(3):
            t = sum(p_c[p].values()) or 1
            for b in 'ATGC': res.append(p_c[p].get(b, 0) / t)
        return res

def predict_dna(sequence, confidence_threshold=0.55, rare_class_threshold=0.65):
    """
    DNA sequence prediction with confidence thresholds.
    
    Args:
        sequence: DNA sequence string
        confidence_threshold: Minimum confidence for general classification (default 55%)
        rare_class_threshold: Higher threshold for rare classes like Influenza B (default 65%)
    """
    # Load Models
    rf_model = joblib.load("dna_classifier.joblib")
    rf_scaler = joblib.load("scaler_rf.joblib")
    gb_model = joblib.load("sequence_model.joblib")
    gb_scaler = joblib.load("scaler_gb.joblib")
    
    # 1. GenetiForest Prediction (Synthetic vs Biological)
    extractor_rf = BiologicalFeatureExtractor()
    feat_rf = extractor_rf.transform([sequence])
    scaled_rf = rf_scaler.transform(feat_rf)
    type_basic = rf_model.predict(scaled_rf)[0]
    rf_proba = rf_model.predict_proba(scaled_rf)[0]
    rf_confidence = max(rf_proba)
    
    # 2. ViralBoost Prediction (Virus Type) with Confidence Check
    extractor_gb = SequenceFeatureExtractor()
    feat_gb = extractor_gb.transform([sequence])
    scaled_gb = gb_scaler.transform(feat_gb)
    
    gb_proba = gb_model.predict_proba(scaled_gb)[0]
    gb_confidence = max(gb_proba)
    predicted_idx = gb_proba.argmax()
    predicted_class = gb_model.classes_[predicted_idx]
    
    # 희귀 클래스 (Influenza B 등)는 더 높은 신뢰도 요구
    rare_classes = ['Influenza B', 'Chicken anemia virus']
    if predicted_class in rare_classes:
        effective_threshold = rare_class_threshold
    else:
        effective_threshold = confidence_threshold
    
    # 신뢰도 임계값 미달 시 'Unknown'으로 분류
    if gb_confidence < effective_threshold:
        type_virus = 'Unknown'
        virus_confidence = gb_confidence
    else:
        type_virus = predicted_class
        virus_confidence = gb_confidence
    
    return {
        "classification": type_basic,
        "classification_confidence": float(rf_confidence),
        "virus_identity": type_virus,
        "virus_confidence": float(virus_confidence),
        "raw_prediction": predicted_class,  # 원래 예측 (디버깅용)
        "raw_confidence": float(gb_confidence)
    }

if __name__ == "__main__":
    # Example usage
    test_seq = "ATGCTAGCTAGCTAGCTAGCGGCTAGCTAGCTAGCTAGCTAGC"
    try:
        results = predict_dna(test_seq)
        print(f"Results for sequence: {test_seq[:20]}...")
        print(f"GenetiForest Result: {results['classification']}")
        print(f"ViralBoost Result: {results['virus_identity']}")
    except Exception as e:
        print(f"Error: {e}")
        print("Ensure all .joblib files are in the same directory.")
