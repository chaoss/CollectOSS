import json
from flask import Flask, request, Response, send_from_directory, redirect, flash
from flask_login import LoginManager, current_user, login_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email
from ..models import User
from ..util import logger
import os




class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('rememberme')
    submit = SubmitField('signin')



class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    submit = SubmitField('signin')




def create_user_routes(server):

    login_manager = LoginManager()
    login_manager.init_app(server.app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @server.app.route(f'/login', methods=['POST'])
    def login():
        form = LoginForm(request.form)
        nxt = request.args.get('next')
        err = request.args.get('err')
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                if login_user(user):
                    logger.info('Logged in user: %s', user.username)
                else:
                    logger.info('Failed to login user: %s', user.username)
            else:
                flash('Bad password')
                return redirect(err or '/login?wrong=1')
        else:
            flash('Form invalid')
            return redirect(err or '/login?invalid=1')
        return redirect(nxt or '/')


    @server.app.route(f'/register', methods=['POST'])
    def register():
        form = RegistrationForm(request.form)
        nxt = request.args.get('next')
        err = request.args.get('err')
        if request.method == 'POST' and form.validate():
            user = User(username=form.username.data, email=form.email.data)
            user.password = form.password.data
            server._augur.session.add(user)
            server._augur.session.commit()
            flash('Registration successful')
        else:
            return redirect(err or '/')
        return redirect(nxt or '/')


    @server.app.route(f'/{server.api_version}/me', methods=['GET', 'POST'])
    @login_required
    def me():
        return current_user.username
