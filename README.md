# Running a Django Server

To run and host the **django-sopila-master** project, you’ll follow the highly specific setup guide and the standard workflow and path for a Django application. Before hosting, ensure the app runs on your machine.

## Clone the Repository

Open your terminal and run the following commands to clone the GitHub repository:
```bash
git clone https://github.com/LucijaZuzic/django-sopila.git
cd django-sopila-master
```

## Install an Older Version of Python

To run this project exactly as it was intended without rewriting the code, you should create a virtual environment using **Python 3.7**.

To download **Python 3.7**, the most stable "old" version that still works on most Windows systems, via the command line, the easiest way is to use the **Python Launcher**.

If you already have a modern version of Python installed, you likely have the **Python Launcher** (`py`).

On Windows, open PowerShell and run this to download the Python 3.7.9 installer:
```powershell
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe" -OutFile "python37_installer.exe"
```

To run the installer silently in the background on Windows, use:
```powershell
.\python37_installer.exe /quiet InstallAllUsers=1 PrependPath=1
```

*Note: You may need to restart your terminal after this.*

## Create a Virtual Environment

This keeps the project's dependencies isolated from your system.

You can now target a specific version of Python to create your virtual environment for the project:
```bash
# Ensure you are using the 3.7 executable
py -3.7 -m venv venvSopila
```

## Activate a Virtual Environment

Depending on your operating system and terminal (shell), you will need to run one of the following:
```bash
# On Windows (Git Bash (MINGW64)):
source venvSopila/Scripts/activate
# On Windows (PowerShell and others):
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Install Dependencies

Check whether a `requirements.txt` file exists. If so, run:
```bash
pip install -r requirements.txt
```

*Note: The `pkg-resources==0.0.0` line in the `requirements.txt` file will cause errors and must be removed if present, and `scikit-learn==0.20.1` must be specified instead of `0.20.3`.*

## Initialize the Database

Django needs to create its internal tables:
```bash
python manage.py migrate
```

## Download FFmpeg

FFmpeg is used in this project to manipulate audio files.

Go to `https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z`.

Download the `zip` file containing the FFmpeg packages and compiled executables, ready to use, instead of the source code.

Extract the files into a directory named `ffmpeg`.

Structure the directories so that `ffmpeg` is at the same level as `manage.py`.

This ensures that the code can access `ffmpeg/bin/ffmpeg.exe`.

It is recommended to add the location of `ffmpeg/bin` to the PATH variable of your operating system.

## Download LilyPond

LilyPond is used in this project to produce the sheet music as a `pdf` file.

Go to `https://gitlab.com/lilypond/lilypond/-/releases/v2.24.4/downloads/lilypond-2.24.4-mingw-x86_64.zip`.

Download the `zip` file containing the LilyPond packages and the compiled executables, ready to run, instead of the source code.

Extract the files into a directory named `lilypond`.

Structure the directories so that `lilypond` is at the same level as `manage.py`.

This ensures that the code can access `lilypond/bin/lilypond.exe`.

It is recommended to add the location ofs `lilypond/bin` to the PATH variable of your operating system.

## Copy the Trained Model

Follow the instruction from `https://github.com/LucijaZuzic/sopila-transcriptor.git` to retrain the model.

The trained model with the `joblib` extension can also be downloaded from `https://drive.google.com/file/d/1HIAFEaunJomerYyrKrfPycj9OpVPSkuP/view?usp=sharing`.

## Set the Project Location

In `sheet_generator\apps.py`, write `APP_DIR = "path\local"` to include the absolute path to the directory where the `apps.py` script is located.

## Machine Learning

The transcription is done using the Random Forest (RF) model and the Discrete Fourier Transform (DFT).

*   **Model Parameters:** The model uses `scikit-learn` and default parameters, unless stated otherwise.
    *   **n_estimators:** 900
    *   **criterion:** Gini
    *   **min_samples_split:** 2
    *   **max_samples_leaf:** 1
    *   **max_features:** auto**
    *   **max_depth:** 80
    *   **bootstrap:** false

## Run the Development Server

If you run runserver without extra info, it defaults to 127.0.0.1:8000.

To run the server on all interfaces on port 8000, you need to configure it to listen on the entire network using 0.0.0.0, as shown:
```bash
python manage.py runserver 0.0.0.0:8000
```

You can now view the server at `http://127.0.0.1:8000/`.

*Note: You must make sure the directories `data`, `sheet_generator\raw_predictions` and `sheet_generator\pdf` are created and present alongside `manage.py` before running the server, as these are used for storing the audio fiels, model predictions and musical note files, respectively.*

*Note: You will see a generic 404 Not Found message since this is a backend server with no visual interface.*

## Configure Tunneling

To enable people on a different network (or anywhere in the world) to access your server, you need to move from local to public hosting.

The "tunneling" method using ngrok is the fastest for testing and allows you to show your work right away without setting up a permanent server.

It creates a secure tunnel from the public internet to your server.

Download ngrok (`https://ngrok.com/download/windows?tab=install`) and register, then enter your assigned authtoken in PowerShell:
```bash
ngrok config add-authtoken <token>
```

*Note: Since your Internet Service Provider (ISP) might flag the `dev` domain, and users cannot be expected to use a Virtual Private Network (VPN) or modify the Domain Name System (DNS), it is better to purchase a commercial domain, even if mobile users on mobile data instead of Wi-Fi might avoid this issue.*

Download Cloudflared to link to this commercial domain:
```bash
winget install --id Cloudflare.cloudflared
```

Then run a command to open the browser and register:
```bash
cloudflared tunnel login
```

To start the Cloudflared tunnel, run the following commands to connect with a commercial domain in the second line:
```bash
cloudflared tunnel create my-sopila
cloudflared tunnel route dns my-sopila sopila-audio.com
cloudflared tunnel run --url http://localhost:8000 my-sopila
```

## Start the Tunnel

After obtaining a ngrok authtoken and signing up for a free ngrok account, you can start the ngrok tunnel.

To forward to the Hypertext Transfer Protocol (HTTP), use the scheme flag as follows, which instructs ngrok to forward to HTTP.

The endpoint produced will be HTTP, not Hypertext Transfer Protocol Secure (HTTPS), avoiding a Secure Socket Layer (SSL) certificate error:
```bash
ngrok http --scheme=http 8000 --host-header=localhost:8000
```

The resulting link will be displayed in the terminal, such as `https://sopila-audio.com`.

Anyone in the world can visit the address to view your project.

## Configure the Mobile Application

Be sure to use the context menu in the top-right corner of the mobile application.

Select the `Edit server IP address` option in the drop-down.

This will save your ngrok link as the address for all requests.

*Note: You include either an adress and a port number (X.X.X.X:port) or the link withot `https://` or `http://`.*