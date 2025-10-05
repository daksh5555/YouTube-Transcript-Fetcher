from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable

app = Flask(__name__)

# 📼 Transcript Language Options
@app.route("/languages", methods=["GET"])
def get_available_languages():
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400

    try:
        transcript_info = YouTubeTranscriptApi.list(video_id)
        languages = [
            {"code": t.language_code, "name": t.language}
            for t in transcript_info
        ]
        return jsonify({"video_id": video_id, "languages": languages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📼 Transcript Fetcher
@app.route("/transcript", methods=["GET"])
def get_transcript():
    video_id = request.args.get("video_id")
    lang = request.args.get("lang", "en")

    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400

    try:
        transcript_list = YouTubeTranscriptApi.fetch(video_id, languages=[lang])
        text = " ".join([entry.text for entry in transcript_list])
        return jsonify({
            "video_id": video_id,
            "language": lang,
            "transcript": text
        }), 200
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        return jsonify({"error": f"Transcript not available for video '{video_id}' in language '{lang}'"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
