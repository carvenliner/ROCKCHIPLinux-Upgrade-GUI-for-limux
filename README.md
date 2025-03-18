# ROCKCHIPLinux-Upgrade-GUI-for-linux
基于瑞芯微官方Upgrade_tool实现的图形化工具
# 对于ubuntu debian 等debian发行版linux
1.下载.deb文件
2. apt install 你的文件
# 对于其他发行版本的linux
1.请安装python3 python3-tk python3-pyqt5  libudev1
         libusb-1.0-0 adb
2.为所有文件赋权 777
3.python3 RKUpgradeTool.py
4.弹窗中输入root密码
我只打包了适用于debian发行版的安装包，其他版本请自行打包或者直接使用
python3 RKUpgradeTool.py
