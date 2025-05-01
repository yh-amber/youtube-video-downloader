#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ffmpeg安装助手
这个脚本会帮助用户在不同平台上安装ffmpeg
"""

import os
import sys
import platform
import subprocess
import webbrowser

def print_banner():
    """打印程序横幅"""
    print("=" * 80)
    print("                ffmpeg 安装助手")
    print("=" * 80)
    print("该工具将帮助您安装 ffmpeg，这是合并YouTube视频和音频所必需的")
    print("=" * 80)

def check_ffmpeg():
    """检查ffmpeg是否已安装"""
    try:
        import shutil
        if shutil.which('ffmpeg'):
            return True
    except ImportError:
        pass
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def install_ffmpeg_windows():
    """Windows平台安装指南"""
    print("\nWindows平台安装ffmpeg:")
    print("1. 下载ffmpeg")
    print("   - 访问 https://ffmpeg.org/download.html")
    print("   - 或直接从 https://github.com/BtbN/FFmpeg-Builds/releases 下载")
    print("2. 解压下载的文件到一个目录，例如 C:\\ffmpeg")
    print("3. 将ffmpeg的bin目录添加到系统PATH环境变量:")
    print("   - 右键点击'此电脑'或'我的电脑'，选择'属性'")
    print("   - 点击'高级系统设置'")
    print("   - 点击'环境变量'按钮")
    print("   - 在'系统变量'部分找到'Path'并点击'编辑'")
    print("   - 点击'新建'按钮并添加ffmpeg的bin目录路径，例如 C:\\ffmpeg\\bin")
    print("   - 点击'确定'保存设置")
    print("\n是否要打开ffmpeg下载页面? (y/n): ", end="")
    if input().lower() == 'y':
        webbrowser.open("https://github.com/BtbN/FFmpeg-Builds/releases")

def install_ffmpeg_macos():
    """macOS平台安装指南"""
    print("\nmacOS平台安装ffmpeg:")
    print("方法1: 使用Homebrew (推荐)")
    print("1. 如果尚未安装Homebrew，请先安装:")
    print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    print("2. 使用Homebrew安装ffmpeg:")
    print("   brew install ffmpeg")
    print("\n方法2: 使用MacPorts")
    print("1. 如果已安装MacPorts:")
    print("   sudo port install ffmpeg")
    
    print("\n是否要运行Homebrew安装命令? (y/n): ", end="")
    if input().lower() == 'y':
        try:
            # 检查是否已安装Homebrew
            result = subprocess.run(
                ["brew", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                print("\n检测到Homebrew，正在安装ffmpeg...")
                subprocess.run(["brew", "install", "ffmpeg"])
            else:
                print("\n未检测到Homebrew，请先安装Homebrew...")
                print("是否要安装Homebrew? (y/n): ", end="")
                if input().lower() == 'y':
                    subprocess.run(["/bin/bash", "-c", "\"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""], shell=True)
        except Exception as e:
            print(f"执行命令时出错: {str(e)}")

def install_ffmpeg_linux():
    """Linux平台安装指南"""
    print("\nLinux平台安装ffmpeg:")
    
    # 尝试检测Linux发行版
    distro = "未知"
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.split("=")[1].strip().strip('"')
                        break
    except:
        pass
    
    if distro == "ubuntu" or distro == "debian":
        print(f"检测到 {distro.capitalize()} 系统，推荐使用以下命令:")
        print("sudo apt update")
        print("sudo apt install ffmpeg")
        
        print("\n是否要运行安装命令? (y/n): ", end="")
        if input().lower() == 'y':
            try:
                subprocess.run(["sudo", "apt", "update"])
                subprocess.run(["sudo", "apt", "install", "ffmpeg"])
            except Exception as e:
                print(f"执行命令时出错: {str(e)}")
    
    elif distro == "fedora":
        print("检测到Fedora系统，推荐使用以下命令:")
        print("sudo dnf install ffmpeg")
        
        print("\n是否要运行安装命令? (y/n): ", end="")
        if input().lower() == 'y':
            try:
                subprocess.run(["sudo", "dnf", "install", "ffmpeg"])
            except Exception as e:
                print(f"执行命令时出错: {str(e)}")
    
    elif distro == "arch" or distro == "manjaro":
        print(f"检测到 {distro.capitalize()} 系统，推荐使用以下命令:")
        print("sudo pacman -S ffmpeg")
        
        print("\n是否要运行安装命令? (y/n): ", end="")
        if input().lower() == 'y':
            try:
                subprocess.run(["sudo", "pacman", "-S", "ffmpeg"])
            except Exception as e:
                print(f"执行命令时出错: {str(e)}")
    
    else:
        print("无法确定具体Linux发行版，请根据您的发行版使用对应的包管理器安装ffmpeg:")
        print("- Ubuntu/Debian: sudo apt install ffmpeg")
        print("- Fedora: sudo dnf install ffmpeg")
        print("- Arch/Manjaro: sudo pacman -S ffmpeg")
        print("- CentOS: sudo yum install ffmpeg")

def main():
    """主函数"""
    print_banner()
    
    # 检查ffmpeg是否已安装
    if check_ffmpeg():
        print("\nffmpeg已经安装在您的系统上!")
        print("您可以正常使用YouTube下载器合并视频和音频。")
        return 0
    
    print("\nffmpeg未安装。这是合并YouTube视频和音频所必需的工具。")
    
    # 根据操作系统提供安装指南
    system = platform.system()
    if system == "Windows":
        install_ffmpeg_windows()
    elif system == "Darwin":  # macOS
        install_ffmpeg_macos()
    elif system == "Linux":
        install_ffmpeg_linux()
    else:
        print(f"未知操作系统: {system}")
        print("请访问 https://ffmpeg.org/download.html 获取安装指南。")
    
    print("\n安装完成后，请重新运行YouTube下载器。")
    print("如果仍然遇到问题，您可以选择使用不需要合并的格式:")
    print("- 在下载选项中选择'仅音频'")
    print("- 或选择'使用推荐预设格式'，然后在提示时选择'2. 最佳音频质量'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())