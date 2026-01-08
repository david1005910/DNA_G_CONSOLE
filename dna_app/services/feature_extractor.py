import numpy as np
import math
from collections import Counter
from sklearn.base import BaseEstimator, TransformerMixin

class BiologicalFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    DNA 서열로부터 생물학적으로 유의미한 수치형 특징들을 추출합니다.
    1. GC Content
    2. Sequence Entropy (Complexity)
    3. K-mer Frequencies (compositional bias)
    """
    def __init__(self, kmer_size=3):
        self.kmer_size = kmer_size
        self.kmers = self._generate_kmers(kmer_size)
    
    def _generate_kmers(self, k):
        """Generate all possible k-mers (e.g., AAA, AAT, ... GGG)"""
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
            # Normalize
            if not seq:
                seq = ""
            seq = seq.upper().replace('U', 'T') 
            
            row = []
            length = len(seq)
            
            # 1. GC Content
            if length > 0:
                gc_count = seq.count('G') + seq.count('C')
                gc_content = gc_count / length
            else:
                gc_content = 0
            row.append(gc_content)
            
            # 2. Shannon Entropy (Sequence Complexity)
            entropy = self._calculate_entropy(seq)
            row.append(entropy)
            
            # 3. K-mer Frequency Profile (Normalized)
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
        """Calculate Shannon entropy of the sequence per base"""
        if not seq: return 0
        counts = Counter(seq)
        total = len(seq)
        entropy = 0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy
        
    def get_feature_names_out(self, input_features=None):
        names = ["gc_content", "entropy"]
        names.extend([f"kmer_{k}" for k in self.kmers])
        return np.array(names)
