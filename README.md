# ROCKCHIPLinux-Upgrade-GUI-for-Linux

基于瑞芯微官方 `Upgrade_Tool` 开发的图形化固件升级工具，支持RK35xx系列芯片设备的系统升级。

## 🌐 支持系统
- Ubuntu/Debian 等 Debian 发行版（推荐）
- 其他 Linux 发行版（需手动配置）

---

## 📥 安装指南(中文）

### 🆓 Debian/Ubuntu 等Debian发行版Linux：
1. **下载安装包**：
   [👉 点击下载最新版 .deb 文件](https://github.com/carvenliner/ROCKCHIPLinux-Upgrade-GUI-for-Linux/releases/tag/release)

2. **安装程序**：
   ```bash
   sudo dpkg -i ROCKCHIPLinux-Upgrade-GUI-for-Linux_*.deb
   sudo apt --fix-broken install  # 解决依赖问题


### 🆓 其他发行版Linux（Arch Centos…）：
1. **下载源码**
2. **安装依赖**
   ```bash
   python3 python3-tk python3-pyqt5 libudev1 libusb-1.0-0 adb
3.**切换到源码目录运行**
  ```bash
   sudo python3 RKUpgradeTool.py

---------------------------------------------------------

  
## 📥 Installation Guide（English）

### 🆓 For Debian-based Linux Distributions (e.g., Ubuntu, Debian):
1. **Download the Installer**:
   [👉 Click here to download the latest `.deb` file](https://github.com/carvenliner/ROCKCHIPLinux-Upgrade-GUI-for-Linux/releases/tag/release)

2. **Install the Program**:
   ```bash
   sudo dpkg -i ROCKCHIPLinux-Upgrade-GUI-for-Linux_*.deb
   sudo apt --fix-broken install  # Resolve dependency issues
