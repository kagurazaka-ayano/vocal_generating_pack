# 环境配置

1. 安装[ffmpeg](https://ffmpeg.org/)

2. 安装CUDA release 12.1和cuDNN v8.9.2(如果你想要使用Nvidia GPU训练)

   > 安装cudnn时会被要求注册nvidia developer account
   >
   > CUDA和cuDNN的配置详见[这篇文章(win)](https://zhuanlan.zhihu.com/p/99880204)和[这篇文章(linux)](https://blog.csdn.net/qq_40263477/article/details/105132822)
    - Windows: [CUDA](https://developer.nvidia.com/cuda-downloads) [cuDNN](https://developer.nvidia.com/cudnn)
    - Linux: [CUDA](https://developer.nvidia.com/cuda-downloads) [cuDNN](https://developer.nvidia.com/cudnn)

3. 从[Anaconda官网](https://docs.conda.io/en/latest/miniconda.html)下载miniconda

4. 安装并激活环境

   > 如果是macos, 先运行scripts中的`fix_mac_certificate_issue.sh`脚本

   linux:
    ```bash
    conda env create -f env_linux.yaml
    conda activate vocal-generating-pack
    ```

   macos:
    ```bash
    conda env create -f env_macos.yaml
    conda activate vocal-generating-pack
    ```

   windows:
    ```bash
    conda env create -f env_windows.yaml
    conda activate vocal-generating-pack 
    ```

5. 如果你想要训练模型, 安装pyannote-audio:
   ```bash
       pip install https://github.com/pyannote/pyannote-audio/archive/develop.zip 
   ```

6. 安装pytorch
   windows/linux:
    ```bash
    pip3 install --upgrade --force-reinstall --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
    ```
   macos:
    ```bash
    pip3 install --upgrade --force-reinstall --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
    ```


国内用户可能需要等待较长时间

## 使用多人物语音分离的先决条件

1. 同意[hf.co/pyannote/speaker-diarization](https://hf.co/pyannote/speaker-diarization) 和[https://hf.co/pyannote/segmentation](hf.co/pyannote/segmentation)的用户使用协议
2. 从[hf.co/settings/tokens](hf.co/settings/tokens)生成你的huggingface auth token
3. 在[./files/keys](./files/keys)或者是你自定义的key文件夹下创建一个叫`huggingface_auth`的文件, 在里面输入你在第二步获得的token
