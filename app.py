# =========================================================================
# REXCRAFT MODS HUB - CORE BACKEND ENGINE (FLASK MASTER)
# =========================================================================
from flask import Flask, render_template, abort

app = Flask(__name__)

# =========================================================================
# DATABASE REPOSITORI MODS LOCAL (JAVA & MCPE BEDROCK INTEGRATION)
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
        "download_url": "/static/upload/java/mod_racikan/mod.zip",
        "file_size": "4.2 MB",
        "total_downloads": "1,240",
        "project_type": "Modpack / Optimization"
    },
    {
        "id": 2,
        "category": "mcpe",
        "name": "mod-bedrock-racikan",
        "title": "Addon MCPE Bedrock Racikan v1.0",
        "desc": "Addon kustom khusus Minecraft Bedrock / Pocket Edition. Tinggal pasang di Android/iOS/Windows 10, lancar jaya!",
        "version_range": "1.20 - 1.21+",
        # Jika Bos belum punya icon mcpe, arahkan ke folder yang sama dulu atau ganti nanti
        "icon_url": "/static/upload/java/mod_racikan/icon.png", 
        "download_url": "/static/upload/java/mod_racikan/mod.zip", # <--- Ganti jadi file .mcaddon / .zip MCPE Bos nanti
        "file_size": "2.8 MB",
        "total_downloads": "850",
        "project_type": "Addon / Resource Pack"
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
