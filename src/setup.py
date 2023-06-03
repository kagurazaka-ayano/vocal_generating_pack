from environments import *
from json import loads
from gzip import GzipFile
from zipfile import ZipFile
import tarfile
import platform
from py7zr import SevenZipFile
from rarfile import RarFile
from filetype import guess_extension
import requests
import huggingface_hub
import re
from shutil import copytree, rmtree

delim = "----------------------------------------"

archive_supported = ("gz", "gzip", "zip", "tar", "rar", "7z")


def get_demucs_models():
	"""
	get demucs models from config.json
	"""
	print("downloading demucs models")
	print(f"Tip: you may put your own demucs model to {demucs_model_path} or add customized model url in {config_path}")
	for i in remote_demucs_models:
		if i in demucs_model_path.iterdir():
			print(f"{i.split('/')[-1]} already exists, skipping")
			continue
		content = requests.get(i, stream=True)
		length = int(content.headers["content-length"])
		print(f"Downloading {i.split('/')[-1]} ({length} bytes)")
		with open(demucs_model_path.joinpath(i.split("/")[-1]), "wb") as f:
			f.write(content.content)
	print(f"demucs models {remote_demucs_models} downloaded")


print(delim)


def extract_gz(path: Path) -> Path:
	file_name = path.stem
	with open(path, "rb") as f:
		with GzipFile(fileobj=f) as g:
			with open(str(path.parent) + file_name + guess_extension(str(path)).lower(), "wb+") as f:
				f.write(g.read())
	return Path(file_name + guess_extension(str(path))).resolve()


def extract_zip(path: Path):
	with ZipFile(path, "r") as z:
		z.extractall(path.parent)


def extract_tar(path: Path):
	with tarfile.open(path, "r") as t:
		t.extractall(path.parent)


def extract_rar(path: Path):
	with RarFile(path, "r") as r:
		r.extractall(path.parent)


def extract_7z(path: Path):
	with SevenZipFile(path, "r") as s:
		s.extractall(path.parent)


def get_cow_transfer_model(name, value, download_path):
	cow_transfer_metadata = lambda link: requests.get(
		"https://api.kit9.cn/api/nainiu_netdisc/api.php?link=" + link).json()
	meta = cow_transfer_metadata(value["link"])
	if meta["code"] != 200:
		print(f"cannot fetch metadata of {name}, skipping")
		return
	print(f"Downloading {name} ({meta['data']['file_size']})")
	content = requests.get(meta["data"]["download_link"], stream=True)
	local_path = Path(download_path.joinpath(meta["data"]["file_name"] + "." + meta["data"]["file_format"]))
	with open(local_path, "wb") as f:
		f.write(content.content)
	print(f"Downloaded {name}")
	print(f"Extracting {name}")
	filetype = guess_extension(str(local_path))
	if filetype not in archive_supported:
		print(f"cannot extract {name}, supported file format: {archive_supported}, skipping")
		return
	match filetype:
		case "gz", "gzip":
			extracted_path = extract_gz(local_path)
			if extracted_path.suffix == ".tar":
				extract_tar(extracted_path)
		case "zip":
			extract_zip(local_path)
		case "tar":
			extract_tar(local_path)
		case "rar":
			extract_rar(local_path)
		case "7z":
			extract_7z(local_path)
		case _:
			pass

def extract_dir(path:Path) -> list:
	copied = []

	for i in path.iterdir():
		if i.is_dir():
			print(f"extracting {path.joinpath(i)}")
			if i in path.parent.iterdir():
				print("duplicated folder, skipping")
				continue
			print(Path(str(path) + i.stem + "/"))
			copytree(i, Path(str(path) + i.stem + "/"))
			copied.append(i.stem)
	rmtree(path)
	return copied


def add_so_vits_model_entry(entry, value):
	config["remote_resources"]["so-vits-svc"].update({entry: value})
	with open(config_path, "w") as f:
		f.write(json.dumps(config, indent=4))

def remove_so_vits_model_entry(entry):
	config["remote_resources"]["so-vits-svc"].pop(entry)
	with open(config_path, "w") as f:
		f.write(json.dumps(config, indent=4))


def get_hugging_face_model(name, value):
	pattern = r"https:\/\/huggingface\.co\/(.+)\/.+\/.+"
	assert re.match(pattern, value["link"]), "invalid huggingface model url"
	repo_id = re.match(pattern, value["link"]).group(1)
	huggingface_hub.snapshot_download(repo_id, allow_patterns=["*.pt", "*.pth", "*.json"], local_dir=so_vits_model_path.joinpath(name), force_download=True)

	for i in so_vits_model_path.joinpath(name).iterdir():
		if i.is_dir():
			extract_dir(i)


def get_so_vits_models(update=False):
	print(f"{'downloading' if not update else 'update'} so-vits-svc models\n")
	print(
		f"Tip: you may put your own so-vits model to {so_vits_model_path}(model_name) or add customized model url in {config_path}\n")
	for name, value in zip(remote_so_vits_models.keys(), remote_so_vits_models.values()):
		download_path = Path(so_vits_model_path.joinpath(name))
		print(name, so_vits_model_path.iterdir())
		if name in [i.stem for i in so_vits_model_path.iterdir()] and not update:
			print(f"{name} already exists, skipping")
			continue
		download_path.mkdir(parents=True, exist_ok=True)
		if value["link"].startswith("https://cowtransfer.com/"):
			get_cow_transfer_model(name, value, download_path)
		elif value["link"].startswith("https://huggingface.co/"):
			try:
				get_hugging_face_model(name, value)
			except AssertionError as e:
				print(e)
				continue


get_so_vits_models()