# CrossShot-Linker-JPG-to-RAW-File-Matching-Utility 🔗📸


Smart JPG-to-RAW matching utility for photographers working with multiple camera systems

![CrossShot Linker Demo](assets/demo.gif)

## Features ✨

- **Multi-Format Support**: Works with 15+ RAW formats from major camera brands
- **Smart Matching**:
  - EXIF metadata analysis
  - Timestamp correlation
  - Perceptual image hashing
- **Flexible Workflow**:
  - Separate input folders for JPG and RAW files
  - Custom output directory
  - Comprehensive matching report
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Supported Camera Formats 📷

| Manufacturer | Supported RAW Formats | File Extensions |
|--------------|-----------------------|-----------------|
| Canon        | CR2, CR3              | .cr2, .cr3      |
| Nikon        | NEF, NRW              | .nef, .nrw      |
| Sony         | ARW                   | .arw            |
| Fujifilm     | RAF                   | .raf            |
| Panasonic    | RW2                   | .rw2            |
| Olympus      | ORF                   | .orf            |
| Pentax       | PEF, DNG              | .pef, .dng      |
| Leica        | DNG, RAW              | .dng, .raw      |
| Sigma        | X3F                   | .x3f            |
| Hasselblad   | 3FR, FFF              | .3fr, .fff      |

## Installation 💻

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
1. Clone repository:
```bash
git clone https://github.com/yourusername/CrossShot-Linker.git
cd CrossShot-Linker
exit

2. Install dependencies:

```bash
pip install -r requirements.txt

3. Run the script:
```bash
python match_photos.py
