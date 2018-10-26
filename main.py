#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import division
from asciimatics.effects import Cycle, Stars, Print
from asciimatics.renderers import FigletText,  SpeechBubble
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from method import *
import warnings
warnings.filterwarnings("ignore")

open_flag = r'''
+-----------------------------------------------------+
|   _____ _    _ _    _        ______ _____  _    _   |
|  / ____| |  | | |  | |      |  ____|  __ \| |  | |  |
| | (___ | |__| | |  | |______| |__  | |  | | |  | |  |
|  \___ \|  __  | |  | |______|  __| | |  | | |  | |  |
|  ____) | |  | | |__| |      | |____| |__| | |__| |  |
| |_____/|_|  |_|\____/       |______|_____/ \____/   |
|                                                     |
+-----------------------------------------------------+

SHU-EDU - 上海大学智慧教务管理系统 for Windows/amd64

提示：输入 help 获取帮助 
提示：输入 cls 清屏
提示：输入 login 登录 logout 登出
提示: 输入 exit 退出程序 否则不保存任何操作到数据库
测试教师账号：10001 208092
测试学生账号：16051086 389340
'''

help_doc = r'''
----------------------------------------------------
SHU-EDU - 上海大学智慧教务管理系统 for Windows/amd64

VERSION:
    V1.0

COMMANDS:
    course                    教师授课
    task                      作业批改
    check                     考勤签到
    msg                       发送通知(例如：答疑辅导)
    score                     成绩管理
    inform                    学生个人信息管理
    show                      教师/学生信息一览

OPTIONS:
    -a                        添加
    -m                        修改
    -d                        删除
    -l                        列表
    -u                        更新
    -t                        教师
    -s                        学生
    -v                        查看详情

USAGES FOR Teachers:
    course -l                                列出课程列表
    course -a                                增加课程
    course -m <course_id>                    修改课程
    course -d <course_id>                    删除课程
    task -l <course_id>                      列出指定课程的作业列表
    task -v <task_id>                        查看指定作业详情
    task -a                                  增加作业
    task -m <task_id>                        修改作业
    task -d <task_id>                        删除作业
    msg                                      发送通知
    check -l <course_id>                     列出指定课程的考勤列表
    check -v <check_id>                      查看指定考勤详情
    check -a                                 增加考勤
    check -m <check_id>                      修改考勤
    check -d <check_id>                      删除考勤
    score -l <course_id>                     列出班级成绩
    score -u <course_id>                     更新班级成绩
    show -s <course_id>                      查看班级学生信息并排序
    find -s                                  模糊查找所有学生信息
    

USAGES FOR Students:    
    inform -l                                列出学生个人信息
    inform -m                                修改学生个人信息
    course -s                                列出学生个人课程表
    course -v                                查看学生个人课程详情
    show -t                                  查看上课教师信息并排序
    find -t                                  模糊查找所有教师信息
    
-----------------------------------------------------
'''

def init():

    global prompt
    global status
    global keys
    
    os.system("title 上海大学智慧教务管理系统")
    Screen.wrapper(display)
    
    print(open_flag)

    prompt = 'SHU-EDU > '
    status = -1
    keys = ['course', 'task', 'check', 'msg', 'score', 'inform', 'show', 'find']


def display(screen):
    effects = [
        Cycle(
            screen,
            FigletText("Shanghai University", font='big'),
            screen.height // 2 - 10),
        Cycle(
            screen,
            FigletText("Edu-System", font='big'),
            screen.height // 2 - 1),
        Stars(screen, (screen.width + screen.height) // 2),
        Print(screen, SpeechBubble("Press 'space' to login."), screen.height // 2 + 10, attr=Screen.A_BOLD)
    ]
    screen.play([Scene(effects, 500)],repeat=False)    
    

def main():

    global prompt
    global status
    
    
    while(1):
        command = input(prompt)
        if(command == ''):
            pass
            
        elif(command == 'help'):
            print(help_doc)
            
        elif(command == 'cls'):
            os.system('cls')
            print(open_flag)
            
        elif(command == 'login'):
            if status < 0:
                status,prompt = login()
            else:
                print("您已登录终端\n无需重复登录！")
                
        elif(command == 'logout'):
            status = -1
            prompt = 'SHU-EDU > '
        elif(command == 'exit'):
            #save_to_database()  测试后上线
            exit('good bye!')
        else:
            key = command.split(' ')[0]
            if key not in keys:
                print("未找到命令：" + command)
                print("输入 help 获取帮助")
                
            elif(status < 0):
                print("无命令权限，请先登录！")
                
            elif(status == 0):
                exec_teacher(command)
                
            elif(status == 1):
                exec_student(command)

if __name__=='__main__':

    init()
    main()
            
    

        
        
    
    