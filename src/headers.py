import binascii
import struct
import base64
import json
import os
from Crypto.Cipher import AES
from thirdparties.demucs import separate
from torch.cuda import is_available
from thirdparties.so_vits_svc_fork.inference.main import infer
from pathlib import Path
from pydub import AudioSegment



# env variables
config_path = Path("config.json").resolve()
config = json.load(config_path.open("r"))
demucs_model_path = Path(config["model_root"]["demucs"])
so_vits_model_path = Path(config["model_root"]["so_vits"])
demucs_preset_path = Path(config["preset_root"]["demucs"])
so_vits_preset_path = Path(config["preset_root"]["so_vits"])

demucs_model_path.mkdir(parents=True, exist_ok=True)
so_vits_model_path.mkdir(parents=True, exist_ok=True)
demucs_preset_path.mkdir(parents=True, exist_ok=True)
so_vits_preset_path.mkdir(parents=True, exist_ok=True)

