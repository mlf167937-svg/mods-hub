import os
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'rexcraft_secret_hub_key_2026'

# DATA REPOSITORI MOD INTERNAL (Bisa ditambah sampai 100+ mod sesuai kebutuhan)
MODS_DATA = {
    "mods-racikan": {
        "id": "mods-racikan",
        "title": "Mods Racikan Java",
        "desc": "Kumpulan modifikasi penting resmi kustom RexCraft untuk meningkatkan performa, stabilitas FPS, dan optimasi engine sirkuit Minecraft JAVA Edition.",
        "category": "java",
        "loader": "FABRIC",
        "version_game": "1.21+",
        "icon_url": "/static/icon.png", 
        "base_downloads": 342,
        "files": [
            {"filename": "Mods_Racikan_v1.0-Java.zip", "size": "14.2 MB"},
            {"filename": "Optimasi_Engine_Core.jar", "size": "4.8 MB"}
        ]
    },
    "bare-bones": {
        "id": "bare-bones",
        "title": "Bare Bones Resource Pack",
        "desc": "Tekstur kustom Bare Bones resmi versi 1.26+ yang dikompresi khusus untuk kelancaran rendering visual Minecraft MCPE / Bedrock Edition.",
        "category": "mcpe",
        "loader": "MCPACK",
        "version_game": "1.26+",
        "icon_url": None,
        "base_downloads": 185,
        "files": [
            {"filename": "Bare_Bones_Visual_Fix.mcpack", "size": "8.1 MB"},
            {"filename": "Bare_Bones_World_Resource.mcaddon", "size": "12.4 MB"}
        ]
    }
}

@app.route('/')
def home():
    mods_list = []
    for mod_id, data in MODS_DATA.items():
        clicks = session.get(f"dl_{mod_id}", 0)
        likes = session.get(f"like_{mod_id}", 0)
        mod_item = data.copy()
        mod_item["downloads"] = data["base_downloads"] + clicks
        mod_item["likes"] = 48 + likes
        mods_list.append(mod_item)
    return render_template('index.html', mods=mods_list)

@app.route('/mod/<mod_id>')
def mod_detail(mod_id):
    if mod_id not in MODS_DATA:
        return "Mod Tidak Ditemukan", 404
    data = MODS_DATA[mod_id].copy()
    clicks = session.get(f"dl_{mod_id}", 0)
    likes = session.get(f"like_{mod_id}", 0)
    data["downloads"] = data["base_downloads"] + clicks
    data["likes"] = 48 + likes
    
    versions_payload = []
    for f in data["files"]:
        versions_payload.append({
            "filename": f["filename"],
            "size": f["size"],
            "download_url": f"/download_action/{mod_id}/{f['filename']}"
        })
    return render_template('mod.html', mod=data, versions=versions_payload)

@app.route('/download_action/<mod_id>/<filename>')
def download_action(mod_id, filename):
    if mod_id in MODS_DATA:
        session[f"dl_{mod_id}"] = session.get(f"dl_{mod_id}", 0) + 1
    # Trik melempar download langsung ke penyimpanan raw GitHub Anda
    github_raw_url = f"https://raw.githubusercontent.com/RexCraft6506/RexCraft-Hub/main/static/{filename}"
    return jsonify({"status": "redirect", "url": github_raw_url}), 200

@app.route('/like_action/<mod_id>', methods=['POST'])
def like_action(mod_id):
    if mod_id in MODS_DATA:
        session[f"like_{mod_id}"] = session.get(f"like_{mod_id}", 0) + 1
        return jsonify({"success": True, "new_likes": 48 + session[f"like_{mod_id}"]})
    return jsonify({"success": False}), 404

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/ai')
def ai_minecraft():
    return render_template('ai.html')

if __name__ == '__main__':
    app.run(debug=True)
