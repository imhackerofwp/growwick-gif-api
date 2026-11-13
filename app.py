from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from PIL import Image, ImageDraw
import io
import base64

app = Flask(__name__)
# Yeh line browser ke CORS error ko hamesha ke liye khatam kar degi
CORS(app) 

# APNI IMGBB API KEY YAHAN DALO
IMGBB_API_KEY = "112b0fd84e8484db2959664024bb2014"

@app.route('/')
def home():
    return "GrowWick Premium GIF Engine is LIVE!"

@app.route('/make-gif', methods=['POST'])
def make_gif():
    try:
        data = request.json
        img_url = data.get('baseImg')
        
        if not img_url:
            return jsonify({"error": "Photo ka link nahi mila"}), 400

        # 1. User ki Photo Download karo
        resp = requests.get(img_url)
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        
        # 2. Resize
        img = img.resize((150, 150))
        
        # 3. GIF Frames Banao (Shine Effect Animation)
        frames = []
        width, height = img.size
        # Yeh loop photo ke upar diagonal white shine animation lagayega
        for i in range(-width, width*2, 15):
            frame = img.copy()
            draw = ImageDraw.Draw(frame, 'RGBA')
            draw.polygon([(i, 0), (i+30, 0), (i-20, height), (i-50, height)], fill=(255, 255, 255, 90))
            frames.append(frame)
            
        # 4. Memory me .gif save karo
        gif_io = io.BytesIO()
        frames[0].save(gif_io, format='GIF', save_all=True, append_images=frames[1:], duration=60, loop=0)
        gif_io.seek(0)
        
        # 5. ImgBB par upload karke public link lo
        b64_img = base64.b64encode(gif_io.read()).decode('utf-8')
        imgbb_resp = requests.post(
            f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}",
            data={"image": b64_img}
        ).json()
        
        if imgbb_resp.get("success"):
            final_link = imgbb_resp["data"]["url"]
            return jsonify({"final_url": final_link})
        else:
            return jsonify({"error": "ImgBB upload fail ho gaya"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
