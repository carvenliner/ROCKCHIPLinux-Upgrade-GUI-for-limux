# ROCKCHIPLinux-Upgrade-GUI-for-Linux

基于瑞芯微官方 `Upgrade_Tool` 开发的图形化固件升级工具，支持 RK35xx 系列芯片设备的系统升级。

## 🌐 支持系统
- **Ubuntu/Debian** 及其衍生发行版（推荐）
- **其他 Linux 发行版**（需手动配置）

---

## 📥 安装指南（中文）

### 🆓 Debian/Ubuntu 等 Debian 发行版：

1. **下载安装包**：  
   [👉 点击下载最新版 `.deb` 文件](https://github.com/carvenliner/ROCKCHIPLinux-Upgrade-GUI-for-Linux/releases/tag/release)

2. **安装程序**：
   ```bash
   sudo dpkg -i ROCKCHIPLinux-Upgrade-GUI-for-Linux_*.deb
   sudo apt --fix-broken install  # 解决依赖问题
   ```

### 🆓 其他 Linux 发行版（Arch、CentOS 等）：

1. **下载源码**：  
   从仓库克隆或下载源代码。

2. **安装依赖**：
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-tk python3-pyqt5 libudev1 libusb-1.0-0 adb
   ```
   > **注意**：请根据你的 Linux 发行版调整包管理器命令，例如 `yum` 适用于 CentOS，`pacman` 适用于 Arch。

3. **运行程序**：
   ```bash
   sudo python3 RKUpgradeTool.py
   ```

---

# ROCKCHIPLinux-Upgrade-GUI-for-Linux

Graphical firmware upgrade tool based on Rockchip official `Upgrade_Tool`, supporting RK35xx series devices.

## 🌐 Supported Systems
- **Ubuntu/Debian-based distributions** (Recommended)
- **Other Linux distributions** (Manual configuration required)

---

## 📥 Installation Guide

### 🆓 For Debian-based Linux Distributions (e.g., Ubuntu, Debian):

1. **Download the Installer**:  
   [👉 Click here to download the latest `.deb` file](https://github.com/carvenliner/ROCKCHIPLinux-Upgrade-GUI-for-Linux/releases/tag/release)

2. **Install the Program**:
   ```bash
   sudo dpkg -i ROCKCHIPLinux-Upgrade-GUI-for-Linux_*.deb
   sudo apt --fix-broken install  # Resolve dependency issues
   ```

### 🆓 For Other Linux Distributions (e.g., Arch, CentOS):

1. **Download the Source Code**:  
   Clone or download the source code from the repository.

2. **Install Dependencies**:
   ```bash
   python3 python3-tk python3-pyqt5 libudev1 libusb-1.0-0 adb
   ```
   > **Note**: Adjust the package manager commands based on your distribution (e.g., `yum` for CentOS, `pacman` for Arch).

3. **Run the Program**:
   ```bash
   sudo python3 RKUpgradeTool.py
   ```
