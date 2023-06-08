from pathlib import Path
import json

# env variables
config_path = Path("config.json").resolve()
config = json.load(open(config_path, "r"))
sources = json.load(open(config["sources"], "r"))
demucs_model_path = Path(config["model_root"]["demucs"]).resolve()
so_vits_model_path = Path(config["model_root"]["so-vits"]).resolve()
demucs_preset_path = Path(config["preset_root"]["demucs"]).resolve()
so_vits_preset_path = Path(config["preset_root"]["so-vits"]).resolve()

# training path
dataset_path = Path(config["dataset"]).resolve()

# model path
demucs_model_path.mkdir(parents=True, exist_ok=True)
so_vits_model_path.mkdir(parents=True, exist_ok=True)
demucs_preset_path.mkdir(parents=True, exist_ok=True)
so_vits_preset_path.mkdir(parents=True, exist_ok=True)



# remote paths
remote_demucs_models = sources["demucs"]["model"].values()
remote_so_vits_models = sources["so-vits"]["model"]



