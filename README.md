# SnapDoc AI: On-Device Document Intelligence for Snapdragon PCs

SnapDoc AI is a fully autonomous, offline-first Retrieval-Augmented Generation (RAG) assistant purpose-built to harness the Qualcomm Hexagon NPU on Snapdragon-powered HP PCs (Windows on ARM).

## Key Features
- **100% On-Device Privacy:** Documents, embeddings, and chat interactions remain entirely local.
- **Hardware Acceleration:** Leverages ONNX Runtime with Qualcomm Neural Network (QNN) Execution Provider for optimal NPU inference.
- **Energy-Efficient Execution:** Offloads heavy matrix operations to the Hexagon NPU, minimizing CPU load and preserving battery life.
- **Multi-Format Ingestion:** Instant semantic querying across local PDFs, codebases, and text files.

## Technical Architecture
- **Language Model:** Pre-optimized Small Language Model (SLM) sourced from Qualcomm AI Hub (`Phi-3.5-mini` / `Llama-3.2-3B`).
- **Inference Engine:** ONNX Runtime (QNN EP) on Windows on ARM64.
- **Vector Retrieval:** Local FAISS / ChromaDB indexing.
- **Application Core:** Python & Flask lightweight server.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/SnapDoc-AI.git](https://github.com/your-username/SnapDoc-AI.git)
   cd SnapDoc-AI

Install dependencies

pip install -r requirements.txt

Run the local service:

python app.py
Open your browser and navigate to http://localhost:5000.
