# =========================================================================
# REXCRAFT MODS HUB - CORE BACKEND ENGINE (FLASK MASTER)
# =========================================================================
from flask import Flask, render_template, abort

app = Flask(__name__)

# =========================================================================
# DATABASE REAL REXCRAFT (JAVA & MCPE BARE BONES INTEGRATION)
# =========================================================================
MODS_DATABASE = [
    {
        "id": 1,
        "category": "java",
        "name": "mod-racikan-bos",
        "title": "Mod Racikan Premium v1.0",
        "desc": "Berkas modifikasi hasil racikan kustom RexCraft Engine, dijamin super stabil, optimal, dan anti-lag.",
        "version_range": "1.20 - 1.21+",
        "icon_url": "/static/upload/java/mod_racikan/icon.png",
        "project_type": "Modpack / Optimization",
        # DAFTAR PILIHAN VERSI DOWNLOAD ALA MODRINTH
        "versions": [
            {
                "version_name": "Mod Racikan Release v1.0.2 (Stable)",
                "game_version": "1.21+",
                "file_size": "4.2 MB",
                "download_url": "/static/upload/java/mod_racikan/mod.zip"
            },
            {
                "version_name": "Mod Racikan Patch v1.0.1 (Legacy)",
                "game_version": "1.20.4",
                "file_size": "4.0 MB",
                "download_url": "/static/upload/java/mod_racikan/mod_old.zip"
            }
        ]
    },
    {
        "id": 2,
        "category": "mcpe",
        "name": "bare-bones-mcpe",
        "title": "Bare Bones Texture Pack (MCPE/Bedrock)",
        "desc": "Tekstur legendaris yang membawa visual Minecraft Anda menjadi sebersih dan sehalus cuplikan trailer resmi Mojang. Ringan, estetik, dan anti-lag!",
        "version_range": "1.19 - 1.21+",
        "icon_url": "/static/upload/java/mod_racikan/icon.png", # <--- Silakan sesuaikan jalur icon bare bones Bos kalau ada
        "project_type": "Texture Pack / Addon",
        # DAFTAR PILIHAN VERSI DOWNLOAD BARE BONES MCPE
        "versions": [
            {
                "version_name": "Bare Bones Bedrock Edition v1.21",
                "game_version": "1.21+",
                "file_size": "2.8 MB",
                "download_url": "/static/upload/java/mod_racikan/mod.zip" # <--- Arahkan ke file mcpack/zip bare bones 1.21 Bos
            },
            {
                "version_name": "Bare Bones Bedrock Edition v1.20",
                "game_version": "1.20",
                "file_size": "2.5 MB",
                "download_url": "/static/upload/java/mod_racikan/mod.zip" # <--- Arahkan ke file mcpack/zip bare bones 1.20 Bos
            }
        ]
    }
]

# =========================================================================
# ROUTING CONTROLLER
# =========================================================================
@app.route('/')
def home_dashboard():
    return render_template('index.html', mods=MODS_DATABASE)

@app.route('/mod/<int:mod_id>')
def mod_detail_page(mod_id):
    selected_mod = None
    for item in MODS_DATABASE:
        if item["id"] == mod_id:
            selected_mod = item
            break
            
    if selected_mod is None:
        abort(404)
        
    return render_template('mod.html', mod=selected_mod)

@app.route('/tutorial')
def tutorial_page():
    return render_template('tutorial.html')

@app.errorhandler(404)
def page_not_found(error):
    return "<h1>404 - Berkas Modifikasi Tidak Ditemukan!</h1><p>Kembali ke <a href='/'>Dashboard RexCraft</a></p>", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
