# DNA_G_OS (v9.0 Core)

## 1. Project Overview

**System Name**: DNA_G_OS (Viral Genome Collection & Analysis Console)
**Objective**: To automatically collect real viral genetic data from global databases (NCBI), analyze their sequence patterns using Machine Learning, and classify them based on specific genetic motifs.

---

## 2. Data Collection Analysis (The "Input")

This system is not generating random numbers; it is harvesting legitimate biological data from the **NCBI Nucleotide Database** (National Center for Biotechnology Information).

### Target Data Specifications

The system is currently configured to collect **Viral Genomes** with the following strict bio-filters:

| Parameter | DNA Configuration | RNA Configuration |
| :--- | :--- | :--- |
| **Organism** | `Viruses` (All viral families) | `Viruses` (All viral families) |
| **Molecule Type** | `biomol_genomic` (Genomic DNA) | `biomol_mrna` (Messenger RNA) |
| **Sequence Length** | `200` to `1000` base pairs | `200` to `1000` base pairs |

**Implication**:
The system is building a repository of short, functional viral segments. These lengths (200-1000bp) are typical for specific viral genes or partial genome fragments often used for identification.

---

## 3. Machine Learning & Embedding Logic

### What does "Embedding" mean here?

In this project, "Embedding" refers to **K-mer Frequency Vectorization** (specifically 3-grams).

1. **Raw Input**: `AGCTGCGCTA...` (Biological Sequence)
2. **Tokenization**: The system breaks the sequence into overlapping 3-letter words (codons/motifs).
   * Example: `AGC`, `GCT`, `CTG`, `TGC`...
3. **Vectorization**: It counts how many times every possible 3-letter combination appears.
   * This converts a biological string into a **mathematical vector** that a computer can understand.
   * *Analogy*: Like analyzing a book by counting how many times "the", "and", or "cat" appears to guess the genre.

### Current Classification Logic

The AI model (`RandomForestClassifier`) is currently trained to detect **"GCG-Rich" Signatures**:

* **Type A (High Density)**: Sequences containing the `GCG` pattern **5 times or more**.
  * *Biological Analogy*: High GC-content regions, often associated with stable gene structures or specific viral classes (like Herpesviruses).
* **Type B (Low Density)**: Sequences with fewer `GCG` patterns.
  * *Biological Analogy*: AT-rich regions, typical of other viral types (like some Flaviviruses or intergenic regions).

> **Real-world Application**: This logic simulates finding "CpG Islands" or specific binding sites in a genome.

---

## 4. System Capabilities & Utility

### What can you do with this system?

1. **Viral Surveillance**: Automatically monitor and download new viral submissions from NCBI that match criteria.
2. **Pattern Discovery**: The "Feature Sensitivity Analytics" panel shows which specific 3-base patterns (e.g., `AAA`, `GCG`) are most important for distinguishing the collected viruses.
3. **Anomaly Detection**: By retraining the model on the collected data, the system learns the "normal" pattern of the current dataset. Any future sequence that deviates significantly could be flagged as a novel variant.

### Technical Architecture

* **Core**: Python 3.9 + Flask
* **Data Source**: NCBI E-utilities (E-search, E-fetch) via REST API
* **Database**: SQLite (Local fast storage for collected sequences)
* **AI Engine**: Scikit-Learn (Random Forest + CountVectorizer)
* **Interface**: React + Vite (Cyberpunk Dashboard)

---

## 5. Summary

You are currently running a **real-time viral bio-surveillance terminal**. It pulls actual genetic code from the US National Library of Medicine, dissolves it into mathematical vectors based on 3-base patterns, and classifies them based on their GCG-motif density to simulate identifying distinct viral signatures.
