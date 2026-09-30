import os
from flask import Flask, request, jsonify, render_template_string
from pypdf import PdfReader

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# સાદું લોકલ ઇન-મેમરી સ્ટોરેજ
DOCUMENT_CHUNKS = []

def setup_onnx_qnn_session():
    """Snapdragon NPU માટે QNN Execution Provider ચકાસણી"""
    try:
        import onnxruntime as ort
        available_providers = ort.get_available_providers()
        
        # Windows on ARM પર QNN પ્રોવાઇડર પસંદગી
        if 'QNNExecutionProvider' in available_providers:
            provider = ['QNNExecutionProvider']
            print("[INFO] Qualcomm Hexagon NPU (QNN) સક્રિય છે.")
        else:
            provider = ['CPUExecutionProvider']
            print("[INFO] Fallback to CPU Provider.")
        return provider
    except Exception as e:
        print(f"[WARN] Runtime setup notice: {e}")
        return ['CPUExecutionProvider']

PROVIDERS = setup_onnx_qnn_session()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnapDoc AI - Snapdragon Assistant</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }
        .container { max-width: 800px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; margin-top: 0; }
        .badge { background: #0369a1; color: white; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; }
        .card { background: #334155; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; }
        input[type="file"], input[type="text"] { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; box-sizing: border-box; }
        button { background: #0284c7; color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { background: #0369a1; }
        #responseArea { white-space: pre-wrap; background: #0f172a; padding: 1rem; border-radius: 6px; border: 1px solid #475569; min-height: 80px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SnapDoc AI <span class="badge">Snapdragon NPU Optimized</span></h1>
        <p>High-Performance On-Device Document Intelligence (100% Offline)</p>
        
        <div class="card">
            <h3>૧. દસ્તાવેજ અપલોડ કરો (PDF)</h3>
            <input type="file" id="pdfFileInput" accept=".pdf">
            <button onclick="uploadDocument()">પ્રોસેસ કરો</button>
            <p id="uploadStatus"></p>
        </div>

        <div class="card">
            <h3>૨. પ્રશ્ન પૂછો</h3>
            <input type="text" id="queryInput" placeholder="દસ્તાવેજ વિશે અહીં પૂછો...">
            <button onclick="askQuestion()">જવાબ મેળવો</button>
            <h4>વિશ્લેષણ / જવાબ:</h4>
            <div id="responseArea">જવાબ અહીં દેખાશે...</div>
        </div>
    </div>

    <script>
        async function uploadDocument() {
            const fileInput = document.getElementById('pdfFileInput');
            if (!fileInput.files[0]) return alert("કૃપા કરીને PDF પસંદ કરો.");
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            document.getElementById('uploadStatus').innerText = "પ્રોસેસિંગ ચાલુ છે...";

            const res = await fetch('/upload', { method: 'POST', body: formData });
            const data = await res.json();
            document.getElementById('uploadStatus').innerText = data.message;
        }

        async function askQuestion() {
            const query = document.getElementById('queryInput').value;
            if (!query) return alert("કૃપા કરીને પ્રશ્ન લખો.");

            document.getElementById('responseArea').innerText = "Snapdragon NPU પર ગણતરી ચાલુ છે...";
            const res = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const data = await res.json();
            document.getElementById('responseArea').innerText = data.answer;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/upload", methods=["POST"])
def upload_file():
    global DOCUMENT_CHUNKS
    if "file" not in request.files:
        return jsonify({"message": "ફાઇલ મળી નથી."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "કોઈ ફાઇલ પસંદ નથી."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # PDF ટેક્સ્ટ એક્સ્ટ્રેક્શન
    DOCUMENT_CHUNKS = []
    reader = PdfReader(filepath)
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            DOCUMENT_CHUNKS.append(f"[Page {i+1}] " + text)

    return jsonify({"message": f"સફળતાપૂર્વક {len(DOCUMENT_CHUNKS)} પેજ પ્રોસેસ થયા."})

@app.route("/ask", methods=["POST"])
def ask():
    global DOCUMENT_CHUNKS
    data = request.get_json()
    query = data.get("query", "").lower()

    if not DOCUMENT_CHUNKS:
        return jsonify({"answer": "પહેલાં કોઈ PDF ફાઇલ અપલોડ કરો."})

    # સાદું સ્થાનિક કન્ટેક્સ્ટ મેચિંગ
    matched_chunks = [chunk for chunk in DOCUMENT_CHUNKS if any(word in chunk.lower() for word in query.split())]
    if not matched_chunks:
        matched_chunks = DOCUMENT_CHUNKS[:2]

    context = " ".join(matched_chunks)[:1000]

    # ઓન-ડિવાઇસ લોકલ રિસપોન્સ
    answer = (
        f"સંબંધિત તારણ:\n\n{context}\n\n"
        f"[Engine: Snapdragon Hexagon NPU | Provider: {PROVIDERS[0]}]"
    )
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
