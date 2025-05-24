import os
import sys
import json
import time

# 尝试不同的导入方式
try:
    import yt_dlp
except ImportError:
    try:
        from yt_dlp import YoutubeDL
    except ImportError:
        print("错误: 无法导入yt_dlp模块")
        print("请确保已正确安装yt-dlp库: pip install yt-dlp")
        print("如果问题仍然存在，请尝试: pip install --upgrade yt-dlp")
        sys.exit(1)

def print_banner():
    """打印程序横幅"""
    print("=" * 80)
    print("                YouTube 视频下载器")
    print("=" * 80)
    print("该程序可以从YouTube下载视频到您的本地计算机")
    print("=" * 80)

def get_available_formats(url):
    """获取可用的格式列表"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # 调试: 打印全部格式数量
        print(f"调试: 发现 {len(info.get('formats', []))} 个格式")
        
        # 收集视频格式
        formats = []
        for f in info.get('formats', []):
            # 调试: 打印格式信息
            print(f"调试: 检查格式 {f.get('format_id')} - vcodec:{f.get('vcodec')}, acodec:{f.get('acodec')}")
            
            # 只选择带有视频的格式
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                format_str = f"{f['format_id']} - {f.get('resolution', 'N/A')} - {f.get('ext', 'N/A')}"
                formats.append((f['format_id'], format_str))
        
        # 收集仅音频格式
        audio_formats = []
        for f in info.get('formats', []):
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                format_str = f"{f['format_id']} - 仅音频 - {f.get('ext', 'N/A')}"
                audio_formats.append((f['format_id'], format_str))
        
        # 调试: 打印收集结果
        print(f"调试: 找到 {len(formats)} 个视频+音频格式")
        print(f"调试: 找到 {len(audio_formats)} 个仅音频格式")
        
        # 如果没有找到视频+音频格式，尝试收集任何包含视频的格式
        if len(formats) == 0:
            print("调试: 未找到同时包含视频和音频的格式，尝试收集任何包含视频的格式...")
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none':  # 只要有视频轨道
                    format_str = f"{f['format_id']} - {f.get('resolution', 'N/A')} - {f.get('ext', 'N/A')} - {'无音频' if f.get('acodec') == 'none' else '有音频'}"
                    formats.append((f['format_id'], format_str))
            print(f"调试: 现在找到 {len(formats)} 个包含视频的格式")
        
        return {
            'title': info.get('title', 'Unknown Title'),
            'id': info.get('id', ''),
            'video_formats': formats,
            'audio_formats': audio_formats
        }

def download_video(url, format_id=None, output_path=None, download_subs=True, sub_langs=None):
    """下载视频"""
    # 设置输出路径
    if output_path:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_template = os.path.join(output_path, '%(title)s.%(ext)s')
    else:
        output_template = '%(title)s.%(ext)s'
    
    # 配置下载选项
    ydl_opts = {
        'outtmpl': output_template,
        'progress_hooks': [progress_hook],
        'ignoreerrors': True,  # 忽略错误，继续下载
        'nooverwrites': False,  # 覆盖已存在的文件
        'retries': 10,          # 重试次数
        'fragment_retries': 10, # 片段重试次数
    }

    # 添加字幕下载选项
    if download_subs:
        # 如果没有指定语言，默认下载英文和中文字幕
        if not sub_langs:
            sub_langs = ['en', 'zh-Hans', 'zh-CN']
        
        print(f"将下载字幕: {', '.join(sub_langs)}")
        ydl_opts.update({
            'writesubtitles': True,        # 下载字幕
            'writeautomaticsub': True,     # 下载自动生成的字幕
            'subtitleslangs': sub_langs,   # 字幕语言
            # 'subtitlesformat': 'srt',      # 字幕格式
            'subtitlesformat': 'best',      # 字幕格式
            'embedsubtitles': True,        # 嵌入字幕到视频
        })

    # 如果指定了格式，则使用该格式
    if format_id:
        ydl_opts['format'] = format_id
    else:
        # 如果没有指定格式，使用最佳格式
        print("未指定格式，将使用最佳视频+音频格式")
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    
    # 确保ffmpeg可用（用于某些格式合并）
    try:
        import shutil
        if shutil.which('ffmpeg'):
            print("已检测到ffmpeg，支持格式合并")
            ydl_opts['postprocessors'] = [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',  # 转换为MP4格式
                },
                {
                    'key': 'FFmpegEmbedSubtitle'  # 显式嵌入字幕
                }
            ]
        else:
            print("警告: 未检测到ffmpeg，某些格式可能无法合并")
    except ImportError:
        print("警告: 无法检查ffmpeg可用性")
    
    # 开始下载
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
            if result != 0:
                print("警告: 下载可能未完全成功")
            return result
    except Exception as e:
        print(f"下载错误: {str(e)}")
        print("尝试使用备用下载方法...")
        
        # 备用下载方法
        backup_opts = ydl_opts.copy()
        backup_opts['format'] = 'best'  # 使用单一最佳格式
        try:
            with yt_dlp.YoutubeDL(backup_opts) as ydl:
                return ydl.download([url])
        except Exception as e2:
            print(f"备用下载方法也失败: {str(e2)}")
            raise

def progress_hook(d):
    """显示下载进度的钩子函数"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '未知')
        speed = d.get('_speed_str', '未知')
        eta = d.get('_eta_str', '未知')
        print(f"\r下载中: {percent} 速度: {speed} 预计剩余时间: {eta}", end='')
    elif d['status'] == 'finished':
        print("\n下载完成！正在进行最终处理...")

