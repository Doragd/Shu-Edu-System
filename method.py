#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
from time import sleep
import re
import getpass
import datetime
import pandas as pd
import numpy as np
import hashlib
from entity import *
from tabulate import tabulate

def login():
    
    global teacher
    global student
    
    try:
        login_id = int(input('请输入学号/工号 > '))
    except:
        print('输入不合法！')
        return -1,'SHU-EDU > '
    password = md5_encrypt(getpass.getpass('请输入密码(无回显 按回车提交) > '))
    if login_id not in list(database.login_data['login_id']):
        print('用户或密码错误！')
        return -1,'SHU-EDU > '
    else:
        if list(database.login_data[database.login_data['login_id'] == login_id]['password'])[0] != password:
            print('用户或密码错误！')
            return -1,'SHU-EDU > '
        else:
            print('欢迎回来！')
            status = list(database.login_data[database.login_data['login_id'] == login_id]['status'])[0]
            if(status == 0):
                os.system("title 上海大学智慧教务管理系统(教师端)")
                teacher = Teacher(login_id)
            else:
                os.system("title 上海大学智慧教务管理系统(学生端)")
                student = Student(login_id)
            
            prompt = 'SHU-EDU:/' + str(login_id) + "$ "
            return status, prompt

def show_course():
    res = teacher.show_course().copy()
    res.columns = ['课程号','课程名','上课时间','上课地点','容量','已选人数','教师号','学分']
    print(tabulate(res, headers='keys', tablefmt='psql'))

def add_course():
    kw = {}
    try:
        kw['course_name'] = input('请输入添加的课程名 > ')
        kw['open_time'] = input('上课时间 > ')
        kw['open_local'] = input('上课地点 > ')   
        kw['pop_capacity'] = int(input('容量 > '))
        kw['pop_selected'] = 0
        kw['credit'] = int(input('学分 > '))
    except:
        print('输入不合法！')
        return
    teacher.add_course(kw)
    show_course()
    
def delete_course(course_id):
    if course_id  not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    teacher.delete_course(course_id)
    show_course()

def modify_course(course_id):
    if course_id  not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    kw = {}
    try:
        kw['course_name'] = input('请输入新的课程名(直接回车则不修改) > ')
        kw['open_time'] = input('上课时间(直接回车则不修改) > ')
        kw['open_local'] = input('上课地点(直接回车则不修改) > ')
        kw['pop_capacity'] = input('容量(直接回车则不修改) > ')
        kw['pop_selected'] = 0
        kw['credit'] = input('学分(直接回车则不修改) > ')
    except:
        print('输入不合法！')
        return
    teacher.modify_course(course_id, kw)
    show_course()
 
def show_task_list(course_id):
    if course_id  not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    res = teacher.show_task_list(course_id).copy()
    res.columns = ['作业号','作业名','课程号','作业发布时间','作业截止时间','所属课程']
    print(tabulate(res, headers='keys', tablefmt='psql'))

def show_task_detail(task_id):
    if task_id not in list(database.task_list['task_id'].drop_duplicates()):
        print('作业号不合法')
        return
    res = teacher.show_task_detail(task_id).copy()
    res.columns = ['学号','作业号','得分','总分','姓名']
    print(tabulate(res, headers='keys', tablefmt='psql'))
    
def add_task():
    kw = {}
    kw['task_id'] = database.task_list['task_id'][len(database.task_list)-1] + 1
    try:
        kw['task_name'] = input('请输入作业名 > ')
        kw['course_id'] = int(input('所属课程号 > '))
    except:
        print('输入不合法！')
        return
    if kw['course_id'] not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    kw['task_start'] = datetime.datetime.now()
    try:
        time = int(input('作业持续时间(天) > '))
    except:
        print('输入不合法！')
        return
    delta = datetime.timedelta(days=time)
    kw['task_end'] = kw['task_start'] + delta
    path = input('请输入添加的作业批改表文件名 > ')
    try:
        task_data = pd.read_excel('update/' + path, headers=None)
        if (list(task_data.columns) != ['student_id', 'task_score', 'full_score']) or (len(task_data)==0):
            print('文件为空或格式不对应!')
            return
    except:
        print('Wrong!')
    task_data['task_id'] = kw['task_id']
    task_data = task_data[['student_id','task_id','task_score','full_score']]
    teacher.add_task(task_data, kw)
    show_task_list(kw['course_id'])
    
def delete_task(task_id):
    if task_id not in list(database.task_list['task_id'].drop_duplicates()):
        print('作业号不合法')
        return
    teacher.delete_task(task_id)

def modify_task(task_id):
    if task_id not in list(database.task_list['task_id'].drop_duplicates()):
        print('作业号不合法')
        return
    try:
        database.task_item[database.task_item['task_id'] == task_id].to_excel('update/modify_task.xlsx', index=None)
    except:
        print('文件被占用中,请关闭其他程序重试')
        return
    print("下载对应的modify_task.xlsx到update文件夹完成，请进行修改 > ")
    while(1):
        flag = input('修改是否完成: y/n > ')
        if(flag == 'y'):
            try:
                task_data = pd.read_excel('update/modify_task.xlsx')
                if (list(task_data.columns) != ['student_id','task_id','task_score', 'full_score']) or (len(task_data)==0):
                    print('文件为空或格式不对应!')
                    return
            except:
                print('Wrong!')
                return
            teacher.modify_task(task_data, task_id)
            print("修改完成")
            break
        else:
            print('等待10s再询问...')
            sleep(10)
            flag2 = input('放弃修改? y/n > ')
            if(flag2 == 'y'):
                break   

def send_msg():
    receivers = input('请输入要发送的邮箱(以空格分割) > ').split(' ')
    for receiver in receivers:
        if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', receiver):
            print('邮箱格式错误！')
            return
    content = {}
    content['subject'] = input('主题 > ')
    content['main'] = input('内容 > ')
    teacher.send_msg(receivers, content)

def show_check_list(course_id):
    if course_id  not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    res = teacher.show_check_list(course_id).copy()
    res.columns = ['签到号','签到发布时间','签到人数', '应到人数', '所属课程号', '所属课程']
    print(tabulate(res, headers='keys', tablefmt='psql'))

def show_check_detail(check_id):
    if check_id not in list(database.check_list['check_id'].drop_duplicates()):
        print('签到记录不合法')
        return
    res = teacher.show_check_detail(check_id).copy()
    res.columns = ['学号','签到号','已签到人数','签到状态','姓名']
    print(tabulate(res, headers='keys', tablefmt='psql'))

def add_check():
    kw = {}
    kw['check_id'] = database.check_list['check_id'][len(database.check_list)-1] + 1
    try:
        kw['course_id'] = int(input('添加签到的课程号 > '))
    except:
        print('输入不合法！')
        return
    if kw['course_id'] not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    kw['check_time'] = datetime.datetime.now()
    path = input('请输入添加的签到记录表文件名 > ')
    try:
        check_data = pd.read_excel('update/' + path, headers=None)
        if (list(check_data.columns) != ['student_id', 'check_flag']) or (len(check_data)==0):
            print('文件为空或格式不对应!')
            return        
    except:
        print('Wrong!')
        return
    kw['check_num'] = np.sum(check_data['check_flag'])
    kw['check_total'] = len(check_data)
    check_data['check_num'] = kw['check_num']
    check_data['check_id'] = kw['check_id']
    check_data = check_data[['student_id','check_id','check_num','check_flag']]
    teacher.add_check(check_data, kw)
    show_check_list(kw['course_id'])

def delete_check(check_id):
    if check_id not in list(database.check_list['check_id'].drop_duplicates()):
        print('签到记录不合法')
        return
    teacher.delete_check(check_id)

def modify_check(check_id):
    if check_id not in list(database.check_list['check_id'].drop_duplicates()):
        print('签到记录不合法')
        return
    try:
        database.check_item[database.check_item['check_id'] == check_id][['student_id','check_id','check_flag']].to_excel('update/modify_check.xlsx', index=None)
    except:
        print('文件被占用中,请关闭其他程序重试')
        return
    print("下载对应的modify_check.xlsx到update文件夹完成，请进行修改 > ")
    while(1):
        flag = input('修改是否完成: y/n > ')
        if(flag == 'y'):
            kw = {}
            kw['check_time'] = datetime.datetime.now()
            try:
                check_data = pd.read_excel('update/modify_check.xlsx')
                if (list(check_data.columns) != ['student_id', 'check_id','check_flag']) or (len(check_data)==0):
                    print('文件为空或格式不对应!')
                    return 
            except:
                print('Wrong!')
                return
            kw['check_num'] = np.sum(check_data['check_flag'])
            kw['check_total'] = len(check_data)
            check_data['check_num'] = kw['check_num']
            check_data = check_data[['student_id','check_id','check_num','check_flag']]
            teacher.modify_check(check_data, check_id, kw)
            print("修改完成")
            break
        else:
            print('等待10s再询问...')
            sleep(10)
            flag2 = input('放弃修改? y/n > ')
            if(flag2 == 'y'):
                break

                    
def show_score(course_id):
    if course_id  not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    res = teacher.show_score(course_id).copy()
    res.columns = ['学号',	'课程号',	'平时成绩',	'期末成绩',	'总评成绩']
    res['学号'] = res['学号'].astype('str')
    print(tabulate(res, headers='keys', tablefmt='psql'))

