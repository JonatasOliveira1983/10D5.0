import os
import shutil
import re

def perform_bulk_archive():
    # Detect directory
    current_dir = os.getcwd()
    if current_dir.endswith("backend"):
        base_dir = current_dir
    else:
        # Tenta localizar a pasta backend a partir da raiz
        potential_path = os.path.join(current_dir, "1CRYPTEN_SPACE_V4.0", "backend")
        if os.path.exists(potential_path):
            base_dir = potential_path
        else:
            base_dir = current_dir
        
    archive_dir = os.path.join(base_dir, "legacy_archives")
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        
    # Regex expandido para pegar quase todo o "lixo"
    pattern = re.compile(r"^(check|debug|test|audit|reset|nuke|wipe|diag|diagnose|diagnostic|get|search|dump|fix|clean|cleanup|clear|restore|verify|surgical|ultra|inject|kill|purge|analyze|inspect|list|read|rectify|refine|replace|rescue|view|seed|surgical|ultra|direct|exhaustive|fast|final|force|full|marco|pristine|surgical|tmp)_.*\.py$")
    
    all_items = os.listdir(base_dir)
    archived_count = 0
    
    print(f"Scanning directory: {base_dir}")
    print(f"Total items found: {len(all_items)}")
    
    for file in all_items:
        file_path = os.path.join(base_dir, file)
        if os.path.isfile(file_path):
            if pattern.match(file.lower()):
                dst = os.path.join(archive_dir, file)
                try:
                    # Se o arquivo já existe no destino, removemos para evitar erro no move
                    if os.path.exists(dst):
                        os.remove(dst)
                    shutil.move(file_path, dst)
                    print(f"Archived: {file}")
                    archived_count += 1
                except Exception as e:
                    print(f"Error moving {file}: {e}")
            else:
                # print(f"Skipping (no match): {file}")
                pass
                
    print(f"\n[GUARDIAN-CLEAN] Total de {archived_count} arquivos movidos para /legacy_archives.")

if __name__ == "__main__":
    perform_bulk_archive()
