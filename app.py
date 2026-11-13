from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from PIL import Image, ImageDraw
import io
import base64

app = Flask(__name__)
CORS(app) 

# APNI IMGBB API KEY YAHAN DALO
IMGBB_API_KEY = "112b0fd84e8484db2959664024bb2014"

@app.route('/')
def home():
    return "GrowWick Premium GIF Engine v2 (Sliced) is LIVE!"

@app.route('/make-gif', methods=['POST'])
def make_gif():
    try:
        data = request.json
        img_url = data.get('baseImg')
        
        if not img_url:
            return jsonify({"error": "Photo ka link nahi mila"}), 400

        # 1. Photo Download & Resize
        resp = requests.get(img_url)
        original = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        original = original.resize((150, 150))
        
        # 2. Teen Diagonal Slices (Cuts) ke Masks Banao
        m1 = Image.new('L', (150,150), 0)
        ImageDraw.Draw(m1).polygon([(0,0), (60,0), (20,150), (0,150)], fill=255)
        
        m2 = Image.new('L', (150,150), 0)
        ImageDraw.Draw(m2).polygon([(60,0), (110,0), (70,150), (20,150)], fill=255)
        
        m3 = Image.new('L', (150,150), 0)
        ImageDraw.Draw(m3).polygon([(110,0), (150,0), (150,150), (70,150)], fill=255)
        
        # Slices ko original image se kaato
        s1 = Image.new('RGBA', (150,150), (0,0,0,0))
        s1.paste(original, mask=m1)
        
        s2 = Image.new('RGBA', (150,150), (0,0,0,0))
        s2.paste(original, mask=m2)
        
        s3 = Image.new('RGBA', (150,150), (0,0,0,0))
        s3.paste(original, mask=m3)
        
        frames = []
        
        # ANIMATION 1: Slices Niche Se Slide Hokar Aayenge (Staggered)
        for i in range(15, -1, -1):
            bg = Image.new('RGBA', (150, 150), (0,0,0,0))
            bg.paste(s1, (0, int(i*1.5)), s1)  # Pehla hissa fast
            bg.paste(s2, (0, int(i*3.0)), s2)  # Dusra hissa medium
            bg.paste(s3, (0, int(i*4.5)), s3)  # Teesra hissa slow
            frames.append(bg)
            
        # Judne ke baad thoda pause
        for _ in range(5):
            frames.append(original.copy())
            
        # ANIMATION 2: The Premium Shine
        width, height = original.size
        for i in range(-width, width*2, 20):
            frame = original.copy()
            draw = ImageDraw.Draw(frame, 'RGBA')
            draw.polygon([(i, 0), (i+40, 0), (i-20, height), (i-60, height)], fill=(255, 255, 255, 120))
            frames.append(frame)
            
        # Loop ke aakhir me pause
        for _ in range(10):
            frames.append(original.copy())
            
        # 3. GIF Save Karo
        gif_io = io.BytesIO()
        frames[0].save(gif_io, format='GIF', save_all=True, append_images=frames[1:], duration=50, loop=0)
        gif_io.seek(0)
        
        # 4. ImgBB par Upload
        b64_img = base64.b64encode(gif_io.read()).decode('utf-8')
        imgbb_resp = requests.post(
            f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}",
            data={"image": b64_img}
        ).json()
        
        if imgbb_resp.get("success"):
            return jsonify({"final_url": imgbb_resp["data"]["url"]})
        else:
            return jsonify({"error": "ImgBB upload fail ho gaya"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
