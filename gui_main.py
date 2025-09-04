import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import atexit
import signal
import subprocess
import yt_dlp
from strategies.factory import DownloadStrategyFactory
from strategies.mp4_strategy import MP4DownloadStrategy
from strategies.mp3_strategy import MP3DownloadStrategy
from config import load_config, save_config
from utils.history import add_download_record
from components.silent_exit_gui_base import SilentExitGUIBase

class YouTubeDownloaderGUI(SilentExitGUIBase):
    def __init__(self, root):
        # 初始化静默退出基类 - 提供应用标题和图标路径
        super().__init__(
            root, 
            app_title="YouTube 视频下载器 - @橘生淮北 基于开源项目 yt-dlp 制作",
            icon_path="YouTube_Downloader_logo.ico"
        )
        
        # 设置窗口基本属性
        self.root.geometry("650x650")
        self.root.configure(bg="#f8f9fa")
        self.root.resizable(True, True)  # 允许窗口大小调整
        
        # 设置窗口最小尺寸
        self.root.minsize(600, 550)
        
        # 设置UI
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 加载配置
        config = load_config()
        self.download_dir = config.get("download_dir", os.path.join(os.path.expanduser("~"), "Downloads", "youtube_downloads"))
        
        # 确保下载目录存在
        if not os.path.exists(self.download_dir):
            try:
                os.makedirs(self.download_dir, exist_ok=True)
                self.log(f"[信息] 创建下载目录: {self.download_dir}")
            except Exception as e:
                self.log(f"[错误] 创建下载目录失败: {e}")
                # 使用当前目录作为备选
                self.download_dir = os.getcwd()
        
        # 主标题
        title_frame = tk.Frame(self.root, bg="#f8f9fa")
        title_frame.pack(pady=(15, 5), padx=20, fill="x")
        
        # 标题居中显示，不使用红色字体
        title_label = tk.Label(title_frame, text="YouTube 视频下载器", 
                              font=("Arial", 18, "bold"), fg="#333333", bg="#f8f9fa")
        title_label.pack(anchor="center")

        # URL 输入区域（优化间距）
        url_frame = tk.Frame(self.root, bg="#f8f9fa")
        url_frame.pack(pady=(10, 8), padx=20, fill="x")
        
        url_label = tk.Label(url_frame, text="🔗 YouTube 视频/播放列表链接:", 
                           font=("Arial", 10, "bold"), fg="#333333", bg="#f8f9fa")
        url_label.pack(anchor="w", pady=(0, 5))
        
        self.url_entry = tk.Entry(url_frame, width=70, font=("Arial", 10), 
                                relief="solid", bd=1)
        self.url_entry.pack(fill="x", padx=10, pady=8)
        
        # 使用说明区域（点击显示/隐藏功能）
        self.usage_visible = False
        
        # 使用说明内容框架（初始隐藏）
        self.usage_frame = tk.Frame(self.root, bg="#e8f5e8", relief="solid", bd=1)
        
        # 绿色加粗的标题
        usage_title_label = tk.Label(self.usage_frame, text="使用说明：", 
                              font=("Arial", 10, "bold"), fg="#28a745", bg="#e8f5e8")
        usage_title_label.pack(anchor="w", padx=10, pady=(8, 2))
        
        # 详细说明文本
        usage_label = tk.Label(self.usage_frame, 
                              text="单个链接填上方，批量链接填下方文本框。如两处都有内容，仅下载批量链接，忽略单个链接。\n示例：批量文本框有内容时，上方单个链接会被忽略。",
                              font=("Arial", 9), fg="#6c757d", bg="#e8f5e8",
                              wraplength=580, justify="left")
        usage_label.pack(anchor="w", padx=10, pady=(0, 8))

        # 格式选择和选项区域（优化间距，将所有功能居中显示）
        options_frame = tk.Frame(self.root, bg="#f8f9fa")
        options_frame.pack(pady=(8, 6), padx=20, fill="x")
        
        # 主要功能行（格式选择、封面下载、功能按钮）- 居中显示
        main_options_frame = tk.Frame(options_frame, bg="#f8f9fa")
        main_options_frame.pack()
        
        # 格式选择（左侧）
        format_label = tk.Label(main_options_frame, text="🎥 格式:", 
                               font=("Arial", 10, "bold"), fg="#333333", bg="#f8f9fa")
        format_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.format_var = tk.StringVar(value="mp4")
        format_dropdown = ttk.Combobox(main_options_frame, textvariable=self.format_var, 
                                     values=["mp4", "mp3"], state="readonly",
                                     font=("Arial", 9), width=6)
        format_dropdown.pack(side=tk.LEFT, padx=(0, 15))
        
        # 封面下载选项（中间）
        self.download_video_thumbnail_var = tk.BooleanVar(value=False)
        thumbnail_check = tk.Checkbutton(main_options_frame, 
                                        text="📷 下载封面", 
                                        variable=self.download_video_thumbnail_var,
                                        font=("Arial", 9, "bold"), fg="#495057", bg="#f8f9fa")
        thumbnail_check.pack(side=tk.LEFT, padx=(0, 15))
        
        # 功能亮点按钮（右侧）
        features_button = tk.Button(main_options_frame, text="🌟 亮点", 
                                   command=self.show_features, 
                                   font=("Arial", 9), 
                                   bg="#6c757d", fg="white",
                                   relief="flat", padx=8, pady=3,
                                   cursor="hand2")
        features_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 使用说明按钮（右侧）
        self.usage_toggle_button = tk.Button(main_options_frame, text="📖 说明", 
                                           command=self.toggle_usage, 
                                           font=("Arial", 9), 
                                           bg="#6c757d", fg="white",
                                           relief="flat", padx=8, pady=3,
                                           cursor="hand2")
        self.usage_toggle_button.pack(side=tk.LEFT)

        # 选择下载目录（优化间距）
        dir_frame = tk.Frame(self.root, bg="#f8f9fa")
        dir_frame.pack(pady=(8, 6), padx=20, fill="x")
        
        # 下载目录显示框
        dir_display_frame = tk.Frame(dir_frame, bg="#ffffff", relief="solid", bd=1)
        dir_display_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        
        self.dir_label = tk.Label(dir_display_frame, text=self.download_dir, 
                                 wraplength=400, justify="left", 
                                 bg="#ffffff", fg="#333333", font=("Arial", 9))
        self.dir_label.pack(fill="both", expand=True, padx=10, pady=8)
        
        # 选择目录按钮（统一样式和美化）
        self.dir_button = tk.Button(dir_frame, text="📁 选择下载位置", 
                                   command=self.choose_directory,
                                   font=("Arial", 10, "bold"), 
                                   bg="#007bff", fg="white",
                                   relief="flat", padx=20, pady=8,
                                   cursor="hand2",
                                   borderwidth=0,
                                   activebackground="#0056b3",
                                   activeforeground="white")
        self.dir_button.pack(side=tk.RIGHT)

        # 批量下载区域（优化间距和大小）
        batch_frame = tk.Frame(self.root, bg="#f8f9fa")
        batch_frame.pack(pady=(8, 6), padx=20, fill="x")
        
        batch_label = tk.Label(batch_frame, text="📋 批量下载（每行一个链接，可选）:", 
                              font=("Arial", 10, "bold"), fg="#333333", bg="#f8f9fa")
        batch_label.pack(anchor="w", pady=(0, 4))
        
        # 批量文本框容器（固定高度）
        text_container = tk.Frame(batch_frame, bg="#ffffff", relief="solid", bd=1)
        text_container.pack(fill="x", pady=(0, 0))
        
        self.batch_text = tk.Text(text_container, height=4, width=70, 
                                font=("Arial", 10), relief="flat", wrap="word")
        self.batch_text.pack(side=tk.LEFT, fill="both", expand=True, padx=8, pady=6)
        
        # 添加滚动条
        scrollbar = tk.Scrollbar(text_container, command=self.batch_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.batch_text.config(yscrollcommand=scrollbar.set)

        # 下载控制区域（优化间距）
        control_frame = tk.Frame(self.root, bg="#f8f9fa")
        control_frame.pack(pady=(10, 8), padx=20, fill="x")
        
        # 下载按钮（与选择下载位置按钮统一样式并美化）
        self.download_button = tk.Button(control_frame, text="🚀 开始下载", 
                                        command=self.start_download,
                                        font=("Arial", 12, "bold"), 
                                        bg="#007bff", fg="white",
                                        relief="flat", padx=30, pady=10,
                                        cursor="hand2",
                                        borderwidth=0,
                                        activebackground="#0056b3",
                                        activeforeground="white")
        self.download_button.pack()
        
        # 进度区域（优化间距）
        progress_frame = tk.Frame(self.root, bg="#f8f9fa")
        progress_frame.pack(pady=(6, 4), padx=20, fill="x")
        
        # 上层：进度条
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", 
                                       length=500, mode='determinate',
                                       style="TProgressbar")
        self.progress['maximum'] = 100  # 设置最大值为100
        self.progress['value'] = 0      # 初始值为0
        self.progress.pack(pady=(0, 8), fill="x")
        
        # 中层：状态标签（速度、剩余时间、百分比）
        self.status_label = tk.Label(progress_frame, text="[状态] 等待下载...", 
                                    wraplength=600, font=("Arial", 9), 
                                    fg="#6c757d", bg="#f8f9fa")
        self.status_label.pack(pady=(0, 6))
        
        # 下层：视频标题标签（分辨率_视频标题）
        self.video_title_label = tk.Label(progress_frame, text="[视频] 等待下载任务...", 
                                         wraplength=600, font=("Arial", 10, "bold"), 
                                         fg="#495057", bg="#f8f9fa")
        self.video_title_label.pack(pady=(0, 4))
        
        # 底层：频道信息标签
        self.channel_info_label = tk.Label(progress_frame, text="@等待频道信息...", 
                                          wraplength=600, font=("Arial", 9), 
                                          fg="#007bff", bg="#f8f9fa")
        self.channel_info_label.pack()

        # 日志区域（与批量下载窗口大小保持一致）
        log_frame = tk.Frame(self.root, bg="#f8f9fa")
        log_frame.pack(pady=(8, 10), padx=20, fill="x")
        
        log_label = tk.Label(log_frame, text="📄 下载日志:", 
                           font=("Arial", 10, "bold"), fg="#333333", bg="#f8f9fa")
        log_label.pack(anchor="w", pady=(0, 4))
        
        # 日志文本框容器（固定高度，与批量下载窗口一致）
        log_container = tk.Frame(log_frame, bg="#ffffff", relief="solid", bd=1)
        log_container.pack(fill="x", pady=(0, 0))
        
        self.log_text = tk.Text(log_container, height=4, width=70, 
                              font=("Consolas", 9), relief="flat", wrap="word",
                              bg="#ffffff", fg="#333333")
        self.log_text.pack(side=tk.LEFT, fill="both", expand=True, padx=8, pady=6)
        
        # 添加滚动条
        log_scrollbar = tk.Scrollbar(log_container, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # 配置日志颜色标签
        self.log_text.tag_config("success", foreground="#28a745", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("error", foreground="#dc3545", font=("Consolas", 9, "bold"))
        
        # 初始化日志内容
        self.log("[系统] YouTube下载器启动完成，等待操作...")
    
    # ===========================================
    # 重写基类方法（自定义清理逻辑）
    # ===========================================
    
    def cleanup_processes(self):
        """自定义清理逻辑（重写基类方法）"""
        # 先执行自定义清理逻辑
        try:
            # 保存设置（如果需要）
            # self.save_settings()
            
            # 清理临时文件（如果有）
            # self.clean_temp_files()
            
            pass  # 目前没有特殊的清理需求
            
        except Exception:
            pass  # 静默失败，不影响程序关闭
        
        # 调用基类清理（包括进程管理和静默退出优化）
        super().cleanup_processes()
    
    def toggle_usage(self):
        """切换使用说明的显示/隐藏状态"""
        if self.usage_visible:
            # 隐藏使用说明
            self.usage_frame.pack_forget()
            self.usage_toggle_button.config(text="📖 说明", bg="#6c757d")
            self.usage_visible = False
        else:
            # 显示使用说明（在按钮下方显示）
            self.usage_frame.pack(pady=(8, 0), padx=20, fill="x", after=self.usage_toggle_button.master.master)
            self.usage_toggle_button.config(text="🔼 隐藏", bg="#17a2b8")
            self.usage_visible = True

    def validate_url(self, url):
        """验证URL合法性和安全性"""
        import re
        
        if not url or not url.strip():
            return False, "链接不能为空"
        
        url = url.strip()
        
        # 检查是否为YouTube链接
        youtube_patterns = [
            r'^https?://(www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]+',
            r'^https?://(www\.)?youtube\.com/shorts/[a-zA-Z0-9_-]+',
            r'^https?://(www\.)?youtube\.com/playlist\?list=[a-zA-Z0-9_-]+',
            r'^https?://youtu\.be/[a-zA-Z0-9_-]+',
            r'^https?://m\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+'
        ]
        
        is_valid = any(re.match(pattern, url) for pattern in youtube_patterns)
        
        if not is_valid:
            return False, "仅支持YouTube视频链接"
        
        # 检查链接长度（防止恶意输入）
        if len(url) > 500:
            return False, "链接过长"
        
        return True, ""
    
    def show_features(self):
        """显示软件功能亮点（重新总结的内容）"""
        features_text = """🎆 YouTube下载器 - 功能亮点 🎆

🎥 核心下载功能：
• 支持 MP4 高清视频下载（最高 4K 超清）
• 支持 MP3 音频提取（192kbps 高品质音质） 
• 批量下载多个视频（无数量限制）
• 智能文件命名（标题+上传者+分辨率）

🌈 特色增强功能：
• 高清封面下载（PNG 格式，完美保存）
• 实时进度显示（下载速度+剩余时间）
• 彩色日志反馈（成功/错误状态一目了然）
• 视频信息预览（标题、作者、时长）

🛡️ 稳定性保障：
• 网络错误自动重试（智能重试机制）
• SSL 协议错误修复（解决连接问题）
• 下载中断后可恢复（断点续传支持）
• 多线程支持（界面不卡顿、响应迅速）

💾 优秀的用户体验：
• 现代化图形界面（简洁友好、直观易用）
• 自定义下载目录（灵活管理文件）
• 下载历史记录（轻松追踪下载任务）
• 一键批量操作（提高工作效率）

🌍 广泛兼容性：
• 跨平台支持（Windows/Mac/Linux）
• 支持所有 YouTube 视频格式
• 支持 YouTube Shorts 短视频
• 支持播放列表整体下载

✨ 最新优化：
• 网络连接稳定性大幅提升
• 封面下载功能全新上线
• 错误处理机制全面增强
• 界面交互体验持续优化"""
        
        messagebox.showinfo("🎆 软件功能亮点", features_text)

    def log(self, message, color=None):
        self.log_text.insert(tk.END, f"{message}\n", color)
        self.log_text.see(tk.END)
        self.root.update()
    
    def get_video_info(self, url):
        """获取视频信息"""
        import yt_dlp
        import re
        from datetime import datetime
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'retries': 3,
                'fragment_retries': 3,
                'socket_timeout': 30,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', '')
                uploader = info.get('uploader', '')
                height = info.get('height', 0)
                ext = info.get('ext', 'mp4')
                
                # 对于视频文件，默认使用mp4格式
                if ext in ['webm', 'mkv', 'flv']:
                    ext = 'mp4'
                
                # 清理文件名中的非法字符
                def clean_filename(name):
                    if not name:
                        return ''
                    # 移除或替换非法字符
                    name = re.sub(r'[<>:"/\|?*]', '_', name)
                    # 限制长度
                    return name[:50] if len(name) > 50 else name
                
                clean_title = clean_filename(title)
                clean_uploader = clean_filename(uploader)
                
                # 生成文件名
                if clean_title:
                    if clean_uploader:
                        if height > 0:
                            filename = f"{clean_title}_{clean_uploader}_{height}p.{ext}"
                        else:
                            filename = f"{clean_title}_{clean_uploader}.{ext}"
                    else:
                        if height > 0:
                            filename = f"{clean_title}_{height}p.{ext}"
                        else:
                            filename = f"{clean_title}.{ext}"
                else:
                    # 没有标题时使用时间格式
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"video_{timestamp}.{ext}"
                
                return {
                    'title': title,
                    'uploader': uploader,
                    'height': height,
                    'ext': ext,
                    'filename': filename,
                    'thumbnail': info.get('thumbnail')  # 添加封面链接
                }
                
        except Exception as e:
            self.log(f"[错误] 获取视频信息失败: {e}")
            # 如果获取信息失败，使用默认文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return {
                'title': '',
                'uploader': '',
                'height': 0,
                'ext': 'mp4',
                'filename': f"video_{timestamp}.mp4",
                'thumbnail': None
            }

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_dir = directory
            self.dir_label.config(text=directory)
            
            # 确保选择的目录存在
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    self.log(f"[信息] 创建下载目录: {directory}")
                except Exception as e:
                    self.log(f"[错误] 创建目录失败: {e}")
                    return
            
            # 保存配置
            config = load_config()
            config["download_dir"] = directory
            save_config(config)
            self.log(f"[设置] 下载目录变更为: {directory}")
    
    def download_video_thumbnail(self, video_info, output_dir):
        """下载视频封面"""
        try:
            import urllib.request
            import urllib.error
            import ssl
            
            thumbnail_url = video_info.get('thumbnail')
            if not thumbnail_url:
                self.log("[警告] 未找到封面链接")
                return None
            
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.log(f"[信息] 创建下载目录: {output_dir}")
            
            # 生成封面文件名
            base_filename = video_info['filename'].rsplit('.', 1)[0]  # 移除扩展名
            thumbnail_filename = f"{base_filename}.png"
            thumbnail_path = os.path.join(output_dir, thumbnail_filename)
            
            self.log(f"[封面] 开始下载封面: {thumbnail_filename}")
            
            # 创建不验证SSL证书的上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 下载封面，添加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    request = urllib.request.Request(
                        thumbnail_url,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    
                    with urllib.request.urlopen(request, context=ssl_context, timeout=30) as response:
                        with open(thumbnail_path, 'wb') as f:
                            f.write(response.read())
                    
                    self.log(f"[成功] 封面下载完成: {thumbnail_filename}")
                    return thumbnail_path
                    
                except (urllib.error.URLError, ssl.SSLError, TimeoutError) as e:
                    if attempt < max_retries - 1:
                        self.log(f"[重试] 封面下载失败，第{attempt + 1}次重试: {e}")
                        continue
                    else:
                        raise e
            
        except Exception as e:
            self.log(f"[错误] 封面下载失败: {e}")
            return None

    def start_download(self):
        url = self.url_entry.get().strip()
        download_type = self.format_var.get()
        use_batch = bool(self.batch_text.get("1.0", tk.END).strip())
        download_thumb = self.download_video_thumbnail_var.get()  # 获取封面下载选项
        
        # 如果有批量链接，使用批量模式；否则检查单个链接
        if not use_batch and not url:
            messagebox.showerror("错误", "请输入 YouTube 链接")
            return
        
        # 验证URL
        if not use_batch:
            is_valid, error_msg = self.validate_url(url)
            if not is_valid:
                messagebox.showerror("链接错误", error_msg)
                return
        else:
            # 验证批量链接
            batch_urls = [u.strip() for u in self.batch_text.get("1.0", tk.END).strip().split('\n') if u.strip()]
            if not batch_urls:
                messagebox.showerror("错误", "请输入批量下载链接")
                return
            
            invalid_urls = []
            for batch_url in batch_urls:
                is_valid, error_msg = self.validate_url(batch_url)
                if not is_valid:
                    invalid_urls.append(f"{batch_url}: {error_msg}")
            
            if invalid_urls:
                error_text = "\n".join(invalid_urls[:5])  # 最多显示5个错误
                if len(invalid_urls) > 5:
                    error_text += f"\n...还有{len(invalid_urls) - 5}个错误"
                messagebox.showerror("批量链接错误", error_text)
                return

        self.download_button.config(state=tk.DISABLED, text="下载中...", bg="#6c757d")
        self.progress['value'] = 0
        self.log(f"准备下载: {url if not use_batch else '批量模式'} 格式: {download_type}")

        thread = threading.Thread(target=self.download_worker, args=(url, download_type, use_batch, download_thumb))
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def download_worker(self, url, download_type, use_batch, download_thumb=False):
        try:
            factory = DownloadStrategyFactory()

            def progress_callback(percent, speed, eta):
                try:
                    # 清理ANSI颜色代码的函数
                    import re
                    def clean_ansi(text):
                        if isinstance(text, str):
                            # 移除ANSI颜色代码
                            return re.sub(r'\x1b\[[0-9;]*m', '', text).strip()
                        return text
                    
                    # 清理所有字段的ANSI代码
                    clean_percent = clean_ansi(percent)
                    clean_speed = clean_ansi(speed)
                    clean_eta = clean_ansi(eta)
                    
                    # 解析百分比
                    if isinstance(clean_percent, str):
                        if '%' in clean_percent:
                            p = float(clean_percent.replace('%', ''))
                        else:
                            p = float(clean_percent) if clean_percent != 'N/A' else 0
                    else:
                        p = float(clean_percent) if clean_percent != 'N/A' else 0
                    
                    # 使用更直接的方式更新进度条
                    def update_progress():
                        self.progress['value'] = p
                        self.root.update_idletasks()  # 强制刷新UI
                    
                    # 使用更直接的方式更新状态
                    def update_status():
                        status = f"速度: {clean_speed} | 剩余: {clean_eta} | 进度: {p:.1f}%"
                        self.status_label.config(text=status)
                        self.root.update_idletasks()  # 强制刷新UI
                    
                    # 在主线程中执行更新
                    self.root.after(0, update_progress)
                    self.root.after(0, update_status)
                    
                    # 记录日志（减少频繁日志输出）
                    if int(p) % 5 == 0 or p >= 100:  # 每5%记录一次，或100%时记录
                        self.root.after(0, lambda: self.log(f"[进度] {p:.1f}% - 速度: {clean_speed}"))
                except Exception as ex:
                    # 记录更详细的错误信息以便调试
                    self.root.after(0, lambda: self.log(f"[进度错误] 原始数据: percent='{percent}', speed='{speed}', eta='{eta}', 错误: {ex}"))

            if download_type == "mp4":
                strategy = MP4DownloadStrategy(progress_callback) if not use_batch else factory.get_strategy(download_type)
            elif download_type == "mp3":
                strategy = MP3DownloadStrategy(progress_callback) if not use_batch else factory.get_strategy(download_type)
            else:
                raise ValueError("不支持的格式")

            if use_batch:
                self.handle_batch_download(strategy, download_type, download_thumb)
            else:
                # 获取视频信息生成文件名
                self.log("[信息] 正在获取视频信息...")
                video_info = self.get_video_info(url)
                
                # 更新视频信息显示（新布局）
                title = video_info.get('title', 'Unknown')
                uploader = video_info.get('uploader', 'Unknown')
                height = video_info.get('height', 0)
                
                # 下层：分辨率_视频标题
                resolution_title = f"{height}p_{title}" if height > 0 else title
                self.root.after(0, lambda: self.video_title_label.config(text=resolution_title))
                
                # 底层：@频道信息
                channel_info = f"@{uploader}"
                self.root.after(0, lambda: self.channel_info_label.config(text=channel_info))
                
                # 根据下载格式调整文件名
                if download_type == "mp3":
                    filename = video_info['filename'].rsplit('.', 1)[0] + '.mp3'
                else:
                    filename = video_info['filename']
                
                output_file = os.path.join(self.download_dir, filename)
                self.log(f"[信息] 文件名: {filename}")
                
                # 下载封面（如果选中）
                if download_thumb:
                    self.download_video_thumbnail(video_info, self.download_dir)
                
                strategy.download(url, output_file)
                self.root.after(0, lambda: self.log("[成功] 下载完成！"))
                self.root.after(0, lambda: messagebox.showinfo("完成", "下载完成！"))
                
                # 使用获取到的标题信息
                title = video_info['title'] or 'Unknown'
                add_download_record(title, download_type, output_file, url)
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log(f"[错误] 下载失败: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"下载失败: {error_msg}"))
        finally:
            self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL, text="🚀 开始下载", bg="#dc3545"))

    def handle_batch_download(self, strategy, download_type, download_thumb=False):
        urls = self.batch_text.get("1.0", tk.END).strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        total = len(urls)
        completed_count = 0  # 记录完成的任务数

        for idx, url in enumerate(urls):
            current_num = idx + 1
            self.root.after(0, lambda i=current_num, t=total, u=url: self.log(f"[批量 {i}/{t}] 开始: {u}"))
            
            try:
                # 获取视频信息生成文件名
                video_info = self.get_video_info(url)
                
                # 更新视频信息显示（批量下载新布局）
                title = video_info.get('title', 'Unknown')
                uploader = video_info.get('uploader', 'Unknown')
                height = video_info.get('height', 0)
                
                # 下层：[批量 序号] 分辨率_视频标题
                resolution_title = f"[批量 {current_num}/{total}] {height}p_{title}" if height > 0 else f"[批量 {current_num}/{total}] {title}"
                self.root.after(0, lambda: self.video_title_label.config(text=resolution_title))
                
                # 底层：@频道信息
                channel_info = f"@{uploader}"
                self.root.after(0, lambda: self.channel_info_label.config(text=channel_info))
                
                # 根据下载格式调整文件名
                if download_type == "mp3":
                    filename = video_info['filename'].rsplit('.', 1)[0] + '.mp3'
                else:
                    filename = video_info['filename']
                
                # 如果文件名重复，添加序号
                base_name, ext = os.path.splitext(filename)
                counter = 1
                original_filename = filename
                while os.path.exists(os.path.join(self.download_dir, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                output_file = os.path.join(self.download_dir, filename)
                
                # 下载封面（如果选中）
                if download_thumb:
                    self.download_video_thumbnail(video_info, self.download_dir)
                
                # 为批量下载创建专用的进度回调
                def batch_progress_callback(percent, speed, eta):
                    try:
                        import re
                        def clean_ansi(text):
                            if isinstance(text, str):
                                return re.sub(r'\x1b\[[0-9;]*m', '', text).strip()
                            return text
                        
                        clean_percent = clean_ansi(percent)
                        clean_speed = clean_ansi(speed)
                        clean_eta = clean_ansi(eta)
                        
                        if isinstance(clean_percent, str):
                            if '%' in clean_percent:
                                p = float(clean_percent.replace('%', ''))
                            else:
                                p = float(clean_percent) if clean_percent != 'N/A' else 0
                        else:
                            p = float(clean_percent) if clean_percent != 'N/A' else 0
                        
                        # 更新进度条和状态
                        def update_progress():
                            self.progress['value'] = p
                            status = f"第{current_num}条视频： 速度: {clean_speed} | 进度: {p:.1f}% | 剩余: {clean_eta}"
                            self.status_label.config(text=status)
                            self.root.update_idletasks()
                        
                        self.root.after(0, update_progress)
                        
                        # 记录批量进度日志
                        if int(p) % 10 == 0 or p >= 100:  # 每10%记录一次
                            self.root.after(0, lambda: self.log(f"[批量 {current_num}/{total}] 进度: {p:.1f}% - 速度: {clean_speed}"))
                    except Exception as ex:
                        pass
                
                # 为批量下载创建特殊的策略实例
                from strategies.factory import DownloadStrategyFactory
                factory = DownloadStrategyFactory()
                if download_type == "mp4":
                    batch_strategy = factory.get_strategy(download_type, batch_progress_callback)
                else:
                    batch_strategy = factory.get_strategy(download_type, batch_progress_callback)
                
                batch_strategy.download(url, output_file)
                self.root.after(0, lambda i=current_num, t=total, u=url: self.log(f"[批量 {i}/{t}] 完成: {u}"))
                
                # 使用获取到的标题信息
                title = video_info['title'] or 'Unknown'
                add_download_record(title, download_type, output_file, url)
                
                completed_count += 1  # 成功完成一个任务
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda i=current_num, t=total, err=error_msg: self.log(f"[批量 {i}/{t}] 失败: {err}"))
        
        # 所有批量任务完成后的提示
        if completed_count == total:
            self.root.after(0, lambda: self.log(f"[批量完成] 所有下载任务已完成！成功: {completed_count}/{total}", "success"))
        else:
            self.root.after(0, lambda: self.log(f"[批量完成] 下载任务结束！成功: {completed_count}/{total}，失败: {total - completed_count}", "error"))
        if completed_count == total:
            self.root.after(0, lambda: messagebox.showinfo("批量下载完成", f"所有 {total} 个下载任务已完成！"))
        else:
            self.root.after(0, lambda: messagebox.showwarning("批量下载完成", f"批量下载结束！成功: {completed_count}/{total}，失败: {total - completed_count}"))

def main():
    """主程序入口（静默模式）"""
    def signal_handler(signum, frame):
        """Signal handler for graceful shutdown"""
        # 静默退出，不打印任何信息
        sys.exit(0)
    
    # 注册信号处理器（仅在支持的系统上）
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 在非调试模式下静默启动
        if '--windowed' in sys.argv or not hasattr(sys, 'ps1'):
            # 打包版本静默运行
            pass
        else:
            print("启动 YouTube 下载器...")
            
        root = tk.Tk()
        
        # 确保窗口显示在前台
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(lambda: root.attributes('-topmost', False))
        
        # 创建应用实例
        app = YouTubeDownloaderGUI(root)
        
        if '--windowed' in sys.argv or not hasattr(sys, 'ps1'):
            # 打包版本静默运行
            pass
        else:
            print("GUI界面已创建，请查看您的屏幕")
        
        # 启动主循环
        root.mainloop()
        
    except KeyboardInterrupt:
        # 静默处理中断
        pass
    except Exception as e:
        # 在打包版本中不显示错误对话框和控制台输出
        if '--windowed' not in sys.argv and hasattr(sys, 'ps1'):
            print(f"程序启动失败: {e}")
            import traceback
            traceback.print_exc()
    finally:
        # 确保所有资源被清理（静默模式）
        try:
            if 'app' in locals():
                app.cleanup_processes()
        except:
            pass
        # 静默退出
        sys.exit(0)

if __name__ == "__main__":
    main()