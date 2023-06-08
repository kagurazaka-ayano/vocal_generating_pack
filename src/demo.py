import os
from functions import separate_vocal, apply_so_vits, fuse_vocal_and_instrumental, convert_ncm, Path
from model_manager import get_so_vits_model, get_demucs_models
from environments import remote_so_vits_models, so_vits_model_path, config
from utilities import get_avaliable_so_vits_models_dict

model_path = Path("demo_assets/models/").resolve()
get_demucs_models()
get_so_vits_model("genshin", so_vits_model_path, remote_so_vits_models["genshin"]["link"], update_cache=False)
path = Path(config["output"]) / Path("demo")
converted_path = convert_ncm("demo_assets/demo.wav", Path(path.stem)/Path("./converted/"))
print("converted")
separated_path = separate_vocal(converted_path, Path(path.stem)/Path("./separated/"), jobs=os.cpu_count() - 1)
print("separated")
models = get_avaliable_so_vits_models_dict()
inferred_path = apply_so_vits(input_vocal=Path(separated_path["vocal"]),
							  output_path=Path(path.stem) / Path("./inferred/"), model_path=Path(
		models["nahida-jp"].joinpath("nahida_jp_G_40000.pth")
	), config_file_path=Path(
		models["nahida-jp"].joinpath("nahida.json")
	), speaker="nahida", cluster=Path(
		models["nahida-jp"].joinpath("nahida_jp_kmeans_10000.pt")
	), auto_predict_f0=False)
print("inferred")
print(fuse_vocal_and_instrumental(
	vocal_path=inferred_path,
	instrumental_path=separated_path["instrumental"],
	output_path=Path(path.stem)/Path("./counterfeited"),
	speaker="nahida"
))
