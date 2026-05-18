import os
from flask import Flask, render_template, abort, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# FUNGSI DETEKSI & URUTKAN VERSI (Terbaru di atas, lama di bawah)
def parse_version(file_dict):
    v_str = file_dict['version']
    if v_str.lower() == 'latest':
        return [999, 999, 999]  # Selalu taruh teks 'Latest' di paling atas
    try:
        # Memecah '1.21.11' menjadi [1, 21, 11] agar bisa diurutkan dengan benar secara angka
        return [int(x) for x in v_str.split('.')]
    except ValueError:
        # Jaga-jaga kalau format versinya mengandung huruf atau teks lain
        return [0, 0, 0]

def get_all_mods():
    mods = []
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        return mods

    # Pindai folder secara dinamis agar aman dari perbedaan huruf besar/kecil (Java/JAVA/bedrock/Bedrock)
    for platform_dir in os.listdir(UPLOAD_FOLDER):
        platform_lower = platform_dir.lower()
        if platform_lower not in ['java', 'bedrock', 'mcpe']:
            continue
            
        # Standarisasi nama platform untuk keperluan routing template
        platform_key = 'bedrock' if platform_lower in ['bedrock', 'mcpe'] else 'java'
        platform_path = os.path.join(UPLOAD_FOLDER, platform_dir)
        
        if not os.path.isdir(platform_path):
            continue
            
        for folder_name in os.listdir(platform_path):
            folder_path = os.path.join(platform_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            info_file = os.path.join(folder_path, 'info.txt')
            if not os.path.exists(info_file):
                continue
                
            try:
                # FIX: Menggunakan utf-8-sig untuk otomatis membuang karakter bom tersembunyi dari Notepad Windows
                with open(info_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read().splitlines()
                
                non_empty_lines = [line.strip() for line in content if line.strip()]
                
                if len(non_empty_lines) < 3:
                    continue
                
                # Pembersihan cerdas teks awalan (Prefix) jika terlanjur ditulis manual
                title = non_empty_lines[0]
                for prefix in ['judul:', 'title:', 'name:', 'nama:']:
                    if title.lower().startswith(prefix):
                        title = title[len(prefix):].strip()
                
                category = non_empty_lines[1]
                for prefix in ['kategori:', 'category:', 'type:', 'jenis:']:
                    if category.lower().startswith(prefix):
                        category = category[len(prefix):].strip()
                
                icon_config = non_empty_lines[2]
                if icon_config.lower().startswith('icon:'):
                    icon_config = icon_config[5:].strip()
                
                # FIX PINTAR: Cari nama file icon asli di dalam folder secara Case-Insensitive
                icon = None
                for real_file in os.listdir(folder_path):
                    if real_file.lower() == icon_config.lower():
                        icon = real_file
                        break
                
                # Jaga-jaga kalau user salah nulis nama icon di info.txt, cari file gambar default di folder tersebut
                if not icon:
                    for real_file in os.listdir(folder_path):
                        if real_file.lower() in ['icon.png', 'icon.jpg', 'icon.jpeg', 'logo.png']:
                            icon = real_file
                            break
                    if not icon:
                        icon = "icon.png" # Fallback terakhir
                
                # Gabungkan sisa baris menjadi deskripsi utuh
                desc_raw = "\n".join(non_empty_lines[3:])
                for prefix in ['deskripsi:', 'description:', 'desc:', 'info:']:
                    if desc_raw.lower().startswith(prefix):
                        desc_raw = desc_raw[len(prefix):].strip()
                
                # BACA BERKAS DOWNLOAD (Mendukung .zip, .mcpack, .mcaddon, .jar, .mcworld secara fleksibel)
                files_info = []
                for file in os.listdir(folder_path):
                    if file.lower().endswith(('.zip', '.mcpack', '.mcaddon', '.jar', '.mcworld', '.mctemplate')):
                        base_name = file.rsplit('.', 1)[0]
                        if '-' in base_name:
                            version = base_name.rsplit('-', 1)[1]
                        elif '_' in base_name:
                            version = base_name.rsplit('_', 1)[1]
                        else:
                            version = 'Latest'
                        files_info.append({'version': version, 'filename': file})
                
                # FIX AUTO-SORT: Mengurutkan versi berkas secara menurun (Terbaru di atas)
                files_info.sort(key=parse_version, reverse=True)
                
                # Baca file galeri dokumentasi mod
                gallery_info = []
                for file in os.listdir(folder_path):
                    if file.lower().startswith('galery') and file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        base_name = file.rsplit('.', 1)[0]
                        txt_file = os.path.join(folder_path, f"{base_name}.txt")
                        
                        text_content = ""
                        if os.path.exists(txt_file):
                            with open(txt_file, 'r', encoding='utf-8-sig') as tf:
                                text_content = tf.read().strip()
                        
                        gallery_info.append({
                            'image': file,
                            'text': text_content
                        })
                
                mods.append({
                    'platform': platform_key,
                    'actual_platform_dir': platform_dir, # Folder fisik asli di server
                    'folder_name': folder_name,
                    'title': title,
                    'category': category,
                    'icon': icon,
                    'desc': desc_raw if desc_raw else "Tidak ada deskripsi tersedia.",
                    'files': files_info,
                    'gallery': gallery_info
                })
            except Exception as e:
                print(f"Gagal memproses mod di folder {folder_name}: {e}")
                
    return mods

def get_community_posts():
    posts = []
    community_path = os.path.join('static', 'community')
    if not os.path.exists(community_path):
        os.makedirs(community_path, exist_ok=True)
        return posts
        
    for folder_name in os.listdir(community_path):
        folder_path = os.path.join(community_path, folder_name)
        if not os.path.isdir(folder_path):
            continue
            
        txt_file = os.path.join(folder_path, 'comunitypost.txt')
        if not os.path.exists(txt_file):
            continue
            
        try:
            with open(txt_file, 'r', encoding='utf-8-sig') as f:
                text_content = f.read().strip()
                
            if not text_content:
                continue
                
            lines = text_content.split('\n')
            yt_link = lines[-1].strip()
            
            if yt_link.startswith('http://') or yt_link.startswith('https://'):
                text_body = '\n'.join(lines[:-1]).strip()
            else:
                text_body = text_content
                yt_link = "https://youtube.com"
                
            thumbnail_file = None
            for file in os.listdir(folder_path):
                if file.lower().startswith('thumbnail') and file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    thumbnail_file = file
                    break
            
            if not thumbnail_file:
                thumbnail_file = "thumbnail.png"
                    
            posts.append({
                'id': folder_name,
                'text': text_body,
                'link': yt_link,
                'thumbnail': thumbnail_file
            })
        except Exception as e:
            print(f"Error membaca komunitas {folder_name}: {e}")
            
    posts.sort(key=lambda x: x['id'], reverse=True)
    return posts

@app.route('/')
def index():
    all_mods = get_all_mods()
    
    # FIX BANNER: Cari otomatis file banner dengan format .png, .jpg, atau .jpeg secara cerdas
    img_dir = os.path.join('static', 'img')
    banner_file = 'banner.png' 
    
    if os.path.exists(img_dir):
        for file in os.listdir(img_dir):
            if file.lower() in ['banner.png', 'banner.jpg', 'banner.jpeg', 'banner.webp']:
                banner_file = file
                break
                
    banner_url = f"/static/img/{banner_file}"
    return render_template('index.html', mods=all_mods, banner_url=banner_url)

@app.route('/mod/<platform>/<folder_name>')
def mod_detail(platform, folder_name):
    if platform not in ['java', 'bedrock']:
        abort(404)
        
    all_mods = get_all_mods()
    target_mod = None
    for m in all_mods:
        if m['platform'] == platform and m['folder_name'] == folder_name:
            target_mod = m
            break
            
    if not target_mod:
        abort(404)
        
    return render_template('mod.html', mod=target_mod)

@app.route('/community')
def community_page():
    posts = get_community_posts()
    return render_template('community.html', posts=posts)

@app.route('/download/<platform_dir>/<folder_name>/<filename>')
def download_file(platform_dir, folder_name, filename):
    # Menggunakan folder fisik asli agar tidak terpeleset masalah case-sensitive Linux
    safe_path = os.path.join(UPLOAD_FOLDER, platform_dir, folder_name)
    return send_from_directory(safe_path, filename, as_attachment=True)

@app.route('/ai')
def ai_page():
    return "<body style='background:#0b0c10;color:#fff;font-family:sans-serif;padding:30px;'><h1>RexAI Q&A</h1><p>Fitur AI Chatbot RexCraftHub siap dikembangkan di sini!</p></body>"

@app.route('/tutorial')
def tutorial_page():
    return "<body style='background:#0b0c10;color:#fff;font-family:sans-serif;padding:30px;'><h1>Tutorial Pemasangan</h1><p>Halaman panduan instalasi mod dan shader RexCraft.</p></body>"

if __name__ == '__main__':
    app.run(debug=True)