def update_score(course_id):
    if course_id  not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    path = input('请输入更新的成绩文件名 > ')
    try:
        score_data = pd.read_excel('update/' + path, headers=None)
        if (list(score_data.columns) != ['student_id', 'class_score', 'exam_score', 'final_score']) or (len(score_data)==0):
            print('文件为空或格式不对应!')
            return
    except:
        print('Wrong！')
        return
    score_data['course_id'] = course_id
    score_data = score_data[['student_id','course_id','class_score', 'exam_score', 'final_score']]
    teacher.update_score(course_id, score_data)
    show_score(course_id)
    
def show_student(course_id):
    
    if course_id  not in list(database.teacher_data[database.teacher_data['teacher_id'] == teacher.teacher_id]['course_id']):
        print('课程号不在范围内！')
        return
    res = teacher.show_student(course_id).copy()
    res.columns = ['学号',	'课程号',	'平时成绩',	'期末成绩',	'总评成绩',	'学生姓名',	'荣誉',	'竞赛',	'学术交流','gpa','不良记录']
    options = [0,1,2,3]
    print("排序选项: [0]默认排序 [1]总评成绩 [2]GPA [3]不良记录")
    try:
        option = int(input('查看班级学生信息的排序方式 > '))
        flag = input('升序 or 降序？y/n > ')
    except:
        print('输入不合法！')
        return
    if option not in options or flag not in ['y','n']:
        print('输入不合法！')
        return
    elif(option == 0):
        print(tabulate(res, headers='keys', tablefmt='psql'))
    elif(option == 1):
        if(flag == 'y'):
            print(tabulate(res.sort_values(by='总评成绩'), headers='keys', tablefmt='psql'))
        else:
            print(tabulate(res.sort_values(by='总评成绩', ascending=False), headers='keys', tablefmt='psql'))
    elif(option == 2):
        if(flag == 'y'):
            print(tabulate(res.sort_values(by='gpa'), headers='keys', tablefmt='psql'))
        else:
            print(tabulate(res.sort_values(by='gpa', ascending=False), headers='keys', tablefmt='psql'))
    else:
        if(flag == 'y'):
            print(tabulate(res.sort_values(by='不良记录'), headers='keys', tablefmt='psql'))
        else:
            print(tabulate(res.sort_values(by='不良记录', ascending=False), headers='keys', tablefmt='psql'))        
    
############################################################################################################     
def show_course_student():
    res = student.show_course().copy()
    res.columns = ['学号','课程号','课程名','上课时间','上课地点','容量','已选人数','教师号','学分']
    print(tabulate(res, headers='keys', tablefmt='psql'))

def show_course_detail():
    res = student.show_course_detail().copy()
    res.columns = ['学号','课程号','平时成绩','期末成绩','总评成绩']
    res['学号'] = res['学号'].apply(lambda x: str(x))
    print(tabulate(res, headers='keys', tablefmt='psql'))

def show_information():
    res = student.show_information().copy()
    res.columns = ['学号','姓名','荣誉','竞赛','学术交流','gpa','不良记录']
    print(tabulate(res, headers='keys', tablefmt='psql'))

def modify_information():
    kw = {}
    kw['award'] = input('请输入更新的荣誉(直接回车则不修改) > ')
    kw['contest'] = input('请输入更新的竞赛(直接回车则不修改) > ')
    kw['academic'] = input('请输入更新的学术情况(直接回车则不修改) > ')
    student.modify_information(kw)
    show_information()
    
def show_teacher():
    course_name = input('请输入需要查询教师信息的课程名 > ')
    if course_name not in list(database.course_data['course_name'].drop_duplicates()):
        print('课程不存在！')
        return
    res = student.show_teacher(course_name).copy()
    res.columns = ['授课课程', '教师工号',	'姓名',	'课程号', '教师评价']
    options = [0,1]
    print("排序选项: [0]默认排序 [1]教师评价")
    try:
        option = int(input('查看教师信息的排序方式 > '))
        flag = input('升序 or 降序？y/n > ')
    except:
        print('输入不合法！')
        return
    if option not in options or flag not in ['y','n']:
        print('输入不合法！')
        return
    elif(option == 0):
        print(tabulate(res, headers='keys', tablefmt='psql'))
    else:
        if(flag == 'y'):
            print(tabulate(res.sort_values(by='教师评价'), headers='keys', tablefmt='psql'))
        else:
            print(tabulate(res.sort_values(by='教师评价', ascending=False), headers='keys', tablefmt='psql'))
    
def find_student():
    options = [0,1]
    print("模糊查找选项: [0]按学号模糊查找 [1]按姓名模糊查找")
    try:
        option = int(input('输入模糊查找方式 > '))
    except:
        print('输入不合法！')
        return
    if (option not in options):
       print('输入不合法！')
       return 
    key = input('请输入模糊查找关键字 > ')
    if (option == 1):
        res = database.student_data[database.student_data['student_name'].str.contains(key)].copy()
        res.columns = ['学号','姓名','荣誉','竞赛','学术交流','gpa','不良记录']
        print(tabulate(res, headers='keys', tablefmt='psql'))
    else:
        res = database.student_data[database.student_data['student_id'].apply(lambda x: str(x)).str.contains(key)].copy()
        res.columns = ['学号','姓名','荣誉','竞赛','学术交流','gpa','不良记录']
        print(tabulate(res, headers='keys', tablefmt='psql'))
        
def find_teacher():
    options = [0,1,2]
    print("模糊查找选项: [0]按教师号模糊查找 [1]按课程号模糊查找 [2]按姓名模糊查找")
    try:
        option = int(input('输入模糊查找方式 > '))
    except:
        print('输入不合法！')
        return
    if(option not in options):
       print('输入不合法！')
       return 
    key = input('请输入模糊查找关键字 > ')
    if (option == 0):
        res = database.teacher_data[database.teacher_data['teacher_id'].apply(lambda x: str(x)).str.contains(key)].copy()
        res.columns = ['工号','姓名','课程号','教师评价']
        print(tabulate(res, headers='keys', tablefmt='psql'))
    elif(option == 1):
        res = database.teacher_data[database.teacher_data['course_id'].apply(lambda x: str(x)).str.contains(key)].copy()
        res.columns = ['工号','姓名','课程号','教师评价']
        print(tabulate(res, headers='keys', tablefmt='psql'))
    else:
        res = database.teacher_data[database.teacher_data['teacher_name'].str.contains(key)].copy()
        res.columns = ['工号','姓名','课程号','教师评价']
        print(tabulate(res, headers='keys', tablefmt='psql'))

def function_bind():

    global func_bind

    student_func = {
        'inform -l': show_information,
        'inform -m': modify_information,
        'course -s': show_course_student,
        'course -v': show_course_detail,
        'show -t': show_teacher,
        'find -t': find_teacher
    }
    teacher_func = {
        'msg': send_msg,
        'course -l': show_course,
        'course -a': add_course,
        'check -a': add_check,
        'task -a': add_task,
        'find -s': find_student,
        'course -m': modify_course,
        'course -d': delete_course,
        'task -l': show_task_list,
        'task -v': show_task_detail,
        'task -m': modify_task,
        'task -d': delete_task,
        'check -l': show_check_list,
        'check -v': show_check_detail,
        'check -m': modify_check,
        'check -d': delete_check,
        'score -l': show_score,
        'score -u': update_score,
        'show -s': show_student,
    }  
    func_bind = [teacher_func, student_func]

function_bind()
        
def exec_teacher(command):
    strs = command.split(' ')
    if len(strs) == 1:
        arg = strs[0]
        if(arg in list(func_bind[0].keys())[0]):
            func_bind[0][arg]() #send_msg()
        else:
            print('命令错误或无权限,输入help查看帮助')
            return    
    elif len(strs) == 2:
        arg = strs[0] + ' ' + strs[1]
        if(arg in list(func_bind[0].keys())[1:6]):
            func_bind[0][arg]()
        else:
            print('命令错误或无权限,输入help查看帮助')
            return
    elif len(strs) == 3:
        try:
            args = [strs[0] + ' ' + strs[1], int(strs[-1])]
        except:
            print("输入参数不合法！")
            return
        if(args[0] in list(func_bind[0].keys())[6:]):
            func_bind[0][args[0]](args[1])
        else:
            print('命令错误或无权限,输入help查看帮助')
            return
    else:
        print('命令错误或无权限,输入help查看帮助')
        return

 
def exec_student(command):
    strs = command.split(' ')
    if len(strs) == 2:
        arg = strs[0] + ' ' + strs[1]
        if(arg in func_bind[1].keys()):
            func_bind[1][arg]()
        else:
            print('命令错误或无权限,输入help查看帮助')
            return
    else:
        print('命令错误或无权限,输入help查看帮助')
        return 

def save_to_database():
    writer = pd.ExcelWriter('update/data.xlsx')
    database.login_data.to_excel(writer,sheet_name='login',index=None)
    database.course_data.to_excel(writer,sheet_name='course',index=None)
    database.task_list.to_excel(writer,sheet_name='task_list',index=None)
    database.task_item.to_excel(writer,sheet_name='task_item',index=None)
    database.check_list.to_excel(writer,sheet_name='check_list',index=None)
    database.check_item.to_excel(writer,sheet_name='check_item',index=None)
    database.score_data.to_excel(writer,sheet_name='score',index=None)
    database.teacher_data.to_excel(writer,sheet_name='teacher',index=None)
    database.student_data.to_excel(writer,sheet_name='student',index=None)
    writer.save()


if __name__=='__main__':
    pass
