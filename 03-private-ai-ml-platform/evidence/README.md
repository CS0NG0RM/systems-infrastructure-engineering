# Engineering Evidence & Technical Verification

This page documents observed engineering results from the **Private AI & Machine Learning Platform**, including local document intelligence, retrieval security, synthetic machine-learning evaluation, neural-network inference, and auditable agent workflows.

All examples use fictional enterprise data and locally controlled components. Screenshots come from different development milestones, not a single final execution.

## Verification Summary

| Component | Automated tests passed | Failures |
|---|---:|---:|
| Private RAG | 94 | 0 |
| Machine Learning | 32 | 0 |
| Agent Platform | 134 | 0 |
| **Total** | **260** | **0** |

The three final regression suites were run independently. Older test screenshots below show intermediate or overlapping subsets; **do not add their counts to 260**.

## 1. Private RAG and Document Intelligence

### 1.1 Document-grounded web application

The locally operated interface answers an authorized IT policy question and identifies the supporting fictional document.

<img width="1920" height="1038" alt="document_grounded_ai_web_interface" src="https://github.com/user-attachments/assets/94e570ec-10dd-4abf-8df8-8d3ee0fcd9af" />

*Figure 1. Authorized RAG response with source attribution to fictional IT document IT-001.*

### 1.2 Paraphrased-question retrieval

A differently phrased backup-restoration question produced an answer supported by a specific retrieved IT document chunk.

<img width="1534" height="835" alt="Paraphrased backup question" src="https://github.com/user-attachments/assets/03a11431-3d17-443c-b91a-1d2526a4b131" />

*Figure 2. Paraphrased request answered with a citation to IT-001-C0001.*

### 1.3 SQL-scoped vector retrieval

The locally persisted vector-retrieval process uses document-scoped constraints, supporting the separation of authorized and unauthorized document records.

<img width="1567" height="690" alt="P03-RAG-SQL-Scoped-Real-Vector-Retrieval" src="https://github.com/user-attachments/assets/101e4690-42ba-4fc2-9d64-1f1eff8a4edd" />

*Figure 3. Development evidence of document-scoped retrieval from the local vector index.*

### 1.4 Real document-ID validation

Five cases validated authorized IT, Finance, and HR retrieval, as well as forbidden-document and mixed-permission scenarios. The screenshot shows returned document identifiers, passage counts, and hybrid scores.

<img width="1920" height="1040" alt="P03-RAG-Document-ID-Real-Vector-Retrieval-Validation" src="https://github.com/user-attachments/assets/df96c1a3-36b3-4b10-88dc-c3afadc2a7b9" />

*Figure 4. Five of five document-ID retrieval scenarios passed using the local index.*

### 1.5 Atomic and incremental indexing

The observed unchanged-document indexing run reused all six existing embeddings, generated no new embeddings, and completed the document transaction.

<img width="872" height="975" alt="P03-RAG-Atomic-Incremental-Indexing-Pipeline" src="https://github.com/user-attachments/assets/e9df193c-370b-47d2-9058-8f293b63c843" />

![Atomic document indexing with embedding reuse](atomic-indexing.png)

*Figure 5. Atomic indexing and persistent vector-index inspection.*

| Observed indexing property | Result |
|---|---:|
| Documents | 3 |
| Chunks | 6 |
| Existing embeddings reused | 6 |
| New embeddings generated | 0 |
| Embedding dimensions | 768 |
| Embedding reuse rate | 100% |
| Document transaction | Committed |

These are results from the pictured run, not a general speed or scalability benchmark.

## 2. Retrieval Security and API Regression

### 2.1 Unauthorized Finance retrieval

A fixed IT Analyst demonstration identity was restricted to the fictional IT document. A Finance-related question did not produce an answer from unauthorized Finance content. The fixed demonstration identity is **not a production authentication mechanism**.

<img width="1919" height="1038" alt="P03-RAG-Refactored-Live-Unauthorized-Retrieval" src="https://github.com/user-attachments/assets/97728b94-df32-4109-982e-502d2e1320c8" />

*Figure 6. Observed access-boundary behavior for one unauthorized Finance query.*

### 2.2 Hybrid-retrieval regression

The pictured regression checkpoint covers hybrid ranking, authorization-related cases, input validation, and retrieval behavior.

<img width="1434" height="410" alt="P03-RAG-Hybrid-Retrieval-Regression-52-Passed" src="https://github.com/user-attachments/assets/e157fceb-9365-4a18-9291-514d31a9f201" />

*Figure 7. Intermediate RAG regression run: 52 tests passed.*

### 2.3 HTTP API integration

The API integration suite exercised successful and unsuccessful request paths, including malformed requests, unavailable retrieval and internal error handling. Expected HTTP error statuses in these tests do not mean the suite failed.

<img width="1920" height="1015" alt="P03-RAG-HTTP-API-Integration-31-Passed" src="https://github.com/user-attachments/assets/ded47e15-912f-43e8-b7dc-b36ec775a288" />

*Figure 8. Intermediate HTTP API integration run: 31 tests passed.*

## 3. Local Language-Model Inference

A local Qwen3 model was invoked through Ollama, returning generated content and performance counters without an external inference API.

<img width="1919" height="1040" alt="local_ai_python_api_inference" src="https://github.com/user-attachments/assets/807405a5-4b8c-4e04-8ef7-b8fbc4d3b742" />

*Figure 9. Example inference run with reported elapsed time and token-generation rate.*

The pictured run reports approximately 2.31 seconds elapsed and 89.89 tokens per second for 200 generated tokens. These are single-run observations, not performance guarantees.

## 4. Machine Learning and Neural-Network Engineering

### 4.1 Independent three-model benchmark

Isolation Forest, Random Forest, and an MLP neural network were compared using the same independent synthetic dataset containing 6,000 fictional transactions and 300 known synthetic anomalies.

<img width="1570" height="969" alt="ml-three-model-independent-benchmark" src="https://github.com/user-attachments/assets/ef6d6bef-f111-4a85-9fa5-d35e282ce040" />

*Figure 10. Controlled model comparison reporting precision, recall and F1 score.*

| Model | Precision | Recall | F1 score |
|---|---:|---:|---:|
| Isolation Forest | 0.588 | 0.580 | 0.584 |
| Random Forest | 0.917 | 0.807 | 0.858 |
| **Neural Network (MLP)** | **0.938** | **0.810** | **0.869** |

The neural network achieved the highest F1 score **in this benchmark**. These results do not establish effectiveness against real financial fraud.

### 4.2 Neural-network training and validation

The pictured MLP training run used 4,500 synthetic training records and 1,500 validation records. Its validation results are from a different run than the independent benchmark above.

<img width="1565" height="551" alt="neural network" src="https://github.com/user-attachments/assets/7877ec13-8191-46af-b6b9-2c4a81af6283" />

*Figure 11. Synthetic-data neural-network validation and confusion-matrix results.*

| Observed metric | Result |
|---|---:|
| Architecture | 64 → 32 → binary output |
| Training records | 4,500 |
| Validation records | 1,500 |
| Training iterations | 41 |
| Precision | 0.970 |
| Recall | 0.867 |
| F1 score | 0.915 |
| True positives | 65 |
| False positives | 2 |
| False negatives | 10 |
| True negatives | 1,423 |

The completed platform separately added model registration and SHA-256 integrity checks. The historical training screenshot alone does not demonstrate those later controls.

### 4.3 Registered neural-network inference

The agent platform subsequently executed the locally registered model against fictional transactions, with artifact-identity and SHA-256 checks in the inference workflow.

| Fictional transaction | Anomaly score | Classification |
|---|---:|---|
| TX-101 | 0.00064 | Normal |
| TX-102 | 1.00000 | Flagged |

The values are **model anomaly scores**, not calibrated probabilities of actual fraud. Hash verification detects mismatches against the expected local digest; it is not independent proof of the artifact's origin.

## 5. Agent Orchestration and Execution Auditing

### 5.1 Agent regression checkpoint

The agent platform's regression tests cover structured requests, role-based authorization, bounded workflow planning and execution, tool adapters, failure handling and persistence.

<img width="1564" height="1015" alt="72 tests" src="https://github.com/user-attachments/assets/ab06d5ae-f357-41e7-9d6d-98ef67b42dab" />

*Figure 12. Intermediate agent-platform checkpoint: 72 tests passed. The completed agent suite later reached 134 passing tests.*

### 5.2 Integrated risk-review demonstration

The demonstrated two-step workflow used **mocked, authorized fictional RAG retrieval** followed by **real registered local neural-network inference**. The result was written to SQLite and successfully recovered.

| Verification property | Observed outcome |
|---|---|
| Workflow steps | 2 |
| Retrieval integration | Mocked authorized RAG metadata |
| Prediction integration | Genuine registered local neural network |
| Execution records | 1 SQLite record |
| Persistence verification | Successful |

This combined demonstration **does not establish direct connection to the standalone live RAG backend**. No screenshot of the final combined execution is included in this gallery yet.

### 5.3 Security and reliability checks

Automated tests exercised request schema validation, rejection of duplicate JSON fields and oversized or invalid requests, role-based tool authorization, bounded plans, technical error classification, workflow stop conditions, and SQLite persistence.

Passing tests provide evidence of the exercised scenarios, not universal guarantees against security or reliability failures.

## 6. Final Regression Totals

| Test suite | Passed | Failed |
|---|---:|---:|
| RAG | 94 | 0 |
| Machine Learning | 32 | 0 |
| Agent Platform | 134 | 0 |
| **Total** | **260** | **0** |

The historical 31-, 52-, and 72-test screenshots are development checkpoints and may overlap with other test suites. They are **not additional tests beyond the final total**.

## 7. Evidence Scope and Limitations

- The evidence uses local components and fictional enterprise data.
- Images document different stages of the implementation, rather than a single final execution.
- The demonstrated web identity is fixed in server-side demonstration code, not authenticated.
- The combined agent workflow uses mocked RAG retrieval with real neural inference.
- The ML evaluation is synthetic and does not validate real-world fraud-detection performance.
- Inference timing is an observed local measurement, not a repeatable performance guarantee.
- Automated tests are not a production security certification.
- Complete private source modules, trained models and operational configuration are excluded from this public showcase.

## Further Documentation

- [Project 03 overview](../README.md)
- [System architecture](../architecture/system-architecture.md)
- [Selected engineering excerpts](../technical-excerpts/engineering-excerpts.md)

Full-source technical walkthroughs may be requested using the contact instructions on the [Project 03 overview](../README.md). Requests do not grant automatic access to the private repository.