def get_playlist_info(playlist_url):
    """获取播放列表信息"""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # 不下载，只获取信息
        'skip_download': True, # 不下载
    }
    
    print("正在获取播放列表信息...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            if not playlist_info:
                print("错误: 无法获取播放列表信息")
                return None
            
            videos = []
            if 'entries' in playlist_info:
                for entry in playlist_info['entries']:
                    if entry:
                        videos.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                            'status': 'pending'
                        })
            
            return {
                'title': playlist_info.get('title', 'Unknown Playlist'),
                'id': playlist_info.get('id', ''),
                'videos': videos
            }
    except Exception as e:
        print(f"获取播放列表信息出错: {str(e)}")
        return None

def save_download_state(state, filename="download_state.json"):
    """保存下载状态到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"下载状态已保存到 {filename}")
    except Exception as e:
        print(f"保存下载状态出错: {str(e)}")

def load_download_state(filename="download_state.json"):
    """从文件加载下载状态"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"加载下载状态出错: {str(e)}")
        return None

def download_playlist(playlist_info, format_id, output_path, start_from=0):
    """下载播放列表中的视频"""
    if not playlist_info or not playlist_info.get('videos'):
        print("错误: 播放列表信息无效")
        return False
    
    videos = playlist_info['videos']
    total_videos = len(videos)
    
    print(f"\n开始下载播放列表: {playlist_info['title']}")
    print(f"共有 {total_videos} 个视频，从第 {start_from + 1} 个开始下载")
    
    # 创建下载状态记录
    download_state = {
        'playlist_id': playlist_info['id'],
        'playlist_title': playlist_info['title'],
        'format_id': format_id,
        'output_path': output_path,
        'total_videos': total_videos,
        'videos': videos
    }
    
    # 初始化计数器
    success_count = 0
    failed_count = 0
    
    # 下载视频
    for i, video in enumerate(videos[start_from:], start_from):
        video_url = video['url']
        video_title = video['title']
        
        print(f"\n[{i+1}/{total_videos}] 正在下载: {video_title}")
        
        # 检查视频状态
        if video.get('status') == 'completed':
            print(f"视频已下载，跳过")
            success_count += 1
            continue
        
        try:
            result = download_video(video_url, format_id, output_path)
            if result == 0:
                print(f"视频下载成功: {video_title}")
                videos[i]['status'] = 'completed'
                success_count += 1
            else:
                print(f"视频下载可能有问题: {video_title}")
                videos[i]['status'] = 'failed'
                failed_count += 1
        except Exception as e:
            print(f"视频下载失败: {video_title}")
            print(f"错误: {str(e)}")
            videos[i]['status'] = 'failed'
            failed_count += 1
        
        # 保存当前下载状态
        save_download_state(download_state)
        
        # 每5个视频暂停一下，避免被YouTube限制
        if (i + 1) % 5 == 0 and i < total_videos - 1:
            pause_time = 10
            print(f"\n已下载 5 个视频，暂停 {pause_time} 秒避免被限制...")
            time.sleep(pause_time)
    
    # 打印下载汇总
    print("\n下载完成！")
    print(f"成功: {success_count}, 失败: {failed_count}, 总计: {total_videos}")
    
    return success_count == total_videos

