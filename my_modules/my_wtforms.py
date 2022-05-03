from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import datetime

# StringField : text박스
# RadioField : radio버튼
# SubmitField : submit 버튼
# IntegerField : 숫자만 입력가능한 text박스
# DataRequired : 유효성검사

class login_form(FlaskForm):
    # ImmutableMultiDict([('user_id', 'A'), ('user_pw', '1234')])
    user_id = StringField('ID',validators=[DataRequired(), Length(max=10)])
    user_pw = PasswordField('PW',validators=[DataRequired(), Length(max=10)])
    submit = SubmitField()

class register_form(FlaskForm):
    # ImmutableMultiDict([('user_id', 'A'), ('user_pw', '123'), ('user_sex', 'M'), ('user_yb', '2000')])
    user_id = StringField(label='ID',validators=[DataRequired(), Length(max=10)])
    user_pw = PasswordField(label='PW',validators=[DataRequired(), Length(max=10)])
    user_sex = RadioField(label='성별',choices=[('M','남자'), ('F','여자')], default='M')       #('M','남자') : value="M", label="남자"
    # year of birth
    year_of_adult = datetime.today().year-18        # datetime.today().year-18 : 성인
    user_yb = IntegerField(label='태어난해',validators=[DataRequired(), NumberRange(min=1900,max=year_of_adult)], default=year_of_adult)