from requests import get
from pathlib import Path
from zipfile import ZipFile
import tarfile
from py7zr import SevenZipFile
from rarfile import RarFile
from gzip import GzipFile
from filetype import guess_extension
from shutil import copytree, rmtree
import re
import huggingface_hub
import requests
from environments import so_vits_model_path
import shutil


def cow_transfer_metadata(link: str) -> dict:
	return get("https://api.kit9.cn/api/nainiu_netdisc/api.php?link=" + link).json()


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


def extract_gz(path: Path) -> Path:
	file_name = path.stem
	with open(path, "rb") as f:
		with GzipFile(fileobj=f) as g:
			with open(str(path.parent) + file_name + guess_extension(str(path)).lower(), "wb+") as f:
				f.write(g.read())
	return Path(file_name + guess_extension(str(path))).resolve()


def move_file(dir: Path, root_dir: Path):
	for i in dir.iterdir():
		if i.is_dir():
			move_file(i, root_dir)
		elif i.name.rsplit('.')[-1] == "pth":
			shutil.copytree(dir, root_dir / i.parent.name, dirs_exist_ok=True)


def get_cow_transfer_model(name, value, download_path):
	download_path.mkdir(parents=True, exist_ok=True)
	archive_supported = ("gz", "gzip", "zip", "tar", "rar", "7z")
	meta = cow_transfer_metadata(value["link"])
	if meta["code"] != 200:
		print(f"cannot fetch metadata of {name}, skipping")
		return {}
	print(f"Downloading {name} ({meta['data']['file_size']})")
	content = requests.get(meta["data"]["download_link"], stream=True)
	local_path = Path(download_path.joinpath(meta["data"]["file_name"] + "." + meta["data"]["file_format"]))
	with open(local_path, "wb") as f:
		f.write(content.content)
	print(f"Downloaded {name}")
	print(f"Extracting {name}")
	filetype = guess_extension(str(local_path))
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
			print(f"cannot extract {name}, supported file format: {archive_supported}, skipping")
			return {}
	print(f"Extracted {name}")


def get_hugging_face_model(name, value, download_path, update_cache=True) -> dict:
	download_path.mkdir(parents=True, exist_ok=True)
	pattern = r"https:\/\/huggingface\.co\/([-\w.]+)\/([\w.-]+)\/?"
	match = re.match(pattern, value)
	repo_id = match.group(1) + "/"
	repo_id += match.group(2).strip("/")
	local_cache_path = Path(huggingface_hub.snapshot_download(repo_id, allow_patterns=["*.pt", "*.pth", "*.json"], force_download=update_cache))
	move_file(local_cache_path, download_path)
	return {download_path.joinpath(local_cache_path.name).stem: download_path.joinpath(local_cache_path.name).resolve()}

def get_avaliable_so_vits_models_dict() -> dict:
	models = {}
	for i in so_vits_model_path.iterdir():
		if i.is_dir():
			models[i.name] = i
	return models


def export_sources():
	raise NotImplementedError


def remove_model(model_name, from_source=False):
	raise NotImplementedError


def add_source(url, model_name=None, download=False):
	raise NotImplementedError


def download_from_source(source_name):
	raise NotImplementedError
