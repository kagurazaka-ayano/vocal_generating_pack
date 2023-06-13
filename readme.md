# 基于demucs和so-vits-svc的语音分离与生成

## 功能
- 语音分离
- 语音生成
- 合并音频

## 安装
1. 安装[ffmpeg](https://ffmpeg.org/)

2. 安装CUDA release 12.1和cuDNN v8.9.2(如果你想要使用NvidiaGPU训练)

    > 安装cudnn时会被要求注册nvidia developer account
    > 
    > CUDA和cuDNN的配置详见[这篇文章(win)](https://zhuanlan.zhihu.com/p/99880204)和[这篇文章(linux)](https://blog.csdn.net/qq_40263477/article/details/105132822)
    - Windows: [CUDA](https://developer.nvidia.com/cuda-downloads) [cuDNN](https://developer.nvidia.com/cudnn)
    - Linux: [CUDA](https://developer.nvidia.com/cuda-downloads) [cuDNN](https://developer.nvidia.com/cudnn)

3. 从[Anaconda官网](https://www.anaconda.com/download/)下载anaconda或miniconda

4. 安装并激活环境
    > 如果是macos, 先运行scripts中的`fix_mac_certificate_issue.sh`脚本

    linux:
    ```bash
    conda env create -f env_linux.yml
    conda activate vocal-generating-pack
    ```
    macos:
    ```bash
    conda env create -f env_macos.yml
    conda activate vocal-generating-pack
    ```

5. 手动安装pytorch依赖
    windows/linux:
    ```bash
    pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
    ```
    macos:
    ```bash
    pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
    ```




## roadmap
- [ ] 文字转语音并输出
- [ ] 集成模型训练
- [ ] Qt GUI
- [ ] WebUI
- [ ] 资源管理器
  - [ ] 模型管理器
  - [ ] 数据集管理器
- [ ] 插件系统

## 借物表
- [demucs(MIT)](https://github.com/facebookresearch/demucs)
- [so-vits-svc-fork(MIT)](https://github.com/voicepaw/so-vits-svc-fork)
- [纳西妲so-vits-svc模型(MIT)](https://huggingface.co/kaze-mio/so-vits-genshin)
- [土狗哥-空庭雨(已获得原作者授权)](https://music.163.com/song?id=2006730110)
