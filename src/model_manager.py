from environments import demucs_model_path, config_path, remote_demucs_models, so_vits_model_path, remote_so_vits_models
from utilities import *


def get_demucs_models(update=False):
	"""
	get demucs demo_assets from config.json
	"""
	print("downloading demucs demo_assets")
	print(
		f"Tip: you may put your own demucs model to {demucs_model_path} or add customized model url in {config_path}")
	for i in remote_demucs_models:
		for j in i:
			if j.split('/')[-1] in [k.name for k in demucs_model_path.iterdir()] and not update:
				print(f"{j.split('/')[-1]} already exists, skipping")
				continue
			content = requests.get(j, stream=True)
			length = int(content.headers["content-length"])
			print(f"Downloading {j.split('/')[-1]} ({length} bytes)")
			with open(demucs_model_path.joinpath(j.split("/")[-1]), "wb") as f:
				f.write(content.content)
			print(f"{j} downloaded")


def get_so_vits_models(update=False):
	print(f"{'downloading' if not update else 'update'} so-vits-svc demo_assets\n")
	print(
		f"Tip: you may put your own so-vits model to {so_vits_model_path}(model_name) or add customized model url in {config_path}\n")
	for name, value in zip(remote_so_vits_models.keys(), remote_so_vits_models.values()):
		download_path = Path(so_vits_model_path.joinpath(name))
		if name in [i.stem for i in so_vits_model_path.iterdir()] and not update:
			print(f"{name} already exists, skipping")
			continue
		get_so_vits_model(name, download_path, value["link"])


def get_so_vits_model(model_name, download_path:Path, link, update_cache=True):
	"""
	get so-vits-svc demo_assets from sources.json
	"""
	if link.startswith("https://cowtransfer.com/"):
		return get_cow_transfer_model(model_name, link, download_path)
	elif link.startswith("https://huggingface.co/"):
		return get_hugging_face_model(model_name, link, download_path, update_cache)

