# =========================================================================
# REXCRAFT MODS HUB - CORE BACKEND ENGINE (FLASK MASTER)
# =========================================================================
# Dioptimalkan untuk deployment lancar di platform Render Cloud.
# Pastikan file ini berada di root folder repositori GitHub Bos.
# =========================================================================

from flask import Flask, render_template, abort

app = Flask(__name__)

# =========================================================================
# DATABASE REPOSITORI MODS LOCAL (MENGGUNAKAN FILE ASLI RACIKAN BOS)
# =========================================================================
# Jika Bos punya mod racikan baru lagi nanti, tinggal tambahkan blok baru 
# di dalam tanda kurung siku [ ... ] ini menggunakan tanda koma (,).
# =========================================================================
MODS_DATABASE = [
    {
        "id": 1,
        "category": "java",
        "name": "mod-racikan-bos",
        "title": "Mod Racikan Premium v1.0",
        "desc": "Berkas modifikasi hasil racikan kustom RexCraft Engine, dijamin super stabil, optimal, dan anti-lag.",
        "version_range": "1.20 - 1.21+",
        # Jalur asset gambar & file zip asli milik Bos di GitHub:
        "icon_url": "/static/upload/java/mod_racikan/icon.png",
        "download_url": "/static/upload/java/mod_racikan/mod.zip"
    }
]

# =========================================================================
# ROUTING CONTROLLER A: HALAMAN UTAMA / DASHBOARD (index.html)
# =========================================================================
@app.route('/')
def home_dashboard():
    # Mengirimkan list MODS_DATABASE ke dalam file templates/index.html 
    # untuk di-render secara otomatis oleh mesin Jinja2.
    return render_template('index.html', mods=MODS_DATABASE)

# =========================================================================
# ROUTING CONTROLLER B: HALAMAN DETAIL BERKAS MOD (mod.html)
# =========================================================================
@app.route('/mod/<int:mod_id>')
def mod_detail_page(mod_id):
    # Algoritma pencarian ID berkas di dalam database local
    selected_mod = None
    for item in MODS_DATABASE:
        if item["id"] == mod_id:
            selected_mod = item
            break
            
    # Jika ID berkas tidak ditemukan di database, lemparkan eror 404
    if selected_mod is None:
        abort(404)
        
    # Mengirimkan data berkas spesifik ke file templates/mod.html
    return render_template('mod.html', mod=selected_mod)

# =========================================================================
# ROUTING CONTROLLER C: HALAMAN PANDUAN / TUTORIAL PEMASANGAN
# =========================================================================
@app.route('/tutorial')
def tutorial_page():
    # Menampilkan halaman edukasi jalur pemasangan berkas resmi RexCraft
    return render_template('tutorial.html')

# =========================================================================
# PLATFORM ERROR HANDLER SYSTEM (FALLBACK CORE)
# =========================================================================
@app.errorhandler(404)
def page_not_found(error):
    # Mengembalikan status 404 jika user mencoba mengakses link gaib
    return "<h1>404 - Berkas Modifikasi Tidak Ditemukan!</h1><p>Kembali ke <a href='/'>Dashboard RexCraft</a></p>", 404

# =========================================================================
# LOCAL COMPILING APPLICATION RUNNER (ANTI-BUG TRIGGER)
# =========================================================================
if __name__ == '__main__':
    # Mode debug diaktifkan untuk deteksi eror real-time saat testing lokal
    app.run(debug=True, host='0.0.0.0', port=5000)
