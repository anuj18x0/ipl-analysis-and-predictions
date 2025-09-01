import os
import requests
import pickle
import re
import bz2
from pathlib import Path


def decompress_score_model(compressed_path):
    """Decompress the BZ2 score model and save as original pickle file"""
    try:
        print("🔓 Decompressing score model...")
        
        # Output path for decompressed model
        output_path = "Model/predict_ipl_score_best_rf.pkl"
        
        # Ensure Model directory exists
        Path("Model").mkdir(parents=True, exist_ok=True)
        
        # Decompress BZ2 file
        with bz2.open(compressed_path, 'rb') as compressed_file:
            model_data = compressed_file.read()
        
        # Save as regular pickle file
        with open(output_path, 'wb') as output_file:
            output_file.write(model_data)
        
        # Verify the decompressed model
        model = pickle.loads(model_data)
        
        original_size = os.path.getsize(compressed_path) / (1024*1024)
        decompressed_size = os.path.getsize(output_path) / (1024*1024)
        
        print(f"✅ Model decompressed successfully!")
        print(f"   Compressed: {original_size:.1f} MB")
        print(f"   Decompressed: {decompressed_size:.1f} MB")
        print(f"   Model type: {type(model)}")
        print(f"   Trees: {model.n_estimators}")
        
        # Optionally remove compressed file to save space
        os.remove(compressed_path)
        print(f"🗑️  Removed compressed file to save space")
        
        return True
        
    except Exception as e:
        print(f"❌ Error decompressing model: {str(e)}")
        return False

def get_google_drive_download_url(share_url):
    """Convert Google Drive share URL to direct download URL"""
    if 'drive.google.com' in share_url and '/file/d/' in share_url:
        file_id = share_url.split('/file/d/')[1].split('/')[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return share_url

def download_from_google_drive(url, file_path):
    """Download file from Google Drive handling virus scan warning for large files"""
    import requests
    import re
    
    session = requests.Session()
    
    # Convert to proper download URL
    if '/file/d/' in url:
        file_id = url.split('/file/d/')[1].split('/')[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    else:
        download_url = url
    
    print(f"   🌐 Downloading from: {download_url}")
    
    # First request
    response = session.get(download_url, stream=True)
    
    # Check if this is a virus scan warning (HTML content)
    content_type = response.headers.get('content-type', '')
    if 'text/html' in content_type:
        print(f"   🦠 Handling virus scan warning for large file...")
        
        # For very large files, Google Drive uses a different confirmation system
        # Try to extract the confirmation token from the HTML
        html_content = response.text
        
        # Look for the confirmation form with multiple patterns
        patterns = [
            r'name="confirm"\s+value="([^"]*)"',
            r'"confirm":"([^"]*)"',
            r'confirm=([^&"\']+)',
            r'download&amp;id=' + file_id + r'&amp;confirm=([^&"\']+)',
        ]
        
        confirm_token = None
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                confirm_token = match.group(1)
                print(f"   🔑 Found confirmation token: {confirm_token}")
                break
        
        if confirm_token:
            # Try the confirmation URL
            confirm_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
            print(f"   🔄 Making confirmed request...")
            response = session.get(confirm_url, stream=True)
            
            # Check if we still get HTML (another confirmation needed)
            if response.headers.get('content-type', '').startswith('text/html'):
                print(f"   🔄 Second confirmation needed, trying alternative method...")
                
                # Try the usercontent domain which sometimes bypasses the warning
                alt_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm={confirm_token}"
                response = session.get(alt_url, stream=True)
                
                # If still HTML, try without stream
                if response.headers.get('content-type', '').startswith('text/html'):
                    print(f"   🔄 Trying non-stream request...")
                    response = session.get(confirm_url, stream=False)
                    if not response.content.startswith(b'<'):
                        # Convert to streaming response
                        print(f"   ✅ Got binary content, converting to stream...")
                        class StreamResponse:
                            def __init__(self, content):
                                self.content = content
                                self.status_code = 200
                            def iter_content(self, chunk_size=8192):
                                for i in range(0, len(self.content), chunk_size):
                                    yield self.content[i:i+chunk_size]
                        response = StreamResponse(response.content)
        else:
            print(f"   ❌ Could not find confirmation token in HTML")
            return False
    
    # Validate final response
    if hasattr(response, 'status_code') and response.status_code != 200:
        print(f"   ❌ HTTP Error {response.status_code}")
        return False
    
    # Download the file
    print(f"   📥 Writing to {file_path}...")
    total_size = 0
    
    try:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
                    # Progress for large files
                    if total_size % (200 * 1024 * 1024) == 0:  # Every 200MB
                        print(f"   📊 Progress: {total_size / (1024*1024):.0f} MB downloaded...")
    except Exception as e:
        print(f"   ❌ Error during download: {e}")
        return False
    
    # Verify download
    file_size = os.path.getsize(file_path)
    print(f"   ✅ Download complete: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
    
    # Quick validation for pickle files
    if file_path.endswith('.pkl'):
        try:
            with open(file_path, 'rb') as f:
                header = f.read(10)
                if header.startswith(b'\x80'):
                    print(f"   ✅ Valid pickle protocol detected")
                    return True
                elif header.startswith(b'<'):
                    print(f"   ❌ Downloaded HTML instead of pickle file")
                    os.remove(file_path)  # Remove corrupted file
                    return False
                else:
                    print(f"   ⚠️  Unknown file format: {header}")
                    return False
        except Exception as e:
            print(f"   ❌ Error validating pickle file: {e}")
            return False
    
    return True

def download_large_files():
    """Download large files from cloud storage if they don't exist locally"""
    
    # URLs for your large files (from environment variables or hardcoded)
    LARGE_FILES = {
        'Datasets/deliveries_2008-2024.csv': os.getenv('DELIVERIES_CSV_URL', 'https://drive.google.com/file/d/19SssaOPuPgTSD4sHpLPRip7QmFX8UDDz/view?usp=sharing'),
        'Model/predict_ipl_score_compressed.pkl.bz2': os.getenv('SCORE_MODEL_COMPRESSED_URL', 'https://drive.google.com/file/d/1I8bziax2KrA8q43awZ4nJ_mkw-yIFc1P/view?usp=sharing'),
        'Model/winner_prediction_model.pkl': os.getenv('WINNER_MODEL_URL', 'https://drive.google.com/file/d/WINNER_MODEL_URL_HERE/view?usp=sharing'),
    }
    
    for file_path, share_url in LARGE_FILES.items():
        if not os.path.exists(file_path):
            if not share_url or share_url.strip() == '':
                print(f"⚠️ No URL provided for {file_path}, skipping...")
                continue
                
            print(f"Downloading {file_path}...")
            
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to direct download URL
            download_url = get_google_drive_download_url(share_url)
            
            # Download file using Google Drive handler
            success = download_from_google_drive(download_url, file_path)
            
            if success:
                print(f"✅ Downloaded {file_path}")
                
                # Special handling for compressed model - decompress and save original
                if file_path.endswith('.bz2') and 'score' in file_path.lower():
                    print(f"📦 Decompressing model: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
                    decompress_score_model(file_path)
            else:
                print(f"❌ Failed to download {file_path}")
        else:
            print(f"✅ {file_path} already exists")

if __name__ == "__main__":
    download_large_files()
