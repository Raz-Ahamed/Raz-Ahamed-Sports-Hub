from flask import Flask, request, Response, render_template, jsonify
from flask_cors import CORS
import requests
import urllib.parse

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

# আপনার আসল ডেটাবেস এখন সম্পূর্ণ ব্যাকএন্ডে লুকানো থাকবে
SECURE_CHANNELS = {
    1: { "name": "Caze TV", "logo": "https://images.seeklogo.com/logo-png/61/1/cazetv-logo-png_seeklogo-619708.png", "category": "Sports", "url": "https://dfr80qz435crc.cloudfront.net/MNOP/Amagi/Caze/Caze_TV_BR/1080p-vtt/index.m3u8" },
    2: { "name": "T Sports", "logo": "https://s3.aynaott.com/storage/dbc585f70a60b9855b6e13a8ce4cb6f4", "category": "Sports", "url": "http://rgkkw.live:80/live/1Aoen7elp5/IgMJ60tmAa/130714.ts" },
    3: { "name": "PTV Sports", "logo": "https://via.placeholder.com/45x45?text=PTV", "category": "Sports", "url": "https://tvsen5.aynaott.com/PtvSports/index.m3u8" },
    4: { "name": "T Sports 2", "logo": "https://i.imgur.com/2JzlorD.png", "category": "Sports", "url": "http://103.59.176.72:8083/live1/tracks-v1a1/mono.m3u8?token=123" },
    5: { "name": "Bein Sports 1", "logo": "https://via.placeholder.com/45x45?text=Bein+1", "category": "Sports", "url": "https://1nyaler.streamhostingcdn.top/stream/23/index.m3u8" },
    6: { "name": "WIN Sports", "logo": "https://via.placeholder.com/45x45?text=WIN", "category": "Sports", "url": "https://1nyaler.streamhostingcdn.top/stream/32/index.m3u8" }
}

@app.route('/')
def home():
    return render_template('index.html')

# ফ্রন্টএন্ডে চ্যানেলের লিস্ট পাঠানোর API (কিন্তু আসল URL ছাড়া)
@app.route('/api/get_channels')
def get_channels():
    safe_data = []
    for ch_id, ch_data in SECURE_CHANNELS.items():
        safe_data.append({
            "id": ch_id,
            "name": ch_data["name"],
            "logo": ch_data["logo"],
            "category": ch_data["category"]
            # খেয়াল করুন: আসল url ফ্রন্টএন্ডে পাঠানো হচ্ছে না!
        })
    return jsonify(safe_data)

@app.route('/proxy')
def proxy_playlist():
    # ফ্রন্টএন্ড এখন আর URL পাঠাবে না, পাঠাবে শুধু ID
    channel_id = request.args.get('id', type=int)
    
    if channel_id not in SECURE_CHANNELS:
        return "Error: Channel not found", 404

    target_url = SECURE_CHANNELS[channel_id]["url"]

    try:
        response = requests.get(target_url, headers=HEADERS)
        content = response.text
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                absolute_url = urllib.parse.urljoin(target_url, line)
                proxied_url = f"/ts?url={urllib.parse.quote(absolute_url)}"
                new_lines.append(proxied_url)
            else:
                new_lines.append(line)

        modified_content = '\n'.join(new_lines)
        return Response(modified_content, content_type='application/vnd.apple.mpegurl')

    except Exception as e:
        return str(e), 500

@app.route('/ts')
def proxy_video_chunk():
    target_url = request.args.get('url')
    if not target_url:
        return "Error: Chunk URL missing", 400
    try:
        req = requests.get(target_url, headers=HEADERS, stream=True)
        return Response(
            req.iter_content(chunk_size=1024*1024), 
            content_type=req.headers.get('Content-Type', 'video/MP2T')
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