def main():
    print_banner()
    
    # 检查是否有之前未完成的下载
    previous_state = load_download_state()
    if previous_state:
        print("\n检测到之前未完成的下载:")
        print(f"播放列表: {previous_state.get('playlist_title', '未知')}")
        print(f"已下载: {sum(1 for v in previous_state.get('videos', []) if v.get('status') == 'completed')}/{previous_state.get('total_videos', 0)}")
        
        resume_choice = input("是否继续上次的下载? (y/n): ")
        if resume_choice.lower() == 'y':
            # 查找上次下载位置
            start_from = 0
            for i, video in enumerate(previous_state.get('videos', [])):
                if video.get('status') == 'completed':
                    start_from = i + 1
            
            # 如果所有视频都已下载，从头开始
            if start_from >= len(previous_state.get('videos', [])):
                print("所有视频都已下载完成，将重新开始")
                start_from = 0
            
            # 继续下载
            download_playlist(
                previous_state,
                previous_state.get('format_id'),
                previous_state.get('output_path'),
                start_from
            )
            return 0
    
    # 检查是否有URL参数
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入YouTube视频URL或播放列表URL: ")
    
    # 检查是否有输出路径参数
    output_path = None
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    
    try:
        # 检查是否是播放列表
        is_playlist = "playlist" in url or "list=" in url
        
        if is_playlist:
            playlist_info = get_playlist_info(url)
            if not playlist_info:
                print("无法获取播放列表信息，将尝试作为单个视频下载")
                is_playlist = False
            else:
                print(f"\n找到播放列表: {playlist_info['title']}")
                print(f"共有 {len(playlist_info['videos'])} 个视频")
                
                # 提供下载选项
                print("\n请选择下载方式:")
                print("1. 下载播放列表中的所有视频")
                print("2. 选择特定视频下载")
                print("3. 从特定位置开始下载")
                playlist_choice = input("请选择 (1/2/3): ")
                
                if playlist_choice == "2":
                    # 显示视频列表
                    print("\n播放列表中的视频:")
                    for i, video in enumerate(playlist_info['videos']):
                        print(f"{i+1}. {video['title']}")
                    
                    video_indices = input("请输入要下载的视频编号，多个用逗号分隔 (例如: 1,3,5): ")
                    selected_indices = []
                    
                    try:
                        for idx in video_indices.split(','):
                            idx = int(idx.strip()) - 1
                            if 0 <= idx < len(playlist_info['videos']):
                                selected_indices.append(idx)
                    except:
                        print("输入无效，将下载所有视频")
                        selected_indices = list(range(len(playlist_info['videos'])))
                    
                    # 创建新的播放列表只包含选定的视频
                    selected_videos = [playlist_info['videos'][i] for i in selected_indices]
                    playlist_info['videos'] = selected_videos
                    playlist_info['total_videos'] = len(selected_videos)
                
                elif playlist_choice == "3":
                    start_idx = input("请输入开始下载的视频编号 (1 到 {}): ".format(len(playlist_info['videos'])))
                    try:
                        start_idx = int(start_idx) - 1
                        if 0 <= start_idx < len(playlist_info['videos']):
                            # 创建新的播放列表从选定位置开始
                            playlist_info['videos'] = playlist_info['videos'][start_idx:]
                    except:
                        print("输入无效，将从头开始下载")
        
        # 询问格式
        print("\n请选择下载类型:")
        print("1. 视频+音频")
        print("2. 仅音频")
        print("3. 使用推荐预设格式 (更简单)")
        choice = input("请输入选择 (1/2/3): ")
        
        if choice == "3":
            print("\n选择预设格式:")
            print("1. 最佳视频+音频质量")
            print("2. 最佳音频质量")
            print("3. 平衡质量(720p)")
            print("4. 低质量(节省带宽)")
            preset_choice = input("请选择 (1-4): ")
            
            preset_formats = {
                "1": "bestvideo+bestaudio/best",
                "2": "bestaudio/best",
                "3": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
                "4": "worstvideo+worstaudio/worst"
            }
            
            if preset_choice in preset_formats:
                selected_format = preset_formats[preset_choice]
            else:
                print("无效选择，使用最佳质量")
                selected_format = "bestvideo+bestaudio/best"
        else:
            if not is_playlist:
                # 获取单个视频的格式信息
                print("正在获取视频信息...")
                formats_info = get_available_formats(url)
                
                print(f"\n找到视频: {formats_info['title']}")
                print(f"调试: formats_info内容: {formats_info}")
                
                # 确保找到了格式
                if not formats_info['video_formats'] and not formats_info['audio_formats']:
                    print("错误: 无法找到任何可下载的格式")
                    print("可能的原因:")
                    print("1. 视频可能受版权保护或地区限制")
                    print("2. YouTube API可能发生变化")
                    print("3. 网络连接问题")
                    print("\n尝试使用预设格式下载...")
                    
                    print("选择下载类型:")
                    print("1. 使用最佳视频+音频质量")
                    print("2. 使用最佳音频质量")
                    print("3. 使用平衡质量(720p)")
                    print("4. 使用低质量(节省带宽)")
                    preset_choice = input("请选择 (1-4): ")
                    
                    preset_formats = {
                        "1": "bestvideo+bestaudio/best",
                        "2": "bestaudio/best",
                        "3": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
                        "4": "worstvideo+worstaudio/worst"
                    }
                    
                    if preset_choice in preset_formats:
                        preset_format = preset_formats[preset_choice]
                        print(f"使用预设格式: {preset_format}")
                        download_video(url, preset_format, output_path)
                        print(f"视频已下载到 {output_path if output_path else '当前目录'}")
                        return 0
                    else:
                        print("无效选择")
                        return 1
            
            if choice == '2':
                if is_playlist:
                    selected_format = "bestaudio/best"
                else:
                    # 显示可用的音频格式
                    print("\n可用的音频格式:")
                    if not formats_info['audio_formats']:
                        print("未找到任何可用的音频格式")
                        print("尝试使用默认最佳音频格式...")
                        selected_format = "bestaudio/best"
                    else:
                        for i, (format_id, format_str) in enumerate(formats_info['audio_formats'], 1):
                            print(f"{i}. {format_str}")
                        
                        max_choice = len(formats_info['audio_formats'])
                        audio_choice = input(f"请选择音频格式 (1-{max_choice}): ")
                        
                        try:
                            audio_choice = int(audio_choice) - 1
                            if audio_choice < 0 or audio_choice >= max_choice:
                                print(f"错误: 请输入1到{max_choice}之间的数字")
                                return 1
                            selected_format = formats_info['audio_formats'][audio_choice][0]
                        except ValueError:
                            print("错误: 请输入有效的数字")
                            return 1
            else:
                if is_playlist:
                    selected_format = "bestvideo+bestaudio/best"
                else:
                    # 显示可用的视频格式
                    print("\n可用的视频格式:")
                    if not formats_info['video_formats']:
                        print("未找到任何可用的视频+音频格式")
                        print("尝试使用默认最佳视频+音频格式...")
                        selected_format = "bestvideo+bestaudio/best"
                    else:
                        for i, (format_id, format_str) in enumerate(formats_info['video_formats'], 1):
                            print(f"{i}. {format_str}")
                        
                        max_choice = len(formats_info['video_formats'])
                        video_choice = input(f"请选择视频格式 (1-{max_choice}): ")
                        
                        try:
                            video_choice = int(video_choice) - 1
                            if video_choice < 0 or video_choice >= max_choice:
                                print(f"错误: 请输入1到{max_choice}之间的数字")
                                return 1
                            selected_format = formats_info['video_formats'][video_choice][0]
                        except ValueError:
                            print("错误: 请输入有效的数字")
                            return 1
        
        # 询问输出路径（如果不是通过命令行参数提供）
        if not output_path:
            output_choice = input("\n是否指定下载路径? (y/n): ")
            if output_choice.lower() == 'y':
                output_path = input("请输入下载路径: ")
        
        # 开始下载
        if is_playlist:
            download_playlist(playlist_info, selected_format, output_path)
        else:
            print(f"\n开始下载 '{formats_info['title']}'...")
            download_video(url, selected_format, output_path)
            print(f"\n视频已成功下载到 {output_path if output_path else '当前目录'}")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        print("调试信息:", e.__class__.__name__)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 