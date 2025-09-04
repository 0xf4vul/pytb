#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
静默退出优化GUI应用模板
版本: v1.0
作者: @橘生淮北

这是一个完整的GUI应用程序模板，展示如何使用静默退出优化组件。
复制此文件作为新项目的起点。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import threading
import subprocess
from typing import Optional

# 导入静默退出基类
try:
    from components.silent_exit_gui_base import SilentExitGUIBase
except ImportError:
    print("错误: 请确保 silent_exit_gui_base.py 位于 components/ 目录中")
    sys.exit(1)


class SilentExitGUITemplate(SilentExitGUIBase):
    """
    静默退出GUI应用模板
    
    这个模板展示了如何使用静默退出优化组件创建专业的GUI应用程序。
    包含常见的GUI元素和最佳实践。
    """
    
    def __init__(self, root: tk.Tk):
        # 初始化基类 - 提供应用标题、图标路径（可选）
        super().__init__(
            root, 
            app_title="静默退出GUI应用模板 - @橘生淮北",
            icon_path="app_icon.ico"  # 如果有图标文件
        )
        
        # 应用状态变量
        self.is_working = False
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="就绪")
        
        # 设置UI
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 配置主窗口
        self.root.geometry("600x450")
        self.root.minsize(500, 400)
        self.root.configure(bg="#f0f0f0")
        
        # 创建主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题区域
        self._create_header(main_frame)
        
        # 控制区域
        self._create_controls(main_frame)
        
        # 进度区域
        self._create_progress_area(main_frame)
        
        # 状态栏
        self._create_status_bar(main_frame)
        
        # 设置键盘快捷键
        self._setup_hotkeys()
    
    def _create_header(self, parent):
        """创建标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 应用标题
        title_label = ttk.Label(
            header_frame,
            text="🚀 GUI应用程序模板",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 版本信息
        version_label = ttk.Label(
            header_frame,
            text="v1.0 - 静默退出优化版",
            font=("Arial", 10),
            foreground="#666666"
        )
        version_label.grid(row=1, column=0, sticky=tk.W)
    
    def _create_controls(self, parent):
        """创建控制区域"""
        # 文件选择区域
        file_frame = ttk.LabelFrame(parent, text="文件操作", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 文件路径输入
        ttk.Label(file_frame, text="文件路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        browse_btn.grid(row=0, column=2, sticky=tk.W)
        
        # 操作按钮区域
        button_frame = ttk.LabelFrame(parent, text="操作", padding="10")
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 按钮
        start_btn = ttk.Button(
            button_frame, 
            text="开始处理", 
            command=self.start_processing,
            style="Accent.TButton"
        )
        start_btn.grid(row=0, column=0, padx=(0, 10))
        
        stop_btn = ttk.Button(
            button_frame, 
            text="停止处理", 
            command=self.stop_processing,
            state="disabled"
        )
        stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        test_btn = ttk.Button(
            button_frame, 
            text="测试后台进程", 
            command=self.test_background_process
        )
        test_btn.grid(row=0, column=2)
        
        # 保存按钮引用
        self.start_btn = start_btn
        self.stop_btn = stop_btn
    
    def _create_progress_area(self, parent):
        """创建进度显示区域"""
        progress_frame = ttk.LabelFrame(parent, text="进度", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 进度文本
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
    
    def _create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # 状态标签
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            foreground="#0066cc"
        )
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 关于按钮
        about_btn = ttk.Button(
            status_frame,
            text="关于",
            command=self.show_about,
            width=8
        )
        about_btn.grid(row=0, column=1, sticky=tk.E)
    
    def _setup_hotkeys(self):
        """设置键盘快捷键"""
        self.root.bind("<Control-o>", lambda e: self.browse_file())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<F1>", lambda e: self.show_about())
    
    # ===========================================
    # 业务逻辑方法
    # ===========================================
    
    def browse_file(self):
        """浏览文件"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("文本文件", "*.txt"),
                ("图片文件", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.update_status(f"已选择文件: {os.path.basename(file_path)}")
    
    def start_processing(self):
        """开始处理"""
        if not self.file_path_var.get():
            messagebox.showwarning("警告", "请先选择一个文件")
            return
        
        if self.is_working:
            return
        
        self.is_working = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # 在后台线程中执行处理
        thread = threading.Thread(target=self._process_worker, daemon=True)
        thread.start()
    
    def stop_processing(self):
        """停止处理"""
        self.is_working = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status("处理已停止")
        self.update_progress(0, "已停止")
    
    def test_background_process(self):
        """测试后台进程管理"""
        # 使用基类提供的方法运行后台进程
        if os.name == 'nt':
            # Windows: 运行ping命令
            process = self.run_background_command(['ping', 'localhost', '-n', '3'])
        else:
            # Unix/Linux: 运行ping命令
            process = self.run_background_command(['ping', '-c', '3', 'localhost'])
        
        if process:
            self.update_status(f"启动了后台进程: PID {process.pid}")
        else:
            self.update_status("后台进程启动失败")
    
    def _process_worker(self):
        """处理工作线程"""
        try:
            file_path = self.file_path_var.get()
            file_size = os.path.getsize(file_path)
            
            self.update_status(f"正在处理: {os.path.basename(file_path)}")
            
            # 模拟处理过程
            for i in range(101):
                if not self.is_working:
                    break
                
                # 模拟耗时操作
                import time
                time.sleep(0.05)
                
                # 更新进度
                self.update_progress(i, f"处理中... {i}%")
            
            if self.is_working:
                self.update_status("处理完成!")
                self.update_progress(100, "完成")
                messagebox.showinfo("完成", "文件处理完成!")
            
        except Exception as e:
            self.update_status(f"处理失败: {str(e)}")
            messagebox.showerror("错误", f"处理失败:\n{str(e)}")
        finally:
            if self.is_working:
                self.is_working = False
                self.root.after(0, lambda: self.start_btn.config(state="normal"))
                self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
    
    def update_status(self, message: str):
        """更新状态信息（线程安全）"""
        self.root.after(0, lambda: self.status_var.set(message))
    
    def update_progress(self, value: float, text: str = None):
        """更新进度（线程安全）"""
        self.root.after(0, lambda: self.progress_var.set(value))
        if text:
            self.root.after(0, lambda: self.progress_label.config(text=text))
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """静默退出GUI应用模板 v1.0

作者: @橘生淮北
基于: 静默退出优化组件库

特性:
• 无感知程序关闭
• 智能进程管理  
• 专业UI设计
• 完整错误处理

这是一个展示如何使用静默退出优化组件的完整模板。
"""
        messagebox.showinfo("关于", about_text)
    
    # ===========================================
    # 重写基类方法（可选）
    # ===========================================
    
    def cleanup_processes(self):
        """自定义清理逻辑"""
        # 停止正在进行的操作
        self.is_working = False
        
        # 在这里添加你的自定义清理逻辑
        # 例如: 保存设置、清理临时文件等
        
        # 调用基类清理
        super().cleanup_processes()


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用实例
    app = SilentExitGUITemplate(root)
    
    # 运行应用
    try:
        root.mainloop()
    except KeyboardInterrupt:
        # 处理 Ctrl+C
        app.on_closing()


if __name__ == "__main__":
    main()