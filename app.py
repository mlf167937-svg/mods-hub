import os
from flask import Flask, render_template, abort, send_from_directory

app = Flask(__name__)

# Konfigurasi Lokasi Upload Mod
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_all_mods():
    mods = []
    platforms = ['java', 'bedrock']
    
    for platform in platforms:
        platform_path = os.path.join(UPLOAD_FOLDER, platform)
        if not os.path.exists(platform_path):
            continue
            
        for folder_name in os.listdir(platform_path):
            folder_path = os.path.join(platform_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            info_file = os.path.join(folder_path, 'info.txt')
            if not os.path.exists(info_file):
                continue
                
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    content = f.read().splitlines()
                
                # Filter hanya baris yang ada isinya (Abaikan baris kosong tak sengaja)
                non_empty_lines = [line.strip() for line in content if line.strip()]
                
                if len(non_empty_lines) < 3:
                    continue
                    
                # FITUR PINTAR: Bersihkan auto prefix jika user nulis "Judul: / Kategori: / Icon:"
                title = non_empty_lines[0]
                if title.lower().startswith('judul:'): title = title[6:].strip()
                elif title.lower().startswith('title:'): title = title[6:].strip()
                
                category = non_empty_lines[1]
                if category.lower().startswith('kategori:'): category = category[9:].strip()
                elif category.lower().startswith('category:'): category = category[9:].strip()
                
                icon = non_empty_lines[2]
                if icon.lower().startswith('icon:'): icon = icon[5:].strip()
                
                # Proteksi Case-Sensitivity Linux untuk Gambar Icon
                for real_file in os.listdir(folder_path):
                    if real_file.lower() == icon.lower():
                        icon = real_file
                        break
                
                # Deskripsi mengambil seluruh sisa baris di info.txt secara utuh
                desc = "\n".join(non_empty_lines[3:])
                if desc.lower().startswith('deskripsi:'): desc = desc[10:].strip()
                elif desc.lower().startswith('description:'): desc = desc[12:].strip()
                
                # BACA FILE VERSI DOWNLOAD (Fix: Case-Insensitive untuk ekstensi .ZIP / .MCPACK di Render)
                files_info = []
                for file in os.listdir(folder_path):
                    if file.lower().endswith(('.zip', '.mcpack', '.mcaddon', '.jar')):
                        base_name = file.rsplit('.', 1)[0]
                        if '-' in base_name:
                            version = base_name.rsplit('-', 1)[1]
                        elif '_' in base_name:
                            version = base_name.rsplit('_', 1)[1]
                        else:
                            version = 'Latest'
                        files_info.append({'version': version, 'filename': file})
                
                # Baca file galeri
                gallery_info = []
                for file in os.listdir(folder_path):
                    if file.lower().startswith('galery') and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        base_name = file.rsplit('.', 1)[0]
                        txt_file = os.path.join(folder_path, f"{base_name}.txt")
                        
                        text_content = ""
                        if os.path.exists(txt_file):
                            with open(txt_file, 'r', encoding='utf-8') as tf:
                                text_content = tf.read().strip()
                        
                        gallery_info.append({
                            'image': file,
                            'text': text_content
                        })
                
                mods.append({
                    'platform': platform,
                    'folder_name': folder_name,
                    'title': title,
                    'category': category,
                    'icon': icon,
                    'desc': desc,
                    'files': files_info,
                    'gallery': gallery_info
                })
            except Exception as e:
                print(f"Error reading mod {folder_name}: {e}")
                
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
            with open(txt_file, 'r', encoding='utf-8') as f:
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
                
            thumbnail_file = "thumbnail.png"
            for file in os.listdir(folder_path):
                if file.lower().startswith('thumbnail') and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    thumbnail_file = file
                    break
                    
            posts.append({
                'id': folder_name,
                'text': text_body,
                'link': yt_link,
                'thumbnail': thumbnail_file
            })
        except Exception as e:
            print(f"Error membaca postingan {folder_name}: {e}")
            
    posts.sort(key=lambda x: x['id'], reverse=True)
    return posts

@app.route('/')
def index():
    all_mods = get_all_mods()
    return render_template('index.html', mods=all_mods)

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

@app.route('/download/<platform>/<folder_name>/<filename>')
def download_file(platform, folder_name, filename):
    safe_path = os.path.join(UPLOAD_FOLDER, platform, folder_name)
    return send_from_directory(safe_path, filename, as_attachment=True)

@app.route('/ai')
def ai_page():
    return "<h1>RexAI Q&A Page</h1><p>Fitur AI Chatbot RexCraftHub siap dikembangkan di sini!</p>"

@app.route('/tutorial')
def tutorial_page():
    return "<h1>Tutorial Pemasangan</h1><p>Halaman panduan instalasi mod dan shader RexCraft.</p>"

if __name__ == '__main__':
    app.run(debug=True)
