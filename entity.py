#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.header import Header

#pandas.DataFrame

def md5_encrypt(str):
    return hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()

def send_mail(receivers, content):
    mail_host="smtp.qq.com"
    mail_user="course_test@qq.com"
    mail_pass="dwhrsttihmsmdbbh"

    sender = 'course_test@qq.com'

    message = MIMEText(content['main'], 'plain', 'utf-8')
    message['From'] = Header('上海大学智慧教务系统', 'utf-8')
    message['To'] =  Header("接收方", 'utf-8')

    subject = content['subject']
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host, 25)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print ("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print ("Error: 无法发送邮件")

class Database(object):
    def __init__(self):
        io = pd.io.excel.ExcelFile('database/data.xlsx')
        self.teacher_data = pd.read_excel(io,sheet_name='teacher')
        self.course_data = pd.read_excel(io,sheet_name='course')
        self.task_list = pd.read_excel(io,sheet_name='task_list')
        self.task_item = pd.read_excel(io,sheet_name='task_item')
        self.check_list = pd.read_excel(io,sheet_name='check_list')
        self.check_item = pd.read_excel(io,sheet_name='check_item')
        self.score_data = pd.read_excel(io,sheet_name='score')
        self.student_data = pd.read_excel(io,sheet_name='student')
        self.login_data = pd.read_excel(io,sheet_name='login')
        io.close()

database = Database()

class Teacher(object):
    def __init__(self, teacher_id):

        self.teacher_id = teacher_id
        self.teacher_name = database.teacher_data[database.teacher_data['teacher_id'] == teacher_id]['teacher_name'].values[0]
        self.teacher_eval = database.teacher_data[database.teacher_data['teacher_id'] == teacher_id]['teacher_eval'].values[0]
    
    def show_course(self):
        course_list = database.course_data[database.course_data['teacher_id'] == self.teacher_id]
        return course_list
    
    def add_course(self,kw):
        add_course_id = database.course_data['course_id'][len(database.course_data)-1] + 1
        kw['teacher_id'] = self.teacher_id
        kw['course_id'] = add_course_id
        teacher_item = {'teacher_id':self.teacher_id, 'teacher_name':self.teacher_name, 'course_id':add_course_id, 'teacher_eval':self.teacher_eval}
        database.teacher_data.loc[len(database.teacher_data)] = teacher_item
        database.course_data.loc[len(database.course_data)] = kw
        return self.show_course()
    
    def delete_course(self,course_id):
        database.course_data = database.course_data[~((database.course_data['course_id'] == course_id) & (database.course_data['teacher_id'] == self.teacher_id))]
        database.teacher_data = database.teacher_data[~(database.teacher_data['course_id'] == course_id)] 
    
    def modify_course(self,course_id,kw):
        temp = database.course_data[((database.course_data['course_id'] == course_id) & (database.course_data['teacher_id'] == self.teacher_id))]
        for kw_key in kw.keys():
            if kw[kw_key] == '':
                kw[kw_key] = list(temp[kw_key])[0]
        kw['pop_capacity'] = int(kw['pop_capacity'])
        kw['credit'] = int(kw['credit'])
        kw['course_id'] = course_id
        kw['teacher_id'] = self.teacher_id
        self.delete_course(course_id)
        self.add_course(kw)
    
    def show_task_list(self, course_id):
        task_list = pd.merge(database.task_list[database.task_list['course_id'] == course_id], database.course_data[['course_id','course_name']])
        return task_list
    
    def show_task_detail(self, task_id):
        task_detail = pd.merge(database.task_item[database.task_item['task_id'] == task_id], database.student_data[['student_id','student_name']])
        return task_detail
    
    def add_task(self, task_data, kw):      
        database.task_list.loc[len(database.task_list)] = kw
        database.task_item = pd.concat((task_data, database.task_item)).reset_index(drop=True)
    
    def delete_task(self, task_id):
        database.task_list = database.task_list[~(database.task_list['task_id'] == task_id)]
        database.task_item = database.task_item[~(database.task_item['task_id'] == task_id)]
    
    def modify_task(self, task_data, task_id):
        kw = list(database.task_list[database.task_list['task_id'] == task_id].values[0])
        self.delete_task(task_id)
        self.add_task(task_data, kw)
            
    def send_msg(self, receivers, content):
        send_mail(receivers, content)
        
    def show_check_list(self, course_id):
        check_list = pd.merge(database.check_list[database.check_list['course_id'] == course_id], database.course_data[['course_id','course_name']])
        return check_list
    
    def show_check_detail(self, check_id):
        check_detail = pd.merge(database.check_item[database.check_item['check_id'] == check_id],database.student_data[['student_name','student_id']])
        return check_detail
    
    def add_check(self, check_data, kw):
        kw['check_id'] = database.check_list['check_id'][len(database.check_list)-1] + 1
        database.check_list.loc[len(database.check_list)] = kw
        database.check_item = pd.concat((check_data, database.check_item)).reset_index(drop=True)
    
    def delete_check(self, check_id):
        database.check_list = database.check_list[~(database.check_list['check_id'] == check_id)]
        database.check_item = database.check_item[~(database.check_item['check_id'] == check_id)]
    
    def modify_check(self, check_data, check_id, kw):
        kw['check_id'] = check_id
        kw['course_id'] = list(database.check_list[database.check_list['check_id'] == check_id]['course_id'])[0]
        self.delete_check(check_id)
        self.add_check(check_data, kw)    
    
    def show_score(self, course_id):
        score = database.score_data[database.score_data['course_id'] == course_id]
        return score
    
    def update_score(self, course_id, scores):
        database.score_data  = database.score_data[~(database.score_data['course_id'] == course_id)]
        database.score_data = pd.concat((scores, database.score_data)).reset_index(drop=True)
    
    def show_student(self,course_id):
        student_list = pd.merge(database.score_data[database.score_data['course_id'] == course_id],database.student_data)
        return student_list

class Student(object):
    def __init__(self, student_id):
        self.student_id = student_id
        self.information = database.student_data[database.student_data['student_id'] == student_id]
        
    def show_course(self):
        course_list = pd.merge(database.score_data[database.score_data['student_id'] == 16050429][['student_id', 'course_id']],database.course_data)
        return course_list
    
    def show_course_detail(self):
        return database.score_data[database.score_data['student_id'] == self.student_id]
    
    def show_information(self):
        return self.information
    
    def modify_information(self, new_information):

        temp = self.information
        for key in new_information.keys():
            if(new_information[key] == ''):
                new_information[key] = list(temp[key])[0]

        new_information['student_id'] = self.student_id
        new_information['student_name'] = list(self.information['student_name'])[0]
        new_information['gpa'] = list(self.information['gpa'])[0]
        new_information['badness'] = list(self.information['badness'])[0]

        
        location = database.student_data[database.student_data['student_id'] == self.student_id].index.tolist()[0]
        database.student_data.loc[location] = pd.Series(new_information)
        self.information = database.student_data[database.student_data['student_id'] == self.student_id]
    
    def show_teacher(self,course_name):
        teacher_list = pd.merge(database.course_data[database.course_data['course_name'] == course_name][['course_name','teacher_id']], database.teacher_data)
        return teacher_list


if __name__=='__main__':
    pass