#!/usr/bin/env python3
#CivitAI model downloader for ComfyUI
#by @rotarybean
#v1.0

import os
import sys
import requests
import json
from pathlib import Path
from urllib.parse import urlparse
import argparse

# Configuration
COMFYUI_BASE = Path.home() / "ComfyUI" / "models"
API_BASE_URL = "https://civitai.com/api/v1/models"

# Model type mappings to directories
MODEL_DIRS = {
    "1": ("checkpoints", "Checkpoint models"),
    "2": ("vae", "VAE models"),
    "3": ("loras", "LoRA models"),
    "4": ("controlnet", "ControlNet models"),
    "5": ("clip_vision", "CLIP Vision models"),
    "6": ("embeddings", "Embedding/textual inversion models"),
    "7": ("upscale_models", "Upscale models"),
    "8": ("clip", "CLIP models"),
    "9": ("unet", "UNet models"),
    "10": ("insightface", "InsightFace models"),
    "11": ("animatediff_models", "AnimateDiff models"),
}

def get_api_key():
    api_key = os.environ.get("CIVITAI_API_KEY")
    
    if not api_key:
        config_file = Path.home() / ".civitai_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
            except:
                pass
    
    if not api_key:
        print("\n⚠️  No API key found!")
        print("You can:")
        print("1. Set environment variable: export CIVITAI_API_KEY='your_key'")
        print("2. Create ~/.civitai_config.json with: {\"api_key\": \"your_key\"}")
        print("3. Get your API key from: https://civitai.com/user/account")
        
        choice = input("\nDo you want to enter API key now? (y/n): ").lower()
        if choice == 'y':
            api_key = input("Enter your CivitAI API key: ").strip()
            if api_key:
                save_choice = input("Save API key to config file? (y/n): ").lower()
                if save_choice == 'y':
                    config_file = Path.home() / ".civitai_config.json"
                    with open(config_file, 'w') as f:
                        json.dump({"api_key": api_key}, f)
                    os.chmod(config_file, 0o600)  # Secure permissions
                    print(f"API key saved to {config_file}")
        else:
            print("Continuing without API key (some models may fail to download)")
    
    return api_key

def get_model_type():
    print("\n" + "="*50)
    print("SELECT MODEL TYPE")
    print("="*50)
    
    for key, (dir_name, description) in MODEL_DIRS.items():
        print(f"{key}: {description}")
    
    while True:
        choice = input("\nEnter number (1-11): ").strip()
        if choice in MODEL_DIRS:
            dir_name, description = MODEL_DIRS[choice]
            return dir_name, description
        print("❌ Invalid choice. Please enter a number between 1 and 11.")

