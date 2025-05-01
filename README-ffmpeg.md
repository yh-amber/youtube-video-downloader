# 安装ffmpeg解决视频合并问题

当您在使用YouTube下载器时遇到以下警告：
```
WARNING: You have requested merging of multiple formats but ffmpeg is not installed. The formats won't be merged
```

这表示您需要安装ffmpeg才能合并视频和音频格式。以下是在不同系统上安装ffmpeg的方法：

## Windows系统

1. 访问 https://ffmpeg.org/download.html 或直接从 https://github.com/BtbN/FFmpeg-Builds/releases 下载ffmpeg
2. 解压下载的文件到一个目录，例如 `C:\ffmpeg`
3. 将ffmpeg的bin目录添加到系统PATH环境变量：
   - 右键点击"此电脑"或"我的电脑"，选择"属性"
   - 点击"高级系统设置"
   - 点击"环境变量"按钮
   - 在"系统变量"部分找到"Path"并点击"编辑"
   - 点击"新建"按钮并添加ffmpeg的bin目录路径，例如 `C:\ffmpeg\bin`
   - 点击"确定"保存设置
4. 重启命令提示符或PowerShell窗口
5. 输入 `ffmpeg -version` 验证安装

## macOS系统

### 使用Homebrew（推荐）

1. 如果尚未安装Homebrew，请先安装：
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. 使用Homebrew安装ffmpeg：
   ```
   brew install ffmpeg
   ```

3. 验证安装：
   ```
   ffmpeg -version
   ```

## Linux系统

### Ubuntu/Debian

```
sudo apt update
sudo apt install ffmpeg
```

### Fedora

```
sudo dnf install ffmpeg
```

### Arch Linux/Manjaro

```
sudo pacman -S ffmpeg
```

### CentOS/RHEL

```
sudo yum install epel-release
sudo yum install ffmpeg
```

## 安装后的操作

安装ffmpeg后，再次运行YouTube下载器，警告应该会消失，下载的视频和音频将会自动合并。

## 替代解决方案

如果无法安装ffmpeg，您可以：

1. 选择"仅音频"选项下载
2. 选择"使用推荐预设格式"然后选择"2. 最佳音频质量"
3. 或者直接选择不需要合并的格式（单一格式，没有加号"+"）