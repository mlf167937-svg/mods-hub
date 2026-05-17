from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# DATA MOCK DATABASE UTAMA REXCRAFT ENGINE
# Menampung detail mod, kategori (java/mcpe), dan parameter filter
MODS_DATABASE = [
    {
        "id": 1,
        "name": "Complementary Unbound Shaders",
        "title": "Complementary Unbound v5.1.1",
        "category": "java",
        "version_range": "1.20 - 1.21",
        "desc": "Shader premium dengan optimasi luar biasa, bayangan realistis, efek air dinamis, dan support untuk mega project cyberpunk.",
        "icon_url": "https://media.forgecdn.net/avatars/573/190/637926127394143492.png",
        "download_url": "https://edge.forgecdn.net/files/5321/412/ComplementaryUnbound_r5.1.1.zip",
        "total_files": 3
    },
    {
        "id": 2,
        "name": "Cyberpunk Mega-City Map Pack",
        "title": "Cyberpunk City High-Rise v2.0",
        "category": "java",
        "version_range": "1.21",
        "desc": "Map perkotaan futuristik dengan susunan multi-tower megah mengelilingi core energi utama, dibangun menggunakan deepslate dan tuff.",
        "icon_url": "", # Kosong untuk menguji fallback icon bawaan di HTML
        "download_url": "#",
        "total_files": 1
    },
    {
        "id": 3,
        "name": "Fabulously Optimized Pack",
        "title": "Fabulously Optimized Engine Pack",
        "category": "java",
        "version_range": "1.19 - 1.21",
        "desc": "Kumpulan mod performa (Sodium, Lithium, dll) racikan khusus untuk mendongkrak FPS saat merender chunk dalam jumlah besar.",
        "icon_url": "https://media.forgecdn.net/avatars/398/12/637604312458428135.png",
        "download_url": "#",
        "total_files": 12
    },
    {
        "id": 4,
        "name": "Bedrock Cyber-UI Addon",
        "title": "Cyber-UI & HUD Pack Addon",
        "category": "mcpe",
        "version_range": "1.20 - 1.21",
        "desc": "Mengubah total tampilan antarmuka Minecraft Bedrock/PE menjadi bertema scifi futuristik dengan dominasi warna hijau neon.",
        "icon_url": "https://media.forgecdn.net/avatars/412/820/637651034928129032.png",
        "download_url": "#",
        "total_files": 2
    },
    {
        "id": 5,
        "name": "Realistic Physics Mcpe Pack",
        "title": "Realistic Item Physics Add-on",
        "category": "mcpe",
        "version_range": "1.21",
        "desc": "Add-on interaktif untuk Minecraft Pocket Edition yang memberikan efek gravitasi nyata pada balok dan item saat dihancurkan.",
        "icon_url": "",
        "download_url": "#",
        "total_files": 1
    }
]

# 1. ROUTE UTAMA: HALAMAN BERANDA
@app.route('/')
def index():
    # Mengirim seluruh database mod ke index.html agar dirender oleh Jinja loop
    return render_template('index.html', mods=MODS_DATABASE)

# 2. ROUTE DETAIL MOD: COCOK DENGAN LINK /mod/<id> DI INDEX.HTML
@app.route('/mod/<int:mod_id>')
def mod_detail(mod_id):
    # Mencari mod berdasarkan ID unik di dalam list database
    selected_mod = next((m for m in MODS_DATABASE if m['id'] == mod_id), None)
    
    if selected_mod:
        return render_template('mod.html', mod=selected_mod)
    else:
        # Jika ID tidak ditemukan, kembalikan ke beranda
        return redirect(url_for('index'))

# 3. ROUTE TUTORIAL (TAMBAHAN COMPATIBILITY BIAR TIDAK 404)
@app.route('/tutorial')
def tutorial():
    return "<h3>Panduan Instalasi RexCraft Hub: Ekstrak berkas zip/jar ke direktori .minecraft/mods atau com.mojang/behavior_packs.</h3>"

# 4. API ENDPOINT (OPSIONAL - JIKA ANDA INGIN MENGEMBANGKAN FITUR LIVE SEARCH LEWAT AJAX)
@app.route('/api/mods', methods=['GET'])
def get_all_mods():
    return jsonify(MODS_DATABASE)

if __name__ == '__main__':
    # Menjalankan server pada port default dengan mode debug aktif
    app.run(debug=True, port=5000)
