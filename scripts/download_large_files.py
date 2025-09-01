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
        try:
            file_id = share_url.split('/file/d/')[1].split('/')[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        except IndexError:
            print(f"⚠️ Could not extract file ID from URL: {share_url}")
            return share_url
    return share_url


def download_from_google_drive(url, file_path):
    """Download file from Google Drive handling virus scan warning for large files"""
    try:
        print(f"📥 Starting download: {file_path}")
        
        session = requests.Session()
        
        # First request to get the file
        response = session.get(url, stream=True)
        
        # Check if this is a virus scan warning page
        if 'virus scan warning' in response.text.lower() or 'download_warning' in response.text:
            print("⚠️ Detected virus scan warning, extracting confirmation token...")
            
            # Extract the confirmation token
            token_match = re.search(r'name="confirm" value="([^"]+)"', response.text)
            if token_match:
                confirm_token = token_match.group(1)
                print(f"🔑 Found confirmation token: {confirm_token[:10]}...")
                
                # Make request with confirmation token
                confirm_url = f"{url}&confirm={confirm_token}"
                response = session.get(confirm_url, stream=True)
            else:
                print("❌ Could not find confirmation token")
                return False
        
        # Check if response is successful
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            print(f"📦 File size: {total_size / (1024*1024):.1f} MB")
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress for large files
                        if total_size > 0 and downloaded_size % (1024*1024*10) == 0:  # Every 10MB
                            progress = (downloaded_size / total_size) * 100
                            print(f"⬇️ Progress: {progress:.1f}% ({downloaded_size / (1024*1024):.1f} MB)")
            
            print(f"✅ Download completed: {downloaded_size / (1024*1024):.1f} MB")
            return True
        else:
            print(f"❌ Download failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return False


def download_large_files():
    """Download all required large files for the application."""
    print("🚀 Starting large file download process...")
    
    # URLs for your large files (from environment variables or hardcoded)
    LARGE_FILES = {
        'Datasets/deliveries_2008-2024.csv': os.getenv('DELIVERIES_CSV_URL', 'https://drive.google.com/file/d/19SssaOPuPgTSD4sHpLPRip7QmFX8UDDz/view?usp=sharing'),
        'Model/predict_ipl_score_compressed.pkl.bz2': os.getenv('SCORE_MODEL_COMPRESSED_URL', ''),
        'Model/winner_prediction_model.pkl': os.getenv('WINNER_MODEL_URL', ''),
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
    
    print("🎉 Large file download process completed!")


if __name__ == "__main__":
    download_large_files()
