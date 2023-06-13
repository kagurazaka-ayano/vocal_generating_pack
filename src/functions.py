import binascii
import struct
import base64
import os
from Crypto.Cipher import AES
from thirdparties.demucs import separate
from torch.cuda import is_available
from thirdparties.so_vits_svc_fork.inference.main import infer
from pydub import AudioSegment
from classes import DemucsGenerateParam
from environment import *


def convert_ncm(file_path, output_path) -> Path:
    """
    convert NetEase ncm file to plain sound file
    :param file_path: the path of the ncm file
    :param output_path: the path of the output directory
    :return: the path of the output file
    """
    if os.path.splitext(file_path)[-1] != '.ncm':
        return Path(file_path)
    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s: s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]
    f = open(file_path, "rb")
    header = f.read(8)
    assert binascii.b2a_hex(header) == b'4354454e4644414d'
    f.seek(2,1)
    key_length = f.read(4)
    key_length = struct.unpack("<I", bytes(key_length))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range(0, len(key_data_array)):
        key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)
    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_length:
            key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c
    meta_length = f.read(4)
    meta_length = struct.unpack("<I", bytes(meta_length))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0, len(meta_data_array)):
        meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])
    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode("utf-8")[6:]
    meta_data = json.loads(meta_data)
    crc32 = f.read(4)
    crc32 = struct.unpack("<I", bytes(crc32))[0]
    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack('<I', bytes(image_size))[0]
    image_data = f.read(image_size)
    file_name = f.name.split("/")[-1].split(".ncm")[0] + "." + meta_data["format"]
    Path(output_path).mkdir(parents=True, exist_ok=True)
    m = open(os.path.join(output_path, file_name), "wb")
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1, chunk_length+1):
            j = i & 0xff
            chunk[i-1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
        m.write(chunk)
    m.close()
    f.close()
    return Path(os.path.join(output_path, file_name))


def separate_vocal(
        track_path: Path,
        output_path: Path,
        save_to_config=False,
        name="",
        device="cpu" if not is_available() else "cuda",
        wav_store_method="float32",
        split_mode="segment",
        split_num=5,
        clip_mode="clamp",
        jobs=os.cpu_count(),
        repo=r"../files/models/demucs/hdemucs_mmi",
        extension="wav"
) -> dict[str, Path]:
    """
    separate the music into vocals and instruments
    :param track_path: the path of the track
    :param output_path: the path of the output directory
    :param device: the device to use, cuda or cpu, default is cpu
    :param wav_store_method: the method to store the wav file, float32 or int16, default is
    :param split_mode: the method to split the track, --segment or --no-split
    :param split_num: the number of segments to split the track, only works when split_mode is --segment
    :param clip_mode: the method to clip the track, rescale or clamp, default is rescale
    :param jobs: the number of jobs to use, default is use all the cpu logic core if in cpu mode
    :param repo: the repo to download the model, default is https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/
    :param save_to_config: whether save the config of this function to a file
    :param name: the name of the config file
    :param extension: extension of output file, default is mp3
    """
    lossy = ["mp3", "m4a", "ogg", "aac"]
    lossless = ["flac", "wav"]

    if extension not in lossy and extension not in lossless:
        raise ValueError("extension must be one of mp3, m4a, ogg, aac, flac, wav")

    split_mode = split_mode if split_mode in ["segment", "no-split"] else "segment"

    args = [str(track_path.resolve()),
         "-o", str(output_path.resolve()),
         "--repo", str(repo),
         "--device", device if device in ["cpu", "cuda"] else "cpu",
         "--" + wav_store_method if wav_store_method in ["float32", "int16"] else "--float32",
         "--" + split_mode, None if split_mode == "no-split" else str(split_num),
         "--clip-mode", clip_mode if clip_mode in ["rescale", "clamp"] else "rescale",
         "--name", "hdemucs_mmi",
         "--jobs", str(0) if jobs < 0 else str(jobs),
         "--two-stems", "vocals",
         "--mp3" if extension in lossy else None
         ]

    if save_to_config:
        import pickle
        args.extend([save_to_config, split_num, name])
        conf = DemucsGenerateParam.from_list(args.copy(), extension)
        conf.get.save_as(name if name != "" else str(int(pickle.dumps(config)) ** 2))
    try:
        args = args[:args.index(save_to_config)]
        args.remove(None)
    except ValueError:
        pass
    print(args)
    separate.main(args)

    if not (extension in lossless and extension != "wav") or not (extension in lossy and extension != "mp3"):
        print("converting file to " + extension + "...")
        if extension in lossless:
            cmd = "ffmpeg -v quiet -threads + " + str(os.cpu_count() // 2) + " -i" + str(Path(os.path.join(output_path, "vocals.wav")).resolve()) + " " + str(Path(os.path.join(output_path, "vocals." + extension.strip("."))).resolve())
        else:
            cmd = "ffmpeg -v quiet -threads " + str(os.cpu_count() // 2) + " -i " + str(Path(os.path.join(output_path, "vocals.mp3")).resolve()) + " " + str(Path(os.path.join(output_path, "vocals." + extension.strip("."))).resolve())
        os.system(cmd)
        print("done")
    return {"vocal": Path(os.path.join(output_path, "vocals." + extension.strip("."))), "instrumental": Path(os.path.join(output_path, "no_vocals." + extension.strip(".")))}


def separate_vocal_parameterized(param: DemucsGenerateParam) -> dict[str, Path]:
    return separate_vocal(
        track_path=param.data.track_path,
        output_path=param.data.output_path,
        save_to_config=param.data.save_to_config,
        name=param.data.name,
        device=param.data.device,
        wav_store_method=param.data.wav_store_method,
        split_mode=param.data.split_mode,
        split_num=param.data.split_num,
        clip_mode=param.data.clip_mode,
        jobs=param.data.jobs,
        repo=param.data.repo,
        extension=param.data.extension
    )


def apply_so_vits(input_vocal: Path,
                  output_path: Path,
                  model_path: Path,
                  config_file_path: Path,
                  speaker: str,
                  cluster=None,
                  db_threshold=-35,
                  auto_predict_f0=True,
                  noice_scale=0.4,
                  pad_seconds=0.5,
                  f0_method="dio",
                  chunk_seconds=0.5,
                  max_chunk_seconds=40,
                  cluster_infer_ratio=0,
                  save_to_config=False,
                  name="",
                  ):
    """
    :param input_vocal: the path of the extracted vocal
    :param output_path: the path of the output directory
    :param model_path: the path of the model
    :param config_file_path: the path of the model config file
    :param speaker: the speaker of the vocal
    :param cluster: the cluster model for the vocal, optional
    :param db_threshold: the db threshold to remove the noice, default is -35
    :param auto_predict_f0: whether to auto predict the f0, default is True
    :param noice_scale: the scale of the noice, default is 0.4
    :param pad_seconds: the seconds to pad the vocal, default is 0.5
    :param f0_method: the method to predict the f0, default is dio
    :param chunk_seconds: length of each vocal chunk, default is 0.5
    :param max_chunk_seconds: max length of each vocal chunk, default is 40
    :param cluster_infer_ratio: the ratio to infer the cluster, default is 0
    :param save_to_config: whether save the config of this function to a file
    :param name: the name of the config file
    """
    clamp = lambda num, low, high: min(high, max(num, low))
    db_threshold = clamp(db_threshold, 0., -60.)
    noice_scale = clamp(noice_scale, 0., 1.)
    pad_seconds = clamp(pad_seconds, 0., 1.)
    chunk_seconds = clamp(chunk_seconds, 0., 3.)
    max_chunk_seconds = clamp(max_chunk_seconds, 0., 240.)
    cluster_infer_ratio = clamp(cluster_infer_ratio, 0., 1.)

    f0_method = f0_method if f0_method in ["crepe", "crepe-tiny", "parselmouth", "dio", "harvest"] else "dio"
    if not input_vocal.exists():
        raise FileNotFoundError(f"File {input_vocal} not found")
    if not model_path.exists():
        raise FileNotFoundError(f"Model {model_path} not found")
    if not config_file_path.exists():
        raise FileNotFoundError(f"Config {config_file_path} not found")
    if cluster is not None and not cluster.exists():
        raise FileNotFoundError(f"Cluster model {cluster} not found")

    if speaker not in json.load(open(config_file_path))["spk"]:
        raise ValueError(f"Speaker {speaker} not found in config {config_file_path}")

    output_file = output_path / Path(f"voice_generated_with_{speaker}.wav").name
    path_out = infer(
        input_path=input_vocal,
        output_path=output_file,
        model_path=model_path,
        config_path=config_file_path,
        speaker=speaker,
        cluster_model_path=cluster,
        auto_predict_f0=auto_predict_f0,
        db_thresh=db_threshold,
        noise_scale=noice_scale,
        pad_seconds=pad_seconds,
        f0_method=f0_method,
        chunk_seconds=chunk_seconds,
        max_chunk_seconds=max_chunk_seconds,
        cluster_infer_ratio=cluster_infer_ratio
    )
    return path_out


def fuse_vocal_and_instrumental(vocal_path: Path, instrumental_path: Path, output_path: Path, speaker: str):
    """
    :param vocal_path: the path of the vocal
    :param instrumental_path: the path of the instrumental
    :param output_path: the path of the output file
    """
    if not vocal_path.exists():
        raise FileNotFoundError(f"File {vocal_path} not found")
    if not instrumental_path.exists():
        raise FileNotFoundError(f"File {instrumental_path} not found")
    output_path.mkdir(parents=True, exist_ok=True)
    vocal = AudioSegment.from_file(vocal_path)
    instrumental = AudioSegment.from_file(instrumental_path)
    out = vocal.overlay(instrumental)
    out.export(output_path / Path(vocal_path.stem + f"_counterfeited_by_{speaker}.wav").name, format="wav")
    return output_path / Path(vocal_path.stem + f"_counterfeited_from_{speaker}.wav").name


def resample(input_path: Path, output_path: Path, sample_rate: int):
    """
    :param input_path: the path of the input file
    :param output_path: the path of the output file
    :param sample_rate: the sample rate of the output file
    :return: the path of the output file
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File {input_path} not found")
    output_path.mkdir(parents=True, exist_ok=True)
    cmd = f"ffmpeg -i {input_path} -ar {sample_rate} {output_path / Path(input_path.name).name}"
    os.system(cmd)
    return output_path / Path(input_path.name).name