def get_model_info(model_id, api_key=None):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        response = requests.get(f"{API_BASE_URL}/{model_id}", headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        model_name = data.get("name", "unknown_model")
        model_type = data.get("type", "").lower()
        
        # Get the latest model version
        versions = data.get("modelVersions", [])
        if versions:
            latest = versions[0]
            download_url = latest.get("downloadUrl")
            files = latest.get("files", [])
            
            if files:
                file_info = files[0]
                original_filename = file_info.get("name", f"{model_name}.safetensors")
                download_url = file_info.get("downloadUrl", download_url)
            else:
                original_filename = f"{model_name}.safetensors"
        else:
            download_url = None
            original_filename = f"{model_name}.safetensors"
        
        return {
            "name": model_name,
            "type": model_type,
            "download_url": download_url,
            "original_filename": original_filename,
            "data": data
        }
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching model info: {e}")
        return None

def download_file(url, filepath, api_key=None):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        # First, get file size for progress tracking
        with requests.get(url, headers=headers, stream=True, timeout=30) as response:
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            
            print(f"📥 Downloading to: {filepath}")
            print(f"📦 File size: {total_size / (1024*1024):.2f} MB")
            
            downloaded = 0
            chunk_size = 8192
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            bar_length = 40
                            filled_length = int(bar_length * downloaded // total_size)
                            bar = '█' * filled_length + '░' * (bar_length - filled_length)
                            
                            # Clear line and show progress
                            sys.stdout.write(f'\r  [{bar}] {percent:.1f}% ({downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB)')
                            sys.stdout.flush()
            
            print()  # New line after progress bar
            return True
            
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        # Clean up partially downloaded file
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def get_filename_suggestion(original_name, model_type, model_name):
    # Clean up the original name
    clean_name = original_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    
    # Add model name if not already in filename
    if model_name.lower() not in clean_name.lower():
        base_name = Path(clean_name).stem
        extension = Path(clean_name).suffix
        clean_name = f"{model_name}_{base_name}{extension}"
    
    return clean_name

def main():
    print("\n" + "="*60)
    print("🎨 CIVITAI MODEL DOWNLOADER FOR COMFYUI")
    print("="*60)
    
    # Get API key
    api_key = get_api_key()
    
    # Get model type
    model_dir, model_type_desc = get_model_type()
    target_dir = COMFYUI_BASE / model_dir
    
    # Create directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Models will be saved to: {target_dir}")
    
    # Get model ID
    while True:
        model_id = input("\n🔢 Enter CivitAI Model ID (or 'q' to quit): ").strip()
        if model_id.lower() == 'q':
            print("👋 Goodbye!")
            sys.exit(0)
        
        if model_id.isdigit():
            break
        print("❌ Please enter a numeric model ID")
    
    # Fetch model information
    print(f"\n⏳ Fetching model information for ID: {model_id}...")
    model_info = get_model_info(model_id, api_key)
    
    if not model_info or not model_info.get("download_url"):
        print("❌ Could not retrieve model information or download URL")
        
        # Try direct download as fallback
        download_url = f"https://civitai.com/api/download/models/{model_id}"
        print(f"\n⚠️  Trying direct download URL: {download_url}")
        model_info = {
            "name": f"model_{model_id}",
            "original_filename": f"model_{model_id}.safetensors",
            "download_url": download_url
        }
    
    print(f"\n✅ Model found: {model_info['name']}")
    print(f"📄 Original filename: {model_info['original_filename']}")
    
    # Ask for filename
    suggested_name = get_filename_suggestion(
        model_info['original_filename'],
        model_type_desc,
        model_info['name']
    )
    
    print(f"\n💡 Suggested filename: {suggested_name}")
    
    while True:
        choice = input("Use suggested name? (y/n): ").lower().strip()
        
        if choice == 'y':
            filename = suggested_name
            break
        elif choice == 'n':
            custom_name = input("Enter custom filename (include extension, e.g., .safetensors): ").strip()
            if custom_name:
                filename = custom_name
                break
            else:
                print("❌ Filename cannot be empty")
        else:
            print("❌ Please enter 'y' or 'n'")
    
    # Determine full filepath
    filepath = target_dir / filename
    
    # Check if file already exists
    if filepath.exists():
        print(f"\n⚠️  File already exists: {filepath}")
        overwrite = input("Overwrite? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("❌ Download cancelled")
            sys.exit(0)
    
    # Confirm download
    print(f"\n📋 Download Summary:")
    print(f"   Model: {model_info['name']}")
    print(f"   Type: {model_type_desc}")
    print(f"   Filename: {filename}")
    print(f"   Location: {target_dir}")
    
    confirm = input("\nStart download? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ Download cancelled")
        sys.exit(0)
    
    # Download the file
    print(f"\n🚀 Starting download...")
    success = download_file(model_info['download_url'], filepath, api_key)
    
    if success:
        # Verify file was downloaded
        file_size = os.path.getsize(filepath) / (1024*1024)
        print(f"\n✅ Download complete!")
        print(f"   📁 Saved to: {filepath}")
        print(f"   📊 Size: {file_size:.2f} MB")
        
        # Set appropriate permissions
        os.chmod(filepath, 0o644)
    else:
        print("\n❌ Download failed!")
        sys.exit(1)

if __name__ == "__main__":
    # Parse command line arguments for non-interactive use
    parser = argparse.ArgumentParser(description="Download CivitAI models for ComfyUI")
    parser.add_argument("--model-id", type=int, help="CivitAI model ID")
    parser.add_argument("--type", choices=[dir_name for dir_name, _ in MODEL_DIRS.values()], 
                       help="Model type (checkpoints, vae, loras, etc.)")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--api-key", help="CivitAI API key")
    parser.add_argument("--list-types", action="store_true", help="List available model types")
    
    args = parser.parse_args()
    
    if args.list_types:
        print("\nAvailable model types:")
        for key, (dir_name, description) in MODEL_DIRS.items():
            print(f"  {dir_name:<20} - {description}")
        sys.exit(0)
    
    main()