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

5. 安装pytorch
    windows/linux:
    ```bash
    pip3 install --upgrade --force-reinstall --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
    ```
    macos:
    ```bash
    pip3 install --upgrade --force-reinstall --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
    ```
   
6. 如果你想要训练模型, 安装pyannote-audio:
   ```bash
       pip install -qq https://github.com/pyannote/pyannote-audio/archive/develop.zip 
   ```
国内用户可能需要等待较长时间
