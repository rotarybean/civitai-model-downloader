# civitai-model-downloader
A Python script for easy CivitAI model downloads using a CivitAI API key

# Description:
civitai_downloader is a python script for easy model downloads - it automatically places your model in the correct folder based upon the model type you select.  

# Reason for script:
While I'm away from my homelab (where my AI server resides) it's rather annoying and tedious to download a model to one machine then WinSCP or FTP the file to the AI server.  Using wget is. . . spotty at best.  For that reason, I wrote this script so I can access the CLI from anywhere (via VPN) and download *directly* to the server. 

# Directions for one-time-Setup:
1. Place the `civitai_downloader.py` file in your home directory.
2. Run `chmod +x ~/civitai_downloader.py` - this will make the downloader executable.
3. OPTIONAL: Create a symbolic link for easier access by running `sudo ln -s ~/civitai_downloader.py /usr/local/bin/civitai-dl`
4. Run the downloader by running `./civitai_downloader.py` or simply `civitai-dl` if you set up the symlink.
5. On first run, you'll be prompted to set up your CivitAI API key.  In CivitAI, go to your account settings and scroll down to the 'API Keys' section - about third up from the bottom.
6. Create a new API key and name it what you like - WARNING: you won't see that key again on CivitAI's site, so store it somewhere safe.
7. Paste or manually type the API key into the prompt in the CivitAI Downloader.  It'll store it for future use if you choose.
8. Setup is done!

# Usage:
1. After initial setup is done, you're ready to download models.  Select your model type and press 'Enter'.
2. Enter the CivitAI Model ID - on the right-hand side of the model page (in your browser), in the Details panel, you'll see a row labeled 'AIR'.  The **second** blue block of numbers is the Model ID.
3. The downloader will attempt to retrieve the model info from two CivitAI sources: https://civitai.com/api/v1/models/[MODEL_ID] and https://civitai.com/api/download/models/[MODEL_ID]
4. Successful model info retreival is indicated by ✅ Model found: [MODEL_ID].
5. The script will suggest a filename.  I **highly** recommend naming it something memorable.  model_123456.safetensors isn't very descriptive.  Change it before downloading.
6. Press y and 'Enter' at "Start download? (y/n):"
7. Watch the progress bar fill!  You've downloaded your selected model, and it's automatically placed in the correct folder based upon the model type you selected at the beginning.

Happy Diffusing!

-@rotarybean

