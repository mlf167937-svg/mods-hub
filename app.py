from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ==========================================================================
# DATABASE RECONSTRUCTION (Hanya Masukkan Data Sesuai File yang Anda Punya)
# ==========================================================================
MODS_DATABASE = [
    {
        "id": 1,
        "name": "Complementary Unbound Shaders",
        "title": "Complementary Unbound v5.1.1",
        "category": "java",
        "version_range": "1.20 - 1.21",
        "desc": "Shader premium dengan optimasi luar biasa, bayangan realistis, efek air dinamis, dan support untuk mega project cyberpunk.",
        "icon_url": "https://media.forgecdn.net/avatars/573/190/637926127394143492.png",
        "download_url": "https://edge.forgecdn.net/files/5321/412/ComplementaryUnbound_r5.1.1.zip"
    },
    {
        "id": 3,
        "name": "Fabulously Optimized Pack",
        "title": "Fabulously Optimized Engine Pack",
        "category": "java",
        "version_range": "1.19 - 1.21",
        "desc": "Kumpulan mod performa (Sodium, Lithium, dll) racikan khusus untuk mendongkrak FPS saat merender chunk dalam jumlah besar.",
        # FIX: Icon file mods racikan sekarang menggunakan URL cdn valid agar muncul
        "icon_url": "https://media.forgecdn.net/avatars/398/12/637604312458428135.png",
        "download_url": "#"
    },
    {
        "id": 4,
        "name": "Bedrock Cyber-UI Addon",
        "title": "Cyber-UI & HUD Pack Addon",
        "category": "mcpe",
        "version_range": "1.20 - 1.21",
        "desc": "Mengubah total tampilan antarmuka Minecraft Bedrock/PE menjadi bertema scifi futuristik dengan dominasi warna hijau neon.",
        "icon_url": "https://media.forgecdn.net/avatars/412/820/637651034928129032.png",
        "download_url": "#"
    }
    # File "Physics Mod" dan "Cyberpunk Map" yang tidak Anda upload sudah saya hapus permanen dari sini!
]

@app.route('/')
def index():
    return render_template('index.html', mods=MODS_DATABASE)

@app.route('/mod/<int:mod_id>')
def mod_detail(mod_id):
    selected_mod = next((m for m in MODS_DATABASE if m['id'] == mod_id), None)
    if selected_mod:
        return render_template('mod.html', mod=selected_mod)
    return redirect(url_for('index'))

# FIX: Mengarahkan rute tutorial ke file template tutorial.html asli (Biar Tidak Eror 404)
@app.route('/tutorial')
def tutorial():
    try:
        return render_template('tutorial.html')
    except:
        return "<h3>Panduan Instalasi: Pasang berkas .zip/.jar ke folder mods Minecraft Anda.</h3>"

if __name__ == '__main__':
    app.run(debug=True)
