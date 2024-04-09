# winNotify桌面通知（微博热搜）
#### 置顶声明
- 本项目仅供个人学习使用。
- 任何人不得将本项目用于商业用途，否则后果自负。
- 任何人不得将本项目用于非法用途，否则后果自负。
#### 1. 项目简介
- 本项目是一个基于Python的桌面通知程序，通过爬取微博热搜榜单，实现实时桌面通知功能。
- 本项目使用了`tkinter`库实现了简单的GUI界面，可以实现开启/关闭通知功能。
#### 2. 项目环境
- Python 3.8
#### 3. 项目功能
- 实时获取微博热搜榜单
- 实现桌面通知功能
- 实现开启/关闭通知功能
- 实现简单的GUI界面
- 实现定时刷新功能
- 实现沸点通知排除功能
#### 4. 项目依赖
- tkinter
- win11toast
- Redis
- pystray
- Python Imaging Library (PIL)
#### 5. 项目运行
- 双击`runHidden.vbs`运行程序
- 原理：`runHidden.vbs`运行`start.bat`，并隐藏`cmd`窗口，`start.bat`中执行`WeiboHotSearchApp.py`