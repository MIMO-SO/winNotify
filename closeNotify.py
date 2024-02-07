import os
import subprocess


def kill_script(script_name):
    input1 = input("输入数字【1】确认关闭脚本：")
    if input1 != "1":
        print("\033[31m" + "您输入的内容不正确！" + "\033[0m")
    else:
        # 列出所有 Python 进程及其命令行参数
        ps_command = subprocess.Popen("wmic process where \"name='python.exe'\" get ProcessId,CommandLine", shell=True,
                                      stdout=subprocess.PIPE)
        ps_output = ps_command.stdout.read()
        ps_command.stdout.close()
        ps_command.wait()

        num = 0

        # 对每个进程进行检查
        for line in ps_output.splitlines():
            if script_name in str(line):
                print("Killing process: " + str(line.decode()))
                pid = int(line.split()[-1])
                os.kill(pid, 9)  # 杀死进程
                num += 1

        if num > 0:
            print("共关闭了" + str(num) + "个进程")
        else:
            print("未找到相关进程")

    print("\033[32m" + "-------------------" + "\033[0m")
    input("\n按回车键退出")


kill_script("WeiboHotSearchApp.py")  # 替换为您的脚本名称
