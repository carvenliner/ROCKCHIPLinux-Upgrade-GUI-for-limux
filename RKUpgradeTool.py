import sys
import os
import shlex
import subprocess
import tkinter as tk
from tkinter import filedialog
from PyQt5.QtCore import Qt, QSize, QPoint, QTimer # 添加 QTimer
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QLabel, QMenu, QMenuBar, QAction, QWidget, QProgressBar,
    QPushButton, QSplitter, QHeaderView, QTabWidget, QLineEdit,
    QDialog  # 添加此行
)

def get_script_dir():
    """获取脚本所在目录的绝对路径"""
    return os.path.dirname(os.path.abspath(__file__))

def request_root():
    """请求root权限并保持工作目录"""
    if os.getuid() != 0:
        script_path = os.path.abspath(__file__)
        script_dir = get_script_dir()
        
        # 构造提权命令（保留工作目录和环境变量）
        cmd = [
            'pkexec',
            '--disable-internal-agent',  # 强制显示图形对话框
            'sh', '-c',
            f'cd {shlex.quote(script_dir)} && '
            f'export DISPLAY={shlex.quote(os.getenv("DISPLAY", ":0"))} && '
            f'export XAUTHORITY={shlex.quote(os.getenv("XAUTHORITY", os.path.expanduser("~/.Xauthority")))} && '
            f'{sys.executable} {shlex.quote(script_path)}'
        ]
        
        try:
            # 执行提权命令
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(None, "错误", f"权限请求失败: {e}")
        sys.exit(0)



    
class PartitionDialog(QDialog):
    def __init__(self, parent=None):
    

        super().__init__(parent)
        self.setWindowTitle("分区管理")
        self.setFixedSize(200, 150)
        
        layout = QVBoxLayout()
        
        self.flash_btn = QPushButton("刷入分区")
        self.backup_btn = QPushButton("备份分区")
        self.erase_btn = QPushButton("擦除分区")
        
        for btn in [self.flash_btn, self.backup_btn, self.erase_btn]:
            btn.setFixedHeight(35)
        
        layout.addWidget(self.flash_btn)
        layout.addWidget(self.backup_btn)
        layout.addWidget(self.erase_btn)
        self.setLayout(layout)


class RockusbGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_data()
        self.refresh_devices()  # 初始化时主动刷新设备列表

    def init_data(self):
        self.selected_partition = None

        self.current_device = ""
        self.firmware_path = ""

    def init_ui(self):
        self.setWindowTitle("瑞芯微升级工具")
        self.resize(1100, 750)
        
        # 创建标签页容器
        tab_widget = QTabWidget()
        
        # 创建分区管理标签页
        partition_tab = self.create_partition_tab()
        tab_widget.addTab(partition_tab, "分区管理")
        
        # 创建设备高级管理标签页
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "设备管理")
        
        self.setCentralWidget(tab_widget)
        self.init_menubar()

    def create_partition_tab(self):
        """创建分区管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 顶部操作栏
        top_layout = QHBoxLayout()
        
        # 设备选择栏 + 刷新按钮
        device_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(300)
        
        # 新增刷新按钮
        refresh_btn = QPushButton("刷新设备")
        refresh_btn.setFixedSize(QSize(100, 30))
        refresh_btn.clicked.connect(self.refresh_devices)  # 绑定刷新方法
        
        device_layout.addWidget(QLabel("当前设备:"))
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(refresh_btn)  # 添加按钮到布局
        
        # 重启操作
        reboot_layout = QHBoxLayout()
        self.reboot_combo = QComboBox()
        self.reboot_combo.addItems(["设备操作", "重启到系统", "进入Loader模式"])
        self.reboot_combo.setFixedWidth(180)
        reboot_layout.addWidget(QLabel("重启控制:"))
        reboot_layout.addWidget(self.reboot_combo)
        
        top_layout.addLayout(device_layout)
        top_layout.addStretch()
        top_layout.addLayout(reboot_layout)
        layout.addLayout(top_layout)

        # 操作按钮区域
        btn_layout = QHBoxLayout()
        self.flash_button = QPushButton("批量刷入")
        self.backup_button = QPushButton("批量备份")
        self.erase_button = QPushButton("批量清除")  # 新增按钮
        self.upgrade_button = QPushButton("固件升级")

        for btn in [self.flash_button, self.backup_button, self.upgrade_button, self.erase_button]:
            btn.setFixedSize(QSize(120, 35))  # 统一按钮尺寸
        btn_layout.addWidget(self.flash_button)
        btn_layout.addWidget(self.backup_button)
        btn_layout.addWidget(self.erase_button)  # 添加按钮到布局
        btn_layout.addWidget(self.upgrade_button)
 
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 修改后的复选框操作按钮布局（将全选和反选按钮放在同一行）
        checkbox_layout = QHBoxLayout()
        self.toggle_select_btn = QPushButton("全选")
        self.toggle_select_btn.setFixedSize(QSize(80, 25))
        self.toggle_select_btn.clicked.connect(self.toggle_all_selection)

        self.inverse_select_btn = QPushButton("反选")
        self.inverse_select_btn.setFixedSize(QSize(80, 25))
        self.inverse_select_btn.clicked.connect(self.toggle_inverse_selection)

        checkbox_layout.addWidget(self.toggle_select_btn)
        checkbox_layout.addWidget(self.inverse_select_btn)  # 将反选按钮移到同一行
        checkbox_layout.addStretch()
        layout.addLayout(checkbox_layout)
        


        # 主内容区域
        splitter = QSplitter(Qt.Vertical)
        
        # 分区表格
        self.partition_table = QTableWidget()
        self.init_partition_table()
        
        # 日志区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(50)
        
        splitter.addWidget(self.partition_table)
        splitter.addWidget(self.log_text)
        splitter.setSizes([400, 280])
        layout.addWidget(splitter, 1)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)

        # 连接信号
        self.device_combo.currentIndexChanged.connect(self.device_changed)
        self.flash_button.clicked.connect(self.batch_flash_partitions)
        self.backup_button.clicked.connect(self.batch_backup_partitions)
        self.upgrade_button.clicked.connect(self.upgrade_firmware)
        self.reboot_combo.currentIndexChanged.connect(self.handle_reboot)

        # 连接信号
        self.erase_button.clicked.connect(self.batch_erase_partitions)  # 新增连接
        return tab
    
    def batch_erase_partitions(self):
        """批量擦除选中的分区"""
        selected = []
        for row in range(self.partition_table.rowCount()):
            if self.partition_table.item(row, 0).checkState() == Qt.Checked:
                selected.append(row)

        if not selected:
            self.log_text.append("错误：请先选择要擦除的分区")
            return

        self.progress_bar.setValue(0)
        total = len(selected)
        for i, row in enumerate(selected, 1):
            # 获取分区信息（LBA和EraseCount）
            lba_start = self.partition_table.item(row, 2).text()  # 第2列是LBA
            erase_count = self.partition_table.item(row, 3).text()  # 第3列是Size（即EraseCount）

            # 执行擦除命令（直接使用原始十六进制值）
            cmd = f"./upgrade_tool EL {lba_start} {erase_count}"
            output = self.run_command(cmd)
            if "Erase OK" in output:
                self.log_text.append(f"分区 {self.partition_table.item(row,4).text()} 擦除成功")
            else:
                self.log_text.append(f"分区 {self.partition_table.item(row,4).text()} 擦除失败")

            # 更新进度条
            self.progress_bar.setValue(int(i / total * 100))
        self.log_text.append("批量擦除操作完成")

    def toggle_inverse_selection(self):
        """反选所有分区的选中状态"""
        for row in range(self.partition_table.rowCount()):
            item = self.partition_table.item(row, 0)
            current_state = item.checkState()
            new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
            item.setCheckState(new_state)
        
        # 更新全选按钮文本
        self._update_select_button_text()

    def _update_select_button_text(self):
        """更新全选按钮文本（复用原逻辑）"""
        is_all_selected = all(
            self.partition_table.item(row, 0).checkState() == Qt.Checked
            for row in range(self.partition_table.rowCount())
        )
        self.toggle_select_btn.setText("取消全选" if is_all_selected else "全选")

    def toggle_all_selection(self):
        """切换全选/取消全选状态"""
        is_all_selected = all(
            self.partition_table.item(row, 0).checkState() == Qt.Checked
            for row in range(self.partition_table.rowCount())
        )
        
        new_state = Qt.Unchecked if is_all_selected else Qt.Checked
        for row in range(self.partition_table.rowCount()):
            self.partition_table.item(row, 0).setCheckState(new_state)
        
        self._update_select_button_text()  # 复用更新方法

    def create_advanced_tab(self):
        """创建设备高级管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # SN管理区域
        sn_group = QWidget()
        sn_layout = QHBoxLayout(sn_group)
        self.sn_input = QLineEdit()
        self.sn_input.setPlaceholderText("输入SN号码")
        write_sn_btn = QPushButton("写入SN")
        write_sn_btn.setFixedSize(QSize(100, 30))
        write_sn_btn.clicked.connect(self.write_sn)
        sn_layout.addWidget(QLabel("SN管理:"))
        sn_layout.addWidget(self.sn_input)
        sn_layout.addWidget(write_sn_btn)
        sn_layout.addWidget(QPushButton("读取SN", clicked=self.read_sn))
        layout.addWidget(sn_group)

        # 命令按钮区域
        cmd_group = QWidget()
        cmd_layout = QGridLayout(cmd_group)
        cmd_buttons = [
            ("切换存储设备", self.switch_storage, 0, 0),
            ("读取Flash ID", self.read_flash_id, 0, 1),
            ("读取Flash信息", self.read_flash_info, 1, 0),
            ("读取芯片信息", self.read_chip_info, 1, 1)
        ]
        for text, handler, row, col in cmd_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(QSize(160, 35))
            btn.clicked.connect(handler)
            cmd_layout.addWidget(btn, row, col)
        layout.addWidget(cmd_group)

        # 信息展示区域
        self.advanced_output = QTextEdit()
        self.advanced_output.setReadOnly(True)
        self.advanced_output.setStyleSheet("font-family: monospace;")
        layout.addWidget(QLabel("命令输出:"))
        layout.addWidget(self.advanced_output, 1)

        return tab

    def init_partition_table(self):
        """初始化分区表格"""
        self.partition_table.setColumnCount(7)
        headers = ["选择", "NO", "LBA", "Size", "分区名", "镜像", "管理"]
        self.partition_table.setHorizontalHeaderLabels(headers)
        self.partition_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.partition_table.setColumnWidth(0, 60)   # 选择列
        self.partition_table.setColumnWidth(1, 60)  # NO列
        self.partition_table.setColumnWidth(2, 120)  # LBA列
        self.partition_table.setColumnWidth(3, 120)  # Size列
        self.partition_table.setColumnWidth(4, 150)  # 分区名
        self.partition_table.setColumnWidth(5, 150)  # 增加镜像列宽度
        self.partition_table.setColumnWidth(6, 150)  # 增加管理列宽度
        self.partition_table.horizontalHeader().setStretchLastSection(True)

    def init_menubar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")


    def handle_reboot(self, index):
        if index == 0:
            return

        try:
            if index == 1:  # 重启到系统（不检测 ADB）
                if not self.current_device:  # 检查是否选中 Loader 设备
                    self.log_text.append("错误: 请先选择设备")
                    self.reboot_combo.setCurrentIndex(0)
                    return
                cmd = "./upgrade_tool RD"
                self.run_command(cmd)
                self.log_text.append("设备正在重启到系统...")

            elif index == 2:  # 进入 Loader 模式（需检测 ADB）
                adb_devices = self.get_adb_devices()
                if not adb_devices:
                    self.log_text.append("错误: 未检测到已授权的 ADB 设备")
                    self.reboot_combo.setCurrentIndex(0)
                    return
                device_id = list(adb_devices.keys())[0]
                cmd = f"adb -s {device_id} reboot loader"
                self.run_command(cmd)
                self.log_text.append(f"设备 {device_id} 正在进入 Loader 模式...")
                QTimer.singleShot(5000, self.refresh_devices)  # 5秒后刷新设备列表

            self.reboot_combo.setCurrentIndex(0)
        except Exception as e:
            self.log_text.append(f"操作失败: {str(e)}")
            self.reboot_combo.setCurrentIndex(0)

    def get_adb_devices(self, silent=False):
        """获取 ADB 设备列表（支持静默模式）"""
        output = self.run_command("adb devices", silent=silent)
        devices = {}
        for line in output.splitlines():
            if "List of devices attached" in line or line.strip() == "":
                continue
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == "device":
                devices[parts[0]] = "authorized"
        return devices

    
    def refresh_devices(self):
        """统一刷新设备列表"""
        self.log_text.append("正在刷新设备列表...")
        
        # 清空旧设备列表
        self.device_combo.clear()
        
        # 获取 Loader 模式设备（通过 upgrade_tool）
        loader_devices = self.get_loader_devices(silent=True)
        
        # 获取 ADB 模式设备
        adb_devices = self.get_adb_devices()
        
        # 合并设备显示（标记设备类型）
        if loader_devices:
            self.device_combo.addItems(loader_devices)
            self.log_text.append(f"Loader 模式设备: {', '.join(loader_devices)}")
        if adb_devices:
            self.device_combo.addItems([f"[ADB] {dev}" for dev in adb_devices.keys()])
            self.log_text.append(f"ADB 模式设备: {', '.join(adb_devices.keys())}")
        
        if not loader_devices and not adb_devices:
            self.log_text.append("未检测到任何设备")

    def run_command(self, command, silent=False):
        """执行系统命令，添加 silent 参数控制日志输出"""
        try:
            if not silent:
                self.log_text.append(f">>> 执行命令: {command}")

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = ''
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output += line
                    if not silent:
                        self.log_text.append(line.strip())
                error = process.stderr.readline()
                if error:
                    self.log_text.append(f"错误: {error.strip()}")

            process.wait()
            return output
        except Exception as e:
            self.log_text.append(f"命令执行异常: {str(e)}")
            return ""

    def device_changed(self, index):
        self.current_device = self.device_combo.currentText()
        self.get_partition_info()

    def get_loader_devices(self, silent=False):
        """获取 Loader 设备列表（支持静默模式）"""
        output = self.run_command("./upgrade_tool ld", silent=silent)
        devices = []
        for line in output.split('\n'):
            if "DevNo=" in line:
                devices.append(line.strip())
        return devices
    

    def get_partition_info(self):
        """获取分区信息（修复标题行问题）"""
        if not self.current_device:
            return

        output = self.run_command("./upgrade_tool PL")
        self.partition_table.setRowCount(0)

        start_parsing = False
        for line in output.split('\n'):
            # 跳过标题行（例如 "NO  LBA        Size       Name"）
            if "Partition Info(gpt):" in line:
                start_parsing = True
                self.partition_table.setHorizontalHeaderLabels(["选择", "NO", "LBA", "Size", "分区名", "镜像", "管理"])
                continue

            # 跳过标题行后的分割线（例如 "-------------------"）
            if start_parsing and "---" in line:
                continue

            if start_parsing and line.strip():
                parts = line.strip().split()
                if len(parts) >= 4 and parts[0].isdigit():  # 确保第一列是数字（NO列）
                    row = self.partition_table.rowCount()
                    self.partition_table.insertRow(row)

                    # 复选框（第0列）
                    checkbox = QTableWidgetItem()
                    checkbox.setCheckState(Qt.Unchecked)
                    self.partition_table.setItem(row, 0, checkbox)

                    # 填充各列数据（NO, LBA, Size, Name）
                    for col in range(4):
                        self.partition_table.setItem(row, col+1, QTableWidgetItem(parts[col]))

              

                    # 镜像选择按钮（第5列）
                    img_btn = QPushButton("选择镜像")
                    img_btn.setFixedSize(QSize(120, 28))  # 统一高度为28，增加宽度
                    img_btn.setStyleSheet("""
                        font-size: 10pt; 
                        padding: 2px;
                    """)
                    img_btn.clicked.connect(lambda _, r=row: self.select_image(r))
                    self.partition_table.setCellWidget(row, 5, img_btn)

                    # 管理按钮（第6列）
                    manage_btn = QPushButton("管理")
                    manage_btn.setFixedSize(QSize(120, 28))  # 调整为相同尺寸
                    manage_btn.setStyleSheet("""
                        background-color: #E0E0E0; 
                        font-size: 10pt; 
                        padding: 2px;
                    """)
                    manage_btn.clicked.connect(lambda _, r=row: self.show_partition_menu(r, manage_btn))
                    self.partition_table.setCellWidget(row, 6, manage_btn)

    def show_partition_menu(self, row, button):
        """显示管理弹窗（居中）"""
        dialog = PartitionDialog(self)
        # 居中弹窗
        dialog.move(
            self.window().frameGeometry().center() - 
            dialog.frameGeometry().center()
        )
        dialog.exec_()

    def select_image(self, row_position):
        root = tk.Tk()
        root.withdraw()
        
        # 获取 PyQt 主窗口位置
        main_win_center = self.window().frameGeometry().center()
        root.geometry(f"+{main_win_center.x()}+{main_win_center.y()}")
        
        img_path = filedialog.askopenfilename(
            title="选择镜像文件",
            filetypes=[("镜像文件", "*.img")]
        )
        if img_path:
            btn = self.partition_table.cellWidget(row_position, 5)
            btn.setText(img_path.split("/")[-1])
            btn.setProperty("data", img_path)
            self.log_text.append(f"已选择镜像: {img_path}")
        root.destroy()

    def select_backup_path(self):
        root = tk.Tk()
        root.withdraw()
        self.default_backup_path = filedialog.askdirectory(title="选择备份路径")
        self.log_text.append(f"备份路径已设置到: {self.default_backup_path}")

    def flash_partition(self, row):
        """刷入分区（使用分区名参数）"""
        part_name = self.partition_table.item(row, 4).text().lower()  # 获取分区名
        btn = self.partition_table.cellWidget(row, 5)
        img_path = btn.property("data")
        
        if not img_path:
            self.log_text.append("请先选择镜像文件")
            return

        cmd = f"./upgrade_tool DI -{part_name} {img_path}"
        self.run_command(cmd)
        self.log_text.append(f"{part_name.upper()}分区刷入完成")

    def read_partition(self, row):
        # 获取分区名（例如 "BOOT"）并清理非法字符
        part_name = self.partition_table.item(row, 4).text().strip().lower()
        part_name = part_name.replace(" ", "_").replace("/", "")  # 确保文件名合法
        
        # 生成纯文件名（如 "boot.img"）
        img_filename = f"{part_name}.img"
        
        # 构造命令（不带路径）
        lba_start = self.partition_table.item(row, 2).text()
        size = self.partition_table.item(row, 3).text()
        cmd = f"./upgrade_tool RL {lba_start} {size} {img_filename}"
        
        # 执行命令并记录日志
        self.run_command(cmd)
        self.log_text.append(f"分区已备份为: {img_filename}")

    def erase_partition(self, row):
        cmd = f"./upgrade_tool EL {self.partition_table.item(row, 2).text()} " \
              f"{self.partition_table.item(row, 3).text()}"
        self.run_command(cmd)
        self.log_text.append(f"分区 {self.partition_table.item(row, 4).text()} 已擦除")

    def batch_flash_partitions(self):
        selected = []
        for row in range(self.partition_table.rowCount()):
            if self.partition_table.item(row, 0).checkState() == Qt.Checked:
                selected.append(row)

        if not selected:
            self.log_text.append("请先选择要刷入的分区")
            return

        self.progress_bar.setValue(0)
        total = len(selected)
        for i, row in enumerate(selected, 1):
            self.flash_partition(row)
            self.progress_bar.setValue(int(i / total * 100))
        self.log_text.append("批量刷入操作完成")

    def batch_backup_partitions(self):
        selected = []
        for row in range(self.partition_table.rowCount()):
            if self.partition_table.item(row, 0).checkState() == Qt.Checked:
                selected.append(row)

        if not selected:
            self.log_text.append("请先选择要备份的分区")
            return

        self.progress_bar.setValue(0)
        total = len(selected)
        for i, row in enumerate(selected, 1):
            self.read_partition(row)
            self.progress_bar.setValue(int(i / total * 100))
        self.log_text.append("批量备份操作完成")

    def upgrade_firmware(self):
        root = tk.Tk()
        root.withdraw()
        firmware_path = filedialog.askopenfilename(
            title="选择固件文件",
            filetypes=[("固件文件", "*.img")]
        )
        if not firmware_path:
            return

        cmd = f"./upgrade_tool UF {firmware_path}"
        output = self.run_command(cmd)
        if "Upgrade OK" in output:
            self.log_text.append("固件升级成功")
            self.progress_bar.setValue(100)
        else:
            self.log_text.append("固件升级失败")

    def read_sn(self):
        output = self.run_command("./upgrade_tool RSN")
        self.advanced_output.setText("=== SN信息 ===\n" + output)

    def write_sn(self):
        sn = self.sn_input.text().strip()
        if not sn:
            self.log_text.append("SN号不能为空")
            return

        output = self.run_command(f"./upgrade_tool SN {sn}")
        self.advanced_output.append("=== 写入SN ===\n" + output)
        if "success" in output.lower():
            self.log_text.append("SN写入成功")

    def switch_storage(self):
        output = self.run_command("./upgrade_tool SSD")
        self.advanced_output.setText("=== 存储切换 ===\n" + output)

    def read_flash_id(self):
        output = self.run_command("./upgrade_tool RID")
        self.advanced_output.setText("=== Flash ID ===\n" + output)

    def read_flash_info(self):
        output = self.run_command("./upgrade_tool RFI")
        self.advanced_output.setText("=== Flash信息 ===\n" + output)

    def read_chip_info(self):
        output = self.run_command("./upgrade_tool RCI")
        self.advanced_output.setText("=== 芯片信息 ===\n" + output)

if __name__ == "__main__":
    # 确保在脚本目录执行
    os.chdir(get_script_dir())
    
    # 检查root权限
    if os.getuid() != 0:
        request_root()
    
    # 验证环境
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本路径: {os.path.abspath(__file__)}")
    
    app = QApplication(sys.argv)
    window = RockusbGUI()
    window.show()
    sys.exit(app.exec_())

