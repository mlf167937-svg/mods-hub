from flask import Flask, render_template, abort, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_online_mods():
    """Fungsi otomatis mendeteksi file yang kamu upload ke GitHub"""
    mods_list = []
    
    # Membaca semua file di dalam folder static/uploads
    if os.path.exists(UPLOAD_FOLDER):
        files = os.listdir(UPLOAD_FOLDER)
        
        for filename in files:
            # Lewati file test atau file sistem tersembunyi
            if filename.startswith('.') or filename == 'test.txt':
                continue
                
            # Mengambil nama mod dari nama file (Mengganti '_' atau '-' dengan spasi)
            # Contoh file: Cyberpunk_Shaders_v1.20.jar -> Judul: Cyberpunk Shaders v1.20
            clean_title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
            
            # Sistem otomatis menebak versi Minecraft (Opsional, jika ada tulisan versi di nama filenya)
            version = "All Version"
            if "1." in filename:
                # Mencoba mengambil teks versi, misal '1.20.1'
                parts = filename.split('_')
                for part in parts:
                    if part.startswith('1.') or '1.' in part:
                        version = os.path.splitext(part)[0]

            mods_list.append({
                "title": clean_title,
                "version": version,
                "desc": f"Modifikasi Minecraft resmi dari RexCraft Mods. Silakan unduh file {filename} untuk memasang.",
                "file": filename
            })
            
    return mods_list

@app.route("/")
def home():
    # Mengambil list file terbaru yang ditarik dari GitHub
    mods = get_online_mods()
    return render_template("index.html", mods=mods)

@app.route("/mod/<filename>")
def mod_page(filename):
    mods = get_online_mods()
    mod = None

    for m in mods:
        if m["file"] == filename:
            mod = m
            break

    if not mod:
        abort(404)

    return render_template("mod.html", mod=mod)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run()
