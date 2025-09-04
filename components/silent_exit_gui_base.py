# 静默退出优化 GUI 基类 - 公共开发组件
# 版本: v1.0
# 作者: @橘生淮北
# 功能: 为GUI应用程序提供完全静默的退出体验

import tkinter as tk
import os
import sys
import atexit
import signal
import subprocess
import threading
from typing import List, Optional

class SilentExitGUIBase:
    """
    静默退出优化GUI基类
    
    提供以下核心功能：
    1. 静默程序关闭（无黑色窗口闪现）
    2. 智能进程管理
    3. 优雅的资源清理
    4. 跨平台兼容性
    
    使用方法：
    class MyApp(SilentExitGUIBase):
        def __init__(self, root):
            super().__init__(root)
            self.setup_ui()
    """
    
    def __init__(self, root: tk.Tk, app_title: str = "GUI Application", icon_path: Optional[str] = None):
        """
        初始化静默退出GUI基类
        
        Args:
            root: Tkinter根窗口
            app_title: 应用程序标题
            icon_path: 图标文件路径（可选）
        """
        self.root = root
        self.root.title(app_title)
        
        # 子进程列表，用于跟踪需要清理的进程
        self.child_processes: List[subprocess.Popen] = []
        
        # 设置窗口图标（如果提供）
        if icon_path:
            self._set_window_icon(icon_path)
        
        # 注册程序退出时的清理函数
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup_processes)
        
        # 注册信号处理器（仅在支持的系统上）
        self._setup_signal_handlers()
    
    def _set_window_icon(self, icon_path: str):
        """
        智能设置窗口图标
        
        处理开发环境和打包后的不同路径问题
        """
        icon_paths_to_try = [
            icon_path,  # 原始路径
            os.path.join(os.path.dirname(sys.argv[0]), icon_path),  # exe所在目录
            os.path.join(os.getcwd(), icon_path),  # 当前工作目录
            os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), icon_path),  # PyInstaller打包路径
        ]
        
        for path in icon_paths_to_try:
            if os.path.exists(path):
                try:
                    self.root.iconbitmap(path)
                    return True
                except Exception:
                    continue
        
        # 如果所有路径都失败，静默忍略
        return False

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            """静默信号处理"""
            self._silent_exit()
        
        try:
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, signal_handler)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, signal_handler)
        except Exception:
            pass  # 某些环境可能不支持信号处理
    
    def on_closing(self):
        """
        程序关闭时的清理工作（静默模式）
        
        核心优化：
        1. 立即隐藏窗口避免闪现
        2. 静默清理所有资源
        3. 优雅退出程序
        """
        try:
            # 立即隐藏窗口，避免关闭时的视觉闪现
            self.root.withdraw()
            
            # 静默清理所有进程和资源
            self.cleanup_processes()
            
            # 优雅关闭程序
            self.root.quit()
            self.root.destroy()
        except Exception:
            # 确保程序能够正常关闭，静默处理异常
            self._force_exit()
    
    def cleanup_processes(self):
        """
        清理所有子进程和资源（静默模式）
        
        优化特性：
        1. 快速终止子进程（2秒超时）
        2. 使用 CREATE_NO_WINDOW 标志避免窗口闪现
        3. 静默处理所有异常
        4. 跨平台兼容
        """
        try:
            # 终止所有子进程
            for process in self.child_processes:
                try:
                    if process.poll() is None:  # 进程仍在运行
                        process.terminate()
                        process.wait(timeout=2)  # 快速等待
                except Exception:
                    try:
                        process.kill()  # 强制终止
                    except Exception:
                        pass
            
            # 清空子进程列表
            self.child_processes.clear()
            
            # Windows 特定清理
            if os.name == 'nt':
                self._cleanup_windows_processes()
                
        except Exception:
            pass  # 静默失败，不影响程序关闭
    
    def _cleanup_windows_processes(self):
        """Windows 特定的进程清理"""
        try:
            # 静默清理常见的子进程
            common_processes = ['yt-dlp.exe', 'ffmpeg.exe', 'youtube-dl.exe']
            
            for process_name in common_processes:
                try:
                    subprocess.run(
                        ['taskkill', '/f', '/im', process_name],
                        capture_output=True,
                        timeout=3,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except Exception:
                    pass
        except Exception:
            pass
    
    def _silent_exit(self):
        """强制静默退出"""
        try:
            self.cleanup_processes()
            sys.exit(0)
        except Exception:
            os._exit(0)
    
    def _force_exit(self):
        """强制退出（最后手段）"""
        try:
            self.root.withdraw()
            self.root.destroy()
        except Exception:
            pass
        finally:
            sys.exit(0)
    
    def add_child_process(self, process: subprocess.Popen):
        """
        添加子进程到管理列表
        
        Args:
            process: 需要管理的子进程
        """
        self.child_processes.append(process)
    
    def remove_child_process(self, process: subprocess.Popen):
        """
        从管理列表中移除子进程
        
        Args:
            process: 需要移除的子进程
        """
        try:
            self.child_processes.remove(process)
        except ValueError:
            pass
    
    def run_background_command(self, command: List[str], **kwargs) -> Optional[subprocess.Popen]:
        """
        运行后台命令并自动管理进程
        
        Args:
            command: 要执行的命令列表
            **kwargs: 传递给 subprocess.Popen 的额外参数
            
        Returns:
            subprocess.Popen 对象或 None（如果失败）
        """
        try:
            # 设置默认参数以避免窗口闪现
            default_kwargs = {
                'capture_output': True,
                'creationflags': subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            }
            default_kwargs.update(kwargs)
            
            process = subprocess.Popen(command, **default_kwargs)
            self.add_child_process(process)
            return process
        except Exception:
            return None
    
    def is_packaged_app(self) -> bool:
        """
        检测是否为打包应用程序
        
        Returns:
            bool: 如果是打包应用返回 True
        """
        return (
            getattr(sys, 'frozen', False) or  # PyInstaller
            '--windowed' in sys.argv or      # 明确指定
            not hasattr(sys, 'ps1')          # 非交互模式
        )
    
    def setup_ui(self):
        """
        子类应重写此方法来设置UI
        
        这是一个抽象方法，子类必须实现
        """
        raise NotImplementedError("子类必须实现 setup_ui 方法")

# 使用示例和测试代码
def create_sample_app():
    """创建示例应用程序"""
    
    class SampleApp(SilentExitGUIBase):
        def setup_ui(self):
            # 设置窗口
            self.root.geometry("400x300")
            self.root.configure(bg="#f0f0f0")
            
            # 标题
            title_label = tk.Label(
                self.root,
                text="静默退出优化演示",
                font=("Arial", 16, "bold"),
                bg="#f0f0f0"
            )
            title_label.pack(pady=20)
            
            # 说明文本
            info_text = """
这是一个使用静默退出优化基类的示例应用程序。

特性：
• 关闭时无黑色窗口闪现
• 自动清理所有子进程
• 优雅的资源管理
• 跨平台兼容

点击右上角的 X 按钮体验静默关闭！
            """
            
            info_label = tk.Label(
                self.root,
                text=info_text,
                font=("Arial", 10),
                bg="#f0f0f0",
                justify="left"
            )
            info_label.pack(pady=20, padx=20)
            
            # 测试按钮
            test_button = tk.Button(
                self.root,
                text="测试后台进程",
                command=self.test_background_process,
                font=("Arial", 12),
                bg="#007bff",
                fg="white",
                relief="flat",
                padx=20,
                pady=10
            )
            test_button.pack(pady=10)
    
        def test_background_process(self):
            """测试后台进程管理"""
            # 运行一个简单的后台命令
            process = self.run_background_command(['ping', 'localhost', '-n', '5'])
            if process:
                print(f"启动了后台进程: PID {process.pid}")
    
    # 创建并运行应用
    root = tk.Tk()
    app = SampleApp(root, "静默退出优化演示", None)
    app.setup_ui()
    
    return root, app

if __name__ == "__main__":
    # 运行示例应用程序
    root, app = create_sample_app()
    root.mainloop()