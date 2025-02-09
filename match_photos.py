import os
import shutil
from PIL import Image
import exifread
import rawpy
import imagehash
import io

# Supported raw formats structure
RAW_FORMATS = [
    # Canon
    {'brand': 'Canon', 'name': 'CR2', 'ext': 'cr2', 'desc': 'Canon Raw 2'},
    {'brand': 'Canon', 'name': 'CR3', 'ext': 'cr3', 'desc': 'Canon Raw 3, used in newer models'},
    
    # Nikon
    {'brand': 'Nikon', 'name': 'NEF', 'ext': 'nef', 'desc': 'Nikon Electronic Format'},
    {'brand': 'Nikon', 'name': 'NRW', 'ext': 'nrw', 'desc': 'Nikon Raw, used in some compact cameras'},
    
    # Sony
    {'brand': 'Sony', 'name': 'ARW', 'ext': 'arw', 'desc': 'Sony Alpha Raw'},
    
    # Fujifilm
    {'brand': 'Fujifilm', 'name': 'RAF', 'ext': 'raf', 'desc': 'Fujifilm Raw'},
    
    # Panasonic
    {'brand': 'Panasonic', 'name': 'RW2', 'ext': 'rw2', 'desc': 'Panasonic Raw'},
    
    # Olympus
    {'brand': 'Olympus', 'name': 'ORF', 'ext': 'orf', 'desc': 'Olympus Raw Format'},
    
    # Pentax
    {'brand': 'Pentax', 'name': 'PEF', 'ext': 'pef', 'desc': 'Pentax Electronic Format'},
    {'brand': 'Pentax', 'name': 'DNG', 'ext': 'dng', 'desc': 'Digital Negative, used in some models'},
    
    # Leica
    {'brand': 'Leica', 'name': 'DNG', 'ext': 'dng', 'desc': 'Digital Negative, commonly used in Leica cameras'},
    {'brand': 'Leica', 'name': 'RAW', 'ext': 'raw', 'desc': 'Leica-specific raw format in some models'},
    
    # Sigma
    {'brand': 'Sigma', 'name': 'X3F', 'ext': 'x3f', 'desc': 'Sigma X3F, used in Foveon sensor cameras'},
    
    # Hasselblad
    {'brand': 'Hasselblad', 'name': '3FR', 'ext': '3fr', 'desc': 'Hasselblad Raw'},
    {'brand': 'Hasselblad', 'name': 'FFF', 'ext': 'fff', 'desc': 'Hasselblad Raw'},
]

def select_raw_format():
    """Display format options and return selected extension"""
    current_brand = None
    print("\nSelect your raw file format:")
    for idx, fmt in enumerate(RAW_FORMATS, 1):
        if fmt['brand'] != current_brand:
            print(f"\n{fmt['brand']}:")
            current_brand = fmt['brand']
        print(f"  {idx}: {fmt['name']} - {fmt['desc']}")
    
    while True:
        try:
            choice = int(input("\nEnter the number of your raw format: "))
            if 1 <= choice <= len(RAW_FORMATS):
                selected = RAW_FORMATS[choice-1]
                print(f"Selected: {selected['brand']} {selected['name']} (.{selected['ext']})")
                return selected
            raise ValueError
        except (ValueError, IndexError):
            print("Invalid selection. Please enter a valid number.")

def get_exif_original_filename(image_path):
    """Extract OriginalFileName from EXIF metadata"""
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        for tag in ['EXIF OriginalFileName', 'Image DocumentName']:
            if tag in tags:
                return str(tags[tag]).strip()
        return None

def get_exif_datetime_original(image_path):
    """Extract DateTimeOriginal from EXIF metadata"""
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        return str(tags.get('EXIF DateTimeOriginal', '')).strip()

def get_image_hash(image):
    """Generate perceptual hash for an image"""
    return imagehash.average_hash(image)

def get_raw_thumbnail(raw_path):
    """Extract embedded thumbnail from raw file"""
    try:
        with rawpy.imread(raw_path) as raw:
            if raw.has_thumb:
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    return Image.open(io.BytesIO(thumb.data))
    except Exception as e:
        print(f"Error processing {raw_path}: {e}")
    return None

def match_files(jpg_folder, raw_folder, raw_ext):
    jpg_files = [f for f in os.listdir(jpg_folder) if f.lower().endswith('.jpg')]
    raw_files = [f for f in os.listdir(raw_folder) if f.lower().endswith(f'.{raw_ext}')]

    matches = []
    matched_raws = set()
    matched_jpgs = set()

    # First pass: Try to match using EXIF OriginalFileName
    for jpg in jpg_files:
        jpg_path = os.path.join(jpg_folder, jpg)
        original_name = get_exif_original_filename(jpg_path)
        if original_name:
            possible_raws = [r for r in raw_files 
                           if r.lower() == original_name.lower() + f'.{raw_ext}']
            if possible_raws:
                matches.append((jpg, possible_raws[0]))
                matched_jpgs.add(jpg)
                matched_raws.add(possible_raws[0])

    # Second pass: Try to match using DateTimeOriginal
    remaining_jpgs = [j for j in jpg_files if j not in matched_jpgs]
    remaining_raws = [r for r in raw_files if r not in matched_raws]

    date_dict = {}
    for file in remaining_jpgs + remaining_raws:
        folder = jpg_folder if file.lower().endswith('.jpg') else raw_folder
        path = os.path.join(folder, file)
        dt = get_exif_datetime_original(path)
        if dt:
            date_dict.setdefault(dt, {'jpgs': [], 'raws': []})
            if file.lower().endswith('.jpg'):
                date_dict[dt]['jpgs'].append(file)
            else:
                date_dict[dt]['raws'].append(file)

    for dt, files in date_dict.items():
        while files['jpgs'] and files['raws']:
            matches.append((files['jpgs'].pop(0), files['raws'].pop(0)))

    # Third pass: Use perceptual hashing on remaining files
    remaining_jpgs = [j for j in jpg_files if j not in [m[0] for m in matches]]
    remaining_raws = [r for r in raw_files if r not in [m[1] for m in matches]]

    jpg_hashes = {}
    for jpg in remaining_jpgs:
        try:
            with Image.open(os.path.join(jpg_folder, jpg)) as img:
                jpg_hashes[jpg] = get_image_hash(img)
        except Exception as e:
            print(f"Error processing {jpg}: {e}")

    raw_hashes = {}
    for raw in remaining_raws:
        thumb = get_raw_thumbnail(os.path.join(raw_folder, raw))
        if thumb:
            raw_hashes[raw] = get_image_hash(thumb)

    # Find closest matches
    while jpg_hashes and raw_hashes:
        best_match = None
        best_score = float('inf')
        
        for jpg, j_hash in jpg_hashes.items():
            for raw, r_hash in raw_hashes.items():
                score = j_hash - r_hash
                if score < best_score:
                    best_score = score
                    best_match = (jpg, raw)
        
        if best_score < 10:  # Adjust threshold as needed
            matches.append(best_match)
            del jpg_hashes[best_match[0]]
            del raw_hashes[best_match[1]]
        else:
            break

    return matches

if __name__ == "__main__":
    # Get user inputs
    jpg_folder = input("Enter the path to the JPG folder: ").strip()
    raw_folder = input("Enter the path to the RAW folder: ").strip()
    selected_format = select_raw_format()
    dest_folder = input("Enter destination folder path for matched RAW files: ").strip()

    # Create destination folder if it doesn't exist
    os.makedirs(dest_folder, exist_ok=True)

    # Perform matching
    matched_pairs = match_files(jpg_folder, raw_folder, selected_format['ext'])
    
    # Copy files and generate report
    print("\nMatched pairs:")
    for jpg, raw in matched_pairs:
        print(f"{jpg} -> {raw}")
        src_path = os.path.join(raw_folder, raw)
        dest_path = os.path.join(dest_folder, raw)
        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied {raw} to {dest_folder}")
        except Exception as e:
            print(f"Failed to copy {raw}: {e}")

    # Generate report
    report_path = os.path.join(dest_folder, 'matching_report.txt')
    with open(report_path, 'w') as f:
        f.write(f"Matched pairs ({selected_format['brand']} {selected_format['name']}):\n")
        for pair in matched_pairs:
            f.write(f"JPG: {pair[0]} -> RAW: {pair[1]}\n")
    
    print(f"\nMatching report saved to {report_path}")