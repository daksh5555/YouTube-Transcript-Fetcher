from flask import Flask, request, jsonify, render_template_string
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from youtube_transcript_api.proxies import WebshareProxyConfig
import os

app = Flask(__name__)

# Configure proxy if credentials are available
WEBSHARE_USERNAME = os.getenv('WEBSHARE_USERNAME')
WEBSHARE_PASSWORD = os.getenv('WEBSHARE_PASSWORD')

def get_youtube_api():
    """Get YouTubeTranscriptApi instance with or without proxy"""
    if WEBSHARE_USERNAME and WEBSHARE_PASSWORD:
        print("Using Webshare proxy configuration")
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=WEBSHARE_USERNAME,
                proxy_password=WEBSHARE_PASSWORD,
            )
        )
    else:
        print("No proxy configured - may encounter IP blocks")
        return YouTubeTranscriptApi()

# HTML template for the home page
HOME_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Transcript Fetcher</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 40px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .transcript-text {
            background: white;
            padding: 15px;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
            line-height: 1.6;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        .error.show {
            display: block;
        }
        .api-docs {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
        }
        .endpoint {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 10px 0;
            word-break: break-all;
        }
        code {
            background: #e0e0e0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        .lang-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .lang-item {
            background: white;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 YouTube Transcript Fetcher</h1>
        <p class="subtitle">Get transcripts from any YouTube video in multiple languages</p>
        
        <div class="section">
            <h2 style="color: #667eea; margin-bottom: 15px;">📋 Get Transcript</h2>
            <div class="input-group">
                <label for="videoInput">YouTube Video ID:</label>
                <input type="text" id="videoInput" placeholder="e.g., dQw4w9WgXcQ">
            </div>
            
            <div class="input-group">
                <label for="langSelect">Language (optional):</label>
                <select id="langSelect">
                    <option value="en">English (en)</option>
                    <option value="es">Spanish (es)</option>
                    <option value="fr">French (fr)</option>
                    <option value="de">German (de)</option>
                    <option value="hi">Hindi (hi)</option>
                    <option value="zh">Chinese (zh)</option>
                    <option value="ja">Japanese (ja)</option>
                    <option value="ko">Korean (ko)</option>
                    <option value="pt">Portuguese (pt)</option>
                    <option value="ru">Russian (ru)</option>
                </select>
            </div>
            
            <button onclick="checkLanguages()">🔍 Check Available Languages</button>
            <button onclick="fetchTranscript()">📥 Get Transcript</button>
            
            <div class="error" id="error"></div>
            
            <div class="result" id="langResult">
                <h3>Available Languages:</h3>
                <div class="lang-list" id="langList"></div>
            </div>
            
            <div class="result" id="result">
                <h3>Transcript:</h3>
                <div class="transcript-text" id="transcriptText"></div>
            </div>
        </div>
        
        <div class="api-docs">
            <h3>📚 API Documentation</h3>
            
            <p><strong>1. Get Available Languages:</strong></p>
            <div class="endpoint">GET /languages?video_id=VIDEO_ID</div>
            
            <p style="margin-top: 15px;"><strong>2. Get Transcript:</strong></p>
            <div class="endpoint">GET /transcript?video_id=VIDEO_ID&lang=en</div>
            
            <p style="margin-top: 15px;"><strong>Parameters:</strong></p>
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li><code>video_id</code> (required): YouTube video ID (11 characters)</li>
                <li><code>lang</code> (optional): Language code (default: en)</li>
            </ul>
            
            <p style="margin-top: 15px;"><strong>Example:</strong></p>
            <div class="endpoint">/transcript?video_id=dQw4w9WgXcQ&lang=en</div>
        </div>
    </div>
    
    <script>
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.classList.add('show');
            document.getElementById('result').classList.remove('show');
            document.getElementById('langResult').classList.remove('show');
        }
        
        function hideError() {
            document.getElementById('error').classList.remove('show');
        }
        
        async function checkLanguages() {
            const videoId = document.getElementById('videoInput').value.trim();
            const langResult = document.getElementById('langResult');
            const langList = document.getElementById('langList');
            
            hideError();
            document.getElementById('result').classList.remove('show');
            
            if (!videoId) {
                showError('Please enter a YouTube video ID');
                return;
            }
            
            try {
                const response = await fetch(`/languages?video_id=${videoId}`);
                const data = await response.json();
                
                if (response.ok) {
                    langList.innerHTML = '';
                    data.languages.forEach(lang => {
                        const div = document.createElement('div');
                        div.className = 'lang-item';
                        div.innerHTML = `<strong>${lang.code}</strong><br>${lang.name}`;
                        langList.appendChild(div);
                    });
                    langResult.classList.add('show');
                } else {
                    showError(data.error || 'Failed to fetch languages');
                }
            } catch (error) {
                showError('Error: ' + error.message);
            }
        }
        
        async function fetchTranscript() {
            const videoId = document.getElementById('videoInput').value.trim();
            const lang = document.getElementById('langSelect').value;
            const resultDiv = document.getElementById('result');
            const transcriptText = document.getElementById('transcriptText');
            
            hideError();
            document.getElementById('langResult').classList.remove('show');
            
            if (!videoId) {
                showError('Please enter a YouTube video ID');
                return;
            }
            
            try {
                const response = await fetch(`/transcript?video_id=${videoId}&lang=${lang}`);
                const data = await response.json();
                
                if (response.ok) {
                    transcriptText.textContent = data.transcript;
                    resultDiv.classList.add('show');
                } else {
                    showError(data.error || 'Failed to fetch transcript');
                }
            } catch (error) {
                showError('Error: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

# 🏠 Home Route
@app.route("/")
def home():
    """Home page with web interface"""
    return render_template_string(HOME_PAGE)

# 📼 Transcript Language Options
@app.route("/languages", methods=["GET"])
def get_available_languages():
    video_id = request.args.get("video_id")
    
    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400
    
    try:
        print(f"Fetching languages for video_id: {video_id}")
        
        # Create API instance and list transcripts
        ytt_api = get_youtube_api()
        transcript_list = ytt_api.list(video_id)
        
        languages = []
        for transcript in transcript_list:
            languages.append({
                "code": transcript.language_code,
                "name": transcript.language
            })
        
        return jsonify({
            "video_id": video_id,
            "languages": languages
        }), 200
        
    except Exception as e:
        print(f"Error fetching languages: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 📼 Transcript Fetcher
@app.route("/transcript", methods=["GET"])
def get_transcript():
    video_id = request.args.get("video_id")
    lang = request.args.get("lang", "en")
    
    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400
    
    try:
        print(f"Fetching transcript for video_id: {video_id}, language: {lang}")
        
        # Create API instance and fetch transcript
        ytt_api = get_youtube_api()
        fetched_transcript = ytt_api.fetch(video_id, languages=[lang])
        
        # Combine all text entries
        text = " ".join([snippet.text for snippet in fetched_transcript])
        
        return jsonify({
            "video_id": video_id,
            "language": lang,
            "transcript": text,
            "total_segments": len(fetched_transcript)
        }), 200
        
    except NoTranscriptFound:
        return jsonify({
            "error": f"No transcript found for video '{video_id}' in language '{lang}'"
        }), 404
        
    except TranscriptsDisabled:
        return jsonify({
            "error": f"Transcripts are disabled for video '{video_id}'"
        }), 403
        
    except VideoUnavailable:
        return jsonify({
            "error": f"Video '{video_id}' is unavailable"
        }), 404
        
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
