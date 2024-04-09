import ctypes
import json
import os
import threading
import time
import tkinter as tk
import urllib.parse
import webbrowser
from tkinter import ttk

import requests
from PIL import Image
from pystray import MenuItem, Icon
from win11toast import toast

from redisUtils import RedisClient

os.environ['NO_PROXY'] = 'weibo.com'
# 获取当前文件路径
path = os.path.abspath(os.path.dirname(__file__))
icon = "file:///" + path + "/icon3.png"


class WeiboHotSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("微博热搜榜")
        self.root.iconbitmap("./icon.ico")
        self.style = ttk.Style()

        self.refresh_interval = tk.StringVar()
        self.refresh_interval.set("120")  # 默认刷新间隔为60秒
        self.send_toast_enabled = tk.BooleanVar()
        self.send_toast_enabled.set(True)  # 默认开启通知
        self.excluded_tags = {  # 默认排除的标签
            "综艺": tk.BooleanVar(value=True),
            "演出": tk.BooleanVar(value=True),
            "音乐": tk.BooleanVar(value=True),
            "美妆": tk.BooleanVar(value=True),
            "影视": tk.BooleanVar(value=True),
            "艺人": tk.BooleanVar(value=True),
            "电视剧": tk.BooleanVar(value=True),
            "电影": tk.BooleanVar(value=True),
            "动漫": tk.BooleanVar(value=True),
            "游戏": tk.BooleanVar(value=True),
            "电竞": tk.BooleanVar(value=True),
            "网红": tk.BooleanVar(value=True),
            "幽默": tk.BooleanVar(value=False),
            "数码": tk.BooleanVar(value=False),
            "美食": tk.BooleanVar(value=False),
            "财经": tk.BooleanVar(value=False),
            "体育": tk.BooleanVar(value=False),
            "情感": tk.BooleanVar(value=False),
            "剧集": tk.BooleanVar(value=False),
            "时尚": tk.BooleanVar(value=False),
            "互联网": tk.BooleanVar(value=False),
            "汽车": tk.BooleanVar(value=False),
            "社会新闻": tk.BooleanVar(value=False),
            "国内时政": tk.BooleanVar(value=False),
            "国外时政": tk.BooleanVar(value=False),
            "作品衍生": tk.BooleanVar(value=False),
            "健康医疗": tk.BooleanVar(value=False),
        }
        self.redis = RedisClient

        self.create_tray_icon()
        self.create_widgets()
        self.update_hot_search()
        self.center_window()

    def create_widgets(self):
        # 创建侧边栏容器
        sidebar = ttk.Frame(self.root, width=100)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        # 添加发送通知开关到侧边栏
        send_toast_frame = ttk.Frame(sidebar)
        send_toast_frame.pack(pady=5)
        send_button = ttk.Checkbutton(send_toast_frame, text="发送沸爆点热搜通知",
                                      variable=self.send_toast_enabled)
        send_button.pack(side=tk.LEFT)

        # 添加排除标签复选框到侧边栏
        exclude_frame = ttk.Frame(sidebar)
        exclude_frame.pack(pady=5)
        exclude_label = ttk.Label(exclude_frame, text="沸点通知排除标签:")
        exclude_label.grid(row=0, column=0, sticky="w", padx=5)
        col = 0
        row = 1
        for tag, var in self.excluded_tags.items():
            checkbox = ttk.Checkbutton(exclude_frame, text=tag, variable=var)
            checkbox.grid(row=row, column=col, sticky="w", padx=5)
            col += 1
            if col == 2:  # 每行最多显示2个复选框，达到最大数量后换行
                col = 0
                row += 1

        # 添加刷新间隔标签到侧边栏
        refresh_frame = ttk.Frame(sidebar)
        refresh_frame.pack(pady=5)
        refresh_label = ttk.Label(refresh_frame, text="刷新间隔(秒):")
        refresh_label.grid(row=0, column=0, sticky="w", padx=5)
        # 添加刷新间隔输入框到侧边栏
        refresh_entry = ttk.Entry(sidebar, textvariable=self.refresh_interval, width=16)
        refresh_entry.pack()
        # 添加更新按钮到侧边栏
        refresh_button = ttk.Button(sidebar, text="更新", command=self.update_interval, width=16)
        refresh_button.pack(pady=5)

        # 创建一个Frame来容纳TreeView和滚动条
        tree_frame = ttk.Frame(self.root, width=600)
        tree_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.tree = ttk.Treeview(tree_frame, columns=("Rank", "Title", "HotnessNum", "Hotness", "Label"), show="headings",
                                 style="Custom.Treeview")
        self.tree.heading("Rank", text="排名", anchor="center")
        self.tree.heading("Title", text="标题", anchor="center")
        self.tree.heading("HotnessNum", text="热值", anchor="center")
        self.tree.heading("Hotness", text="热度", anchor="center")
        self.tree.heading("Label", text="标签", anchor="center")
        self.tree.column("Rank", width=50, anchor="center")  # 设置排名列宽度为50像素
        self.tree.column("Title", width=250, anchor="center")  # 设置标题列宽度为250像素
        self.tree.column("HotnessNum", width=60, anchor="center")  # 设置热值列宽度为50像素
        self.tree.column("Hotness", width=50, anchor="center")  # 设置热度列宽度为50像素
        self.tree.column("Label", width=100, anchor="center")  # 设置标签列宽度为100像素
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.tree.tag_bind("hot_search", "<Double-1>", self.open_webpage)  # 绑定双击事件
        # 创建样式
        self.style.configure("Custom.Treeview", rowheight=24)  # 调整默认行高
        # 设置窗口的透明度（值为0.0到1.0之间）
        self.root.attributes('-alpha', 0.96)

    def selfToast(self, word, realpos, label_name, open_url, button, icon_):
        toast(word, '热搜：' + str(realpos) + '，热度：' + label_name, on_click=open_url,
              button=button, icon=icon_)

    def sendToast(self, category, word, realpos, label_name, url_word):
        if self.send_toast_enabled.get():
            if category is not None and category != "":
                if label_name == "爆" or (not any((self.excluded_tags[tag].get() and tag in category) for tag in
                                                  self.excluded_tags) and label_name == "沸"):
                    redis_word = "weibo_hot_" + word
                    old_label = self.redis.get(redis_word)
                    # 加上redis的判断，防止重复发送
                    if old_label is None or (old_label in ["沸"] and label_name == "爆"):
                        open_url = "https://s.weibo.com/weibo?q=" + url_word
                        button = {'activationType': 'protocol', 'arguments': open_url,
                                  'content': '点击打开'}
                        threading.Thread(
                            target=self.selfToast,  # 将 target 参数设置为函数本身
                            args=(word, realpos, label_name, open_url, button, icon),  # 将函数参数传递给 args 参数
                        ).start()
                        self.redis.setex(redis_word, 60 * 60 * 24, str(label_name))

    def update_hot_search(self):
        # 如果在晚上11点到早上7点之间，不发送通知
        now = time.localtime(time.time())
        if 23 <= now.tm_hour or now.tm_hour <= 6:
            self.task_id = self.root.after(int(self.refresh_interval.get()) * 1000, self.update_hot_search)
            return
        try:
            response = requests.get("https://weibo.com/ajax/statuses/hot_band", timeout=5)
            jsonText = json.loads(response.text)
            if jsonText.get("http_code") == 200:
                band_list = jsonText.get("data").get("band_list")
                if band_list:
                    band_list = band_list[:min(25, len(band_list))]
                    self.tree.delete(*self.tree.get_children())
                    index = 0
                    for i, band in enumerate(band_list):
                        if index >= 20: break
                        label_name = band.get("label_name")
                        if label_name is None:
                            continue
                        raw_hot = band.get("raw_hot")
                        category = band.get("category")
                        word = band.get("word")
                        url_word = urllib.parse.quote(band.get("word_scheme"))
                        realpos = band.get("realpos")
                        # 展示热搜
                        self.tree.insert("", "end", values=(index + 1, word, raw_hot, label_name, category, url_word),
                                         tags=("hot_search", ))
                        index += 1
                        # 发送通知
                        self.sendToast(category, word, realpos, label_name, url_word)
            else:
                print("请求失败")
        except requests.RequestException as e:
            print("请求失败:", e)
        finally:
            self.task_id = self.root.after(int(self.refresh_interval.get()) * 1000, self.update_hot_search)

    def update_interval(self):
        try:
            interval = int(self.refresh_interval.get())
            if interval <= 0:
                raise ValueError("刷新间隔必须大于0")
            self.root.after_cancel(self.task_id)
            self.update_hot_search()
        except ValueError as e:
            print("Error updating interval:", e)

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 710
        window_height = 430

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y - 30}")
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)

    def open_webpage(self, event):
        item = self.tree.identify_row(event.y)  # 获取选中项
        word = self.tree.item(item, "values")[5]  # 获取选中行的第4列
        url = f"https://s.weibo.com/weibo?q={word}"
        webbrowser.open(url)

    def create_tray_icon(self):
        icon_path = "./icon.ico"  # 修改为你的图标文件路径
        icon_image = Image.open(icon_path)
        menu = (
            MenuItem('打开', self.show_window),  # 第一个菜单项
            MenuItem('退出', self.quit_application),  # 最后一个菜单项
            MenuItem(text='点击托盘图标显示', action=self.show_window, default=True, visible=False)
        )
        self.icon = Icon("微博热搜榜", icon_image, "微博热搜榜", menu)  # 创建一个Icon对象，并存储在实例变量中
        self.icon.onclick = self.show_window
        threading.Thread(target=self.icon.run).start()

    def show_window(self, icon, item):
        self.root.deiconify()

    def on_closing(self):
        self.root.withdraw()

    def quit_application(self, icon, item):
        self.icon.stop()  # 停止 Pystray 的事件循环
        self.root.quit()  # 终止 Tkinter 的事件循环
        self.root.destroy()


if __name__ == "__main__":
    icon_path = os.path.abspath("./icon.ico")
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(icon_path)
    root = tk.Tk()
    app = WeiboHotSearchApp(root)
    root.iconbitmap(icon_path)
    root.mainloop()
