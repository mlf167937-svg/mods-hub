# =========================================================================
# KODE PERBAIKAN SINKRONISASI FOLDER UPLOADS (PASTIKAN PAKE HURUF 'S')
# =========================================================================
BASE_UPLOAD_DIR = os.path.join('static', 'uploads') # <-- Sudah diperbaiki!

def get_dynamic_mods():
    mods_list = []
    mod_id_counter = 1
    
    if not os.path.exists(BASE_UPLOAD_DIR):
        return mods_list

    for category in ['java', 'mcpe']:
        category_path = os.path.join(BASE_UPLOAD_DIR, category)
        if not os.path.exists(category_path):
            continue
            
        for mod_folder in os.listdir(category_path):
            mod_path = os.path.join(category_path, mod_folder)
            
            if os.path.isdir(mod_path):
                display_title = mod_folder.replace('-', ' ').replace('_', ' ').title()
                
                # SINKRONISASI JALUR ICON
                icon_url = f"/static/uploads/{category}/{mod_folder}/icon.png"
                if not os.path.exists(os.path.join(mod_path, 'icon.png')):
                    icon_url = None
                
                versions = []
                game_versions_found = []
                
                for file_name in os.listdir(mod_path):
                    file_full_path = os.path.join(mod_path, file_name)
                    
                    if os.path.isfile(file_full_path) and file_name != 'icon.png' and not file_name.startswith('.'):
                        
                        loader, game_version = parse_file_info(file_name)
                        
                        if game_version != "Unknown":
                            game_versions_found.append(game_version)
                        
                        try:
                            size_bytes = os.path.getsize(file_full_path)
                            if size_bytes < 1024 * 1024:
                                file_size = f"{round(size_bytes / 1024, 1)} KB"
                            else:
                                file_size = f"{round(size_bytes / (1024 * 1024), 1)} MB"
                        except:
                            file_size = "Unknown"
                        
                        clean_display_name = file_name.split('.zip')[0].split('.jar')[0].split('.mcpack')[0].replace('_', ' ').title()

                        versions.append({
                            "version_name": clean_display_name,
                            "loader": loader,
                            "game_version": game_version,
                            "file_size": file_size,
                            # SINKRONISASI LINK DOWNLOAD
                            "download_url": f"/static/uploads/{category}/{mod_folder}/{file_name}"
                        })

                versions.sort(key=lambda x: x['game_version'], reverse=True)
                
                if game_versions_found:
                    unique_versions = sorted(list(set(game_versions_found)))
                    if len(unique_versions) > 1:
                        version_range = f"{unique_versions[0]} - {unique_versions[-1]}"
                    else:
                        version_range = unique_versions[0]
                else:
                    version_range = "Multi-Version"

                mods_list.append({
                    "id": mod_id_counter,
                    "category": category,
                    "name": mod_folder,
                    "title": display_title,
                    "desc": f"Berkas resmi kustom {display_title} untuk kategori Minecraft {category.upper()} Edition.",
                    "version_range": version_range,
                    "icon_url": icon_url,
                    "project_type": "Texture Pack" if category == 'mcpe' else "Mod / Optimization",
                    "versions": versions
                })
                mod_id_counter += 1
                
    return mods_list
