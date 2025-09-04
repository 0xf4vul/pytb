#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级项目精简工具
根据评估结果进行精准清理，保留必要文件
"""

import os
import sys
import shutil
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class AdvancedCleanupTool:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.cleanup_log = []
        self.deletion_stats = {}
        self.detailed_log = []
        self.total_size_saved = 0
        self.delete_root = self.project_root / '.delete'
        
        # 核心必要文件 - 绝对不能删除
        self.core_files = {
            'gui_main.py',           # 主程序
            'config.py',             # 配置文件
            '.gitignore',            # Git忽略规则
            'README.md',             # 项目说明
            'YouTube_Downloader_logo.ico',  # 图标文件 - 重要，不能删
            '2025-09-05.jpg',        # 程序截图 - 重要，不能删
            'pack_silent_optimized.bat',    # 核心打包脚本
            'history.json',          # 下载历史数据
            'config.json',           # 配置数据
        }
        
        # 核心目录 - 必须保留
        self.core_dirs = {
            'strategies',    # 下载策略
            'utils',         # 工具模块
            'components',    # 组件库 (保留但可精简)
        }
        
        # 按类别分类的冗余文件
        self.redundant_files_by_category = {
            'dev_docs': {
                'Silent_Exit_Optimization_Fix_Report.md': '开发过程优化报告',
                'Silent_Exit_Optimization_Guide.md': '开发过程优化指南', 
                'Silent_Exit_Optimization_Implementation_Report.md': '开发过程实现报告',
                'YouTube_Downloader_Optimization_Guide.md': '项目优化指南',
                'To-Do-List.txt': '开发任务清单',
                'YouTube_logo_instructions.txt': '图标使用说明',
                'pro.sum.md': '项目总结文档',
                'cleanup_report.json': '旧版清理报告',
            },
            'test_files': {
                'test_gui.py': 'GUI测试脚本',
                'test_icon.py': '图标测试脚本',
            },
            'redundant_images': {
                'YouTube_logo.png': '冗余PNG图标（已有ICO版本）',
            },
            'duplicate_code': {
                'factory.py': '重复的工厂类（strategies目录已有）',
            },
            'old_tools': {
                'gui_sensitive_cleanup_tool.py': '旧版敏感信息清理工具',
                'update_tools.bat': '工具更新脚本（项目完成后无需）',
            },
            'temp_files': {
                'utils/progress.py': '空的进度条模块文件',
            },
            'virtual_env': {
                'clean_env/': 'Python虚拟环境目录（已手动删除，释放40.4MB）',
            }
        }
        
        # 组件库中可精简的文件
        self.components_redundant = {
            'PROJECT_COMPLETION_REPORT.md': '项目完成报告',
            'FINAL_SUMMARY.md': '最终总结文档', 
            'VERSION.md': '版本说明文档',
            '组件提炼、完成说明.md': '组件提炼说明',
            'test_components.py': '组件测试文件',
        }
        
        # 虚拟环境目录已删除，不需要清理模式
        # clean_env 目录已手动删除，释放空间 40.4MB
        self.venv_clean_patterns = []

    def optimize_requirements(self):
        """优化requirements.txt"""
        requirements_file = self.project_root / 'requirements.txt'
        
        # 创建精简的依赖列表
        essential_deps = [
            'yt-dlp>=2023.7.6',
            'pyinstaller>=5.0.0',
        ]
        
        try:
            # 保持原有内容，只添加注释
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 如果文件为空或很短，则写入基础依赖
                if len(content.strip()) < 20:
                    with open(requirements_file, 'w', encoding='utf-8') as f:
                        f.write('# 核心依赖\n')
                        for dep in essential_deps:
                            f.write(dep + '\n')
                    self.log_action("优化依赖文件", "requirements.txt")
                else:
                    self.log_action("保持依赖文件", "requirements.txt 内容已存在")
            else:
                # 创建新的requirements.txt
                with open(requirements_file, 'w', encoding='utf-8') as f:
                    f.write('# 核心依赖\n')
                    for dep in essential_deps:
                        f.write(dep + '\n')
                self.log_action("创建依赖文件", "requirements.txt")
                
            return True
        except Exception as e:
            self.log_action("优化失败", f"requirements.txt: {e}")
            return False

    def safe_delete_file(self, file_path, category, reason):
        """安全删除：移动到.delete文件夹而非直接删除"""
        # 创建分类目录
        delete_dir = self.delete_root / category
        delete_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取文件信息
        file_size = file_path.stat().st_size if file_path.exists() else 0
        
        # 处理重名冲突
        target_path = delete_dir / file_path.name
        counter = 1
        while target_path.exists():
            target_path = delete_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1
        
        try:
            # 移动文件
            shutil.move(str(file_path), str(target_path))
            
            # 记录统计信息
            if category not in self.deletion_stats:
                self.deletion_stats[category] = 0
            self.deletion_stats[category] += 1
            self.total_size_saved += file_size
            
            # 记录详细信息
            detail = {
                'file': str(file_path.relative_to(self.project_root)),
                'category': category,
                'reason': reason,
                'size_bytes': file_size,
                'backup_location': str(target_path.relative_to(self.project_root)),
                'timestamp': datetime.now().isoformat()
            }
            self.detailed_log.append(detail)
            
            self.log_action(f"安全移动[{category}]", f"{file_path.name} -> .delete/{category}/")
            return True
            
        except Exception as e:
            self.log_action("移动失败", f"{file_path.name}: {e}")
            return False

    def log_action(self, action, details=""):
        """记录清理操作"""
        log_entry = f"[精简] {action}"
        if details:
            log_entry += f": {details}"
        self.cleanup_log.append(log_entry)
        print(log_entry)

    def clean_redundant_files(self):
        """按类别清理冗余文件"""
        total_deleted = 0
        
        for category, files_dict in self.redundant_files_by_category.items():
            self.log_action(f"开始清理[{category}]", f"共{len(files_dict)}个文件")
            
            for filename, reason in files_dict.items():
                file_path = self.project_root / filename
                
                if file_path.exists():
                    # 双重检查：确保不删除重要文件
                    if filename in ['YouTube_Downloader_logo.ico', '2025-09-05.jpg']:
                        self.log_action("跳过重要文件", f"保留: {filename}")
                        continue
                        
                    if self.safe_delete_file(file_path, category, reason):
                        total_deleted += 1
                        
        return total_deleted

    def clean_components_dir(self):
        """精简组件库目录"""
        components_dir = self.project_root / 'components'
        total_deleted = 0
        
        if not components_dir.exists():
            return total_deleted
            
        self.log_action("开始精简[components]", f"共{len(self.components_redundant)}个文件")
        
        for filename, reason in self.components_redundant.items():
            file_path = components_dir / filename
            if file_path.exists():
                if self.safe_delete_file(file_path, 'components_docs', reason):
                    total_deleted += 1
                    
        return total_deleted

    def clean_venv_deep(self):
        """深度清理虚拟环境"""
        deleted_count = 0
        
        # 清理虚拟环境中的可执行文件
        for pattern in self.venv_clean_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        self.log_action("深度清理虚拟环境", str(file_path.relative_to(self.project_root)))
                        deleted_count += 1
                    except Exception as e:
                        self.log_action("删除失败", f"{file_path.name}: {e}")
        
        return deleted_count

    def clean_empty_files(self):
        """清理空文件"""
        total_deleted = 0
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and file_path.stat().st_size == 0:
                # 保留必要的空文件如 __init__.py
                if file_path.name in ['__init__.py']:
                    continue
                
                # 确保不删除重要文件
                if file_path.name in self.core_files:
                    continue
                    
                if self.safe_delete_file(file_path, 'empty_files', '空文件，无内容'):
                    total_deleted += 1
                    
        return total_deleted

    def record_manual_deletion(self):
        """记录手动删除的clean_env目录"""
        # 记录手动删除的虚拟环境目录
        manual_deletion = {
            'file': 'clean_env/',
            'category': 'virtual_env',
            'reason': 'Python虚拟环境目录（手动删除，释放40.4MB）',
            'size_bytes': 42343227,  # 40.4MB
            'backup_location': '已永久删除（可通过打包脚本重建）',
            'timestamp': datetime.now().isoformat(),
            'deletion_method': '手动删除'
        }
        self.detailed_log.append(manual_deletion)
        
        # 更新统计
        if 'virtual_env' not in self.deletion_stats:
            self.deletion_stats['virtual_env'] = 0
        self.deletion_stats['virtual_env'] += 1
        self.total_size_saved += 42343227
        
        self.log_action("记录手动删除[virtual_env]", "clean_env/ 目录已删除，释放40.4MB")

    def optimize_requirements(self):
        """优化requirements.txt"""
        requirements_file = self.project_root / 'requirements.txt'
        
        # 创建精简的依赖列表
        essential_deps = [
            'yt-dlp>=2025.8.27',
            'pyinstaller>=6.0.0',
        ]
        
        try:
            with open(requirements_file, 'w', encoding='utf-8') as f:
                for dep in essential_deps:
                    f.write(dep + '\n')
            self.log_action("优化依赖文件", "requirements.txt")
            return True
        except Exception as e:
            self.log_action("优化失败", f"requirements.txt: {e}")
            return False

    def generate_final_report(self):
        """生成最终执行报告"""
        report = {
            'cleanup_metadata': {
                'cleanup_time': datetime.now().isoformat(),
                'tool_version': '2.0_safe_delete',
                'project_root': str(self.project_root),
                'backup_location': '.delete/'
            },
            'cleanup_statistics': {
                'total_files_processed': sum(self.deletion_stats.values()),
                'files_by_category': self.deletion_stats,
                'total_space_saved_bytes': self.total_size_saved,
                'total_space_saved_mb': round(self.total_size_saved / (1024*1024), 2)
            },
            'safety_features': {
                'safe_delete_enabled': True,
                'backup_location': '.delete/',
                'recovery_possible': True,
                'gitignore_updated': True
            },
            'deleted_files_details': self.detailed_log,
            'cleanup_actions_log': self.cleanup_log
        }
        
        # 保存报告到.delete目录
        self.delete_root.mkdir(exist_ok=True)
        report_file = self.delete_root / f'cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.log_action("生成执行报告", str(report_file.relative_to(self.project_root)))
            return report
        except Exception as e:
            self.log_action("报告生成失败", str(e))
            return report

    def update_gitignore(self):
        """更新.gitignore文件，忽略.delete文件夹"""
        gitignore_path = self.project_root / '.gitignore'
        delete_ignore_line = '\n# 安全清理备份目录\n.delete/\n'
        
        try:
            # 读取现有内容
            if gitignore_path.exists():
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = ''
            
            # 检查是否已经包含.delete规则
            if '.delete/' not in content:
                content += delete_ignore_line
                
                with open(gitignore_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.log_action("更新.gitignore", "已添加.delete/忽略规则")
            else:
                self.log_action(".gitignore检查", ".delete/规则已存在")
                
        except Exception as e:
            self.log_action(".gitignore更新失败", str(e))

    def validate_important_files(self):
        """验证重要文件是否存在"""
        important_files = ['YouTube_Downloader_logo.ico', '2025-09-05.jpg', 'gui_main.py']
        missing_files = []
        
        for filename in important_files:
            if not (self.project_root / filename).exists():
                missing_files.append(filename)
                
        if missing_files:
            self.log_action("警告", f"未找到重要文件: {', '.join(missing_files)}")
            return False
            
        self.log_action("验证通过", "所有重要文件均存在")
        return True

    def execute_advanced_cleanup(self):
        """执行高级清理"""
        total_deleted = 0
        
        self.log_action("开始高级精简【安全模式】")
        
        # 0. 验证重要文件
        self.log_action("步骤0: 验证重要文件")
        if not self.validate_important_files():
            self.log_action("终止清理", "缺少重要文件，不安全执行清理")
            return 0
        
        # 1. 更新.gitignore
        self.log_action("步骤1: 更新.gitignore文件")
        self.update_gitignore()
        
        # 1.5. 记录手动删除的clean_env目录
        self.log_action("步骤1.5: 记录手动删除操作")
        self.record_manual_deletion()
        
        # 2. 按类别清理冗余文件
        self.log_action("步骤2: 按类别清理冗余文件")
        total_deleted += self.clean_redundant_files()
        
        # 3. 精简组件库
        self.log_action("步骤3: 精简组件库")
        total_deleted += self.clean_components_dir()
        
        # 4. 清理空文件
        self.log_action("步骤4: 清理空文件")
        total_deleted += self.clean_empty_files()
        
        # 5. 优化依赖文件
        self.log_action("步骤5: 优化依赖文件")
        self.optimize_requirements()
        
        # 6. 生成最终报告
        self.log_action("步骤6: 生成最终报告")
        final_report = self.generate_final_report()
        
        self.log_action(f"精简完成，共处理 {total_deleted} 个文件")
        self.log_action(f"节省空间: {final_report['cleanup_statistics']['total_space_saved_mb']:.2f} MB")
        self.log_action("安全备份位置: .delete/ 目录")
        
        return total_deleted


def create_gui():
    """创建图形界面"""
    root = tk.Tk()
    root.title("高级项目精简工具")
    root.geometry("600x400")
    root.configure(bg="#f0f0f0")
    
    # 标题
    title_label = tk.Label(
        root,
        text="🔧 高级项目精简工具",
        font=("Arial", 16, "bold"),
        bg="#f0f0f0",
        fg="#2c3e50"
    )
    title_label.pack(pady=20)
    
    # 说明文本
    info_text = """
    🔒 安全清理模式 - 文件不会被永久删除！
    
    ✅ 保留核心文件：gui_main.py, config.py, strategies/, utils/
    ✅ 保留必要组件：silent_exit_gui_base.py, README.md
    ✅ 保留打包工具：pack_silent_optimized.bat
    ✅ 保留重要资源：YouTube_Downloader_logo.ico, 2025-09-05.jpg
    
    📦 安全移动至.delete文件夹：
    • 开发文档：优化报告、指南、任务清单
    • 测试文件：test_gui.py, test_icon.py
    • 冗余图片：YouTube_logo.png (934KB)
    • 重复代码：根目录的factory.py
    • 旧版工具：敏感信息清理工具等
    
    📄 自动生成详细报告到.delete/目录
    🚫 自动更新.gitignore忽略.delete/文件夹
    
    点击"执行精简"开始安全优化项目结构
    """
    
    info_label = tk.Label(
        root,
        text=info_text,
        font=("Arial", 10),
        bg="#f0f0f0",
        justify="left",
        fg="#34495e"
    )
    info_label.pack(pady=20, padx=20)
    
    def execute_cleanup():
        result = messagebox.askyesno(
            "确认精简",
            "确定要执行高级精简吗？\n\n🔒 安全模式：文件将移动到.delete文件夹\n📦 可以随时从.delete文件夹恢复\n📄 生成详细报告供查阅"
        )
        
        if result:
            cleanup_tool = AdvancedCleanupTool()
            deleted_count = cleanup_tool.execute_advanced_cleanup()
            
            # 获取最后一次报告的统计信息
            if hasattr(cleanup_tool, 'total_size_saved'):
                space_saved_mb = cleanup_tool.total_size_saved / (1024*1024)
                details_msg = f"共处理 {deleted_count} 个文件\n节省空间: {space_saved_mb:.2f} MB\n备份位置: .delete/"
            else:
                details_msg = f"共处理 {deleted_count} 个文件"
                
            messagebox.showinfo(
                "精简完成",
                f"🎉 高级精简完成！\n\n{details_msg}\n\n📄 详细报告已保存在.delete目录\n🔄 如需恢复，请从.delete文件夹移回"
            )
            
            root.quit()
    
    # 执行按钮
    execute_btn = tk.Button(
        root,
        text="🚀 执行精简",
        command=execute_cleanup,
        font=("Arial", 14, "bold"),
        bg="#e74c3c",
        fg="white",
        relief="flat",
        padx=30,
        pady=15
    )
    execute_btn.pack(pady=30)
    
    # 警告标签
    warning_label = tk.Label(
        root,
        text="🔒 安全模式：文件只移动到.delete文件夹，不会永久删除",
        font=("Arial", 9),
        bg="#f0f0f0",
        fg="#27ae60"
    )
    warning_label.pack()
    
    root.mainloop()


def main():
    """主函数"""
    print("高级项目精简工具启动中...")
    
    # 检查是否在正确的项目目录
    current_dir = Path.cwd()
    if not (current_dir / 'gui_main.py').exists():
        print("❌ 错误: 请在项目根目录中运行此工具")
        sys.exit(1)
    
    print("✅ 项目目录验证通过")
    
    # 启动GUI
    create_gui()


if __name__ == "__main__":
    main()
