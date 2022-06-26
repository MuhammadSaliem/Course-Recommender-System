# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from re import I, L
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

import os
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users, Course, TakenCourses

from apps.authentication.util import verify_pass

import pandas as pd
from flask import jsonify
from Recommender_Engine import udemy_functions


#import required datasets for recommendation
df_raw = pd.read_csv('C:/Graduation/argon-dashboard-flask-master/data/cleaned/df_courses.csv', delimiter= ' ')
df_courses = pd.read_csv('C:/Graduation/argon-dashboard-flask-master/data/Recommending/df_courses.csv')
df_norm = pd.read_csv('C:/Graduation/argon-dashboard-flask-master/data/Recommending/df_norm.csv')
df_reviews=pd.read_csv('C:/Graduation/argon-dashboard-flask-master/data/cleaned/df_reviews.csv', index_col=0)


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

@blueprint.route('/data')
def data():
    #Add courses to sqlite
    df = df_courses
    lst = []
    for i in range(len(df)):
        course = Course()
        course.course_id = str(df['id'][i])
        course.title = df['published_title'][i]
        course.price = df['price'][i]
        course.image = df['image'][i]
        course.instructor = df['instructor'][i]

        '''s = df['visible_instructdors'][i]
        start = s.find("'title': '") + 10
        end = s.find("', 'name'", start)
        course.instructor = s[start:end]
        '''

        db.session.add(course)
           

    #Add reviews to sqlite
    db.session.commit()
    return jsonify({'ahmed': 15, 'Zena': 23, 'Karim': 23})

#Return list of id of the user taken courses
def userTakenCoursesIds(user):

    username = current_user.username 
    _courseList = TakenCourses.query.filter_by(userId = current_user.id)

    taken_courses = []
    for course in _courseList:
        taken_courses.append(course.courseId)

    return taken_courses    

#Return list of courses taken by a user
def userTakenCourses(username):
    course_id_list= userTakenCoursesIds(current_user.username)
    courseList = []
    for courseid in course_id_list:
        courseList.append(Course.query.filter_by(course_id = courseid).first())
        print(courseid)

    return courseList        

@blueprint.route('/courses', methods = ['GET', 'POST'])    
@login_required
def course():   

    username = current_user.username
    taken_courses = userTakenCoursesIds(username)
    
    if request.method == 'GET':
        if  username !=None :
            df_temp = udemy_functions.recommend_for_user(username , 5,taken_courses, df_courses, df_norm)
            df_temp= df_temp.iloc[1:50][['id','published_title', 'avg_cos_sim', 'image', 'instructor', 'price', 'description_text']]
            return render_template('home/course.html', courses = df_temp, segment= 'none')
        return "No respone bro!"

    if request.method == 'POST':
        #print('***********************', request.form['AddCourseButton'], '**********************')
        df_temp = udemy_functions.recommend_for_user(username , 5,df_reviews, df_courses, df_norm)
        df_temp= df_temp.iloc[1:100][['id', 'published_title', 'avg_cos_sim', 'image', 'instructor', 'price', 'description_text']]
        return render_template('home/course.html', courses = df_temp, segment= 'none')

            
@blueprint.route('/addcourse', methods = ['POST'])    
@login_required
def addCourse():    
    if request.method == 'POST':
        _course = TakenCourses.query.filter_by(courseId = request.form['AddCourseButton'], userId = current_user.id).first()

        if not _course:
            _course = TakenCourses()
            _course.courseId = request.form['AddCourseButton']
            _course.userId = current_user.id
            db.session.add(_course)
            db.session.commit()
            return redirect('/courses')

@blueprint.route('/usercourses', methods = ['GET'])    
@login_required
def userCourses():    
    courseList = userTakenCourses(current_user.username)
    print('*********************************************', courseList[0].course_id)
    return render_template('home/course-list.html', courses = courseList, segment= 'none')

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    user = current_user.username                          
    return redirect(url_for('home_blueprint.index', username = user))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:

            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
