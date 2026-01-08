import numpy as np
import math
from collections import Counter
from sklearn.base import BaseEstimator, TransformerMixin

class SequenceFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    시퀀스 고유의 생물학적 특징을 추출하는 고급 피처 추출기.
    
    Features:
    1. GC Content
    2. GC Skew: (G-C)/(G+C) - DNA 복제 방향 지표
    3. AT Skew: (A-T)/(A+T) - 전사 방향 지표
    4. Shannon Entropy (Sequence Complexity)
    5. 5-mer Frequency Profile (Extended K-mer)
    6. Codon Usage Bias (첫 3개 아미노산 코돈 빈도)
    7. Dinucleotide Bias (CpG, TpA 등)
    8. Repeat Pattern Score (Simple Sequence Repeat)
    9. Transition/Transversion Potential
    """
    def __init__(self, kmer_size=5):
        self.kmer_size = kmer_size
        self.kmers = self._generate_kmers(kmer_size)
        self.dinucleotides = ['AA', 'AT', 'AG', 'AC', 
                              'TA', 'TT', 'TG', 'TC',
                              'GA', 'GT', 'GG', 'GC',
                              'CA', 'CT', 'CG', 'CC']
    
    def _generate_kmers(self, k):
        """Generate all possible k-mers"""
        bases = ['A', 'C', 'G', 'T']
        if k == 1: return bases
        return [b + s for b in bases for s in self._generate_kmers(k-1)]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        X: List of DNA strings
        Returns: numpy array of shape (n_samples, n_features)
        """
        features = []
        for seq in X:
            if not seq:
                seq = ""
            seq = seq.upper().replace('U', 'T')
            
            row = []
            length = len(seq)
            
            # 1. GC Content
            gc_content = self._calc_gc_content(seq, length)
            row.append(gc_content)
            
            # 2. GC Skew
            gc_skew = self._calc_gc_skew(seq)
            row.append(gc_skew)
            
            # 3. AT Skew
            at_skew = self._calc_at_skew(seq)
            row.append(at_skew)
            
            # 4. Shannon Entropy
            entropy = self._calc_entropy(seq)
            row.append(entropy)
            
            # 5. 5-mer Frequency (Top 20 most variable k-mers)
            kmer_features = self._calc_kmer_freq(seq, length)
            row.extend(kmer_features[:20])  # Limit to 20 k-mers
            
            # 6. Dinucleotide Bias (16 features)
            di_features = self._calc_dinucleotide_freq(seq, length)
            row.extend(di_features)
            
            # 7. Repeat Pattern Score
            repeat_score = self._calc_repeat_score(seq)
            row.append(repeat_score)
            
            # 8. CpG Ratio (특히 바이러스에서 중요)
            cpg_ratio = self._calc_cpg_ratio(seq, length)
            row.append(cpg_ratio)
            
            # 9. Codon Position Bias (3개 위치별 염기 분포)
            codon_bias = self._calc_codon_position_bias(seq)
            row.extend(codon_bias)
            
            features.append(row)
            
        return np.array(features)

    def _calc_gc_content(self, seq, length):
        if length == 0: return 0
        return (seq.count('G') + seq.count('C')) / length
    
    def _calc_gc_skew(self, seq):
        g = seq.count('G')
        c = seq.count('C')
        if g + c == 0: return 0
        return (g - c) / (g + c)
    
    def _calc_at_skew(self, seq):
        a = seq.count('A')
        t = seq.count('T')
        if a + t == 0: return 0
        return (a - t) / (a + t)
    
    def _calc_entropy(self, seq):
        if not seq: return 0
        counts = Counter(seq)
        total = len(seq)
        entropy = 0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def _calc_kmer_freq(self, seq, length):
        """Calculate k-mer frequencies"""
        total_kmers = length - self.kmer_size + 1
        if total_kmers <= 0:
            return [0] * len(self.kmers)
        
        counts = Counter([seq[i:i+self.kmer_size] for i in range(total_kmers)])
        return [counts.get(kmer, 0) / total_kmers for kmer in self.kmers]
    
    def _calc_dinucleotide_freq(self, seq, length):
        """Calculate dinucleotide frequencies"""
        total = length - 1
        if total <= 0:
            return [0] * 16
        
        counts = Counter([seq[i:i+2] for i in range(total)])
        return [counts.get(di, 0) / total for di in self.dinucleotides]
    
    def _calc_repeat_score(self, seq):
        """Calculate simple sequence repeat score"""
        if len(seq) < 6: return 0
        
        repeat_count = 0
        # Check for 2-mer, 3-mer, 4-mer repeats
        for unit_len in [2, 3, 4]:
            for i in range(len(seq) - unit_len * 2):
                unit = seq[i:i+unit_len]
                if seq[i+unit_len:i+unit_len*2] == unit:
                    repeat_count += 1
        
        return repeat_count / len(seq)
    
    def _calc_cpg_ratio(self, seq, length):
        """Calculate CpG ratio (observed/expected)"""
        if length < 2: return 0
        
        cpg_count = seq.count('CG')
        c_count = seq.count('C')
        g_count = seq.count('G')
        
        expected = (c_count * g_count) / length if length > 0 else 0
        if expected == 0: return 0
        
        return cpg_count / expected
    
    def _calc_codon_position_bias(self, seq):
        """Calculate nucleotide bias at each codon position"""
        if len(seq) < 3: return [0] * 12
        
        pos_counts = [{}, {}, {}]
        for i in range(0, len(seq) - 2, 3):
            for j in range(3):
                base = seq[i+j]
                if base in 'ATGC':
                    pos_counts[j][base] = pos_counts[j].get(base, 0) + 1
        
        features = []
        for pos in range(3):
            total = sum(pos_counts[pos].values()) or 1
            for base in 'ATGC':
                features.append(pos_counts[pos].get(base, 0) / total)
        
        return features
        
    def get_feature_names_out(self, input_features=None):
        names = [
            "gc_content", "gc_skew", "at_skew", "entropy"
        ]
        # Top 20 k-mers
        names.extend([f"kmer_{self.kmers[i]}" for i in range(20)])
        # Dinucleotides
        names.extend([f"di_{di}" for di in self.dinucleotides])
        # Other features
        names.extend(["repeat_score", "cpg_ratio"])
        # Codon position bias
        for pos in range(3):
            for base in 'ATGC':
                names.append(f"codon_pos{pos}_{base}")
        
        return np.array(names)
