# YouTube视频下载器

这是一个简单易用的Python脚本，用于从YouTube下载视频到本地计算机。

## 功能特点

- 支持从命令行或交互式界面输入YouTube URL
- 支持下载视频+音频或仅音频文件
- 提供多种分辨率和格式选择
- 显示实时下载进度和速度
- 支持指定自定义下载路径

## 安装依赖

在使用此脚本之前，您需要安装必要的依赖项：

1. ffmpeg
```bash
请参照README-ffmpeg.md
```

2. yt-dlp
```bash
pip install yt-dlp
```

## 使用方法

### 基本用法

```bash
python downloader.py
```

这将启动交互式界面，提示您输入YouTube URL和选择下载选项。

### 使用命令行参数

```bash
python downloader.py "https://www.youtube.com/watch?v=<YOUTUBE_VIDEO_ID>" "<download_folder>"
```

参数说明：
1. YouTube视频URL (必需)
2. 下载路径 (可选)

## 示例

### 下载Python教程视频

```bash
python downloader.py "https://www.youtube.com/playlist?list=PLE7DDD91010BC51F8"
```

## 注意事项

- 请尊重版权，仅下载您有权访问的内容
- 下载速度取决于您的网络连接和YouTube服务器状态
- 某些视频可能因版权或地区限制而无法下载

## 故障排除

如果遇到问题，请确保：
1. 您已安装最新版本的yt-dlp
2. 提供的YouTube URL是有效的
3. 您的网络连接正常
4. 您有足够的磁盘空间存储下载的文件 