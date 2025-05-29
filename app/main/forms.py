from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
from app.models import Post

class PostForm(FlaskForm):
    clientname = StringField('Name', validators=[DataRequired()])
    clientss = StringField('Social security number', validators=[Optional()])
    clientemail = StringField('Email', validators=[Optional(), Email()])
    clientphone = StringField('Phone', validators=[Optional()])
    clientaddress = StringField('Address', validators=[Optional()])
    clientzip = StringField('ZIP', validators=[Optional()])
    clientcity = StringField('City', validators=[Optional()])
    clientinfo = TextAreaField('Info', validators=[Optional(), Length(max=2048)])  # Or TinyMCEField if you use it
    submit = SubmitField(label='Submit')
    cancel = SubmitField(label='Cancel', render_kw={'formnovalidate': True})

    def validate_clientss(self, clientss):
        if clientss.data:
            existing = Post.query.filter_by(clientss=clientss.data).first()
            if existing is not None:
                raise ValidationError('Social security number must be unique.')

    def validate_clientemail(self, clientemail):
        if clientemail.data:
            existing = Post.query.filter_by(clientemail=clientemail.data).first()
            if existing is not None:
                raise ValidationError('Email already registered.')

class EditPostForm(FlaskForm):
    clientname = StringField('Name', validators=[DataRequired()])
    clientss = StringField('Social security number', validators=[Optional()])
    clientemail = StringField('Email', validators=[Optional(), Email()])
    clientphone = StringField('Phone', validators=[Optional()])
    clientaddress = StringField('Address', validators=[Optional()])
    clientzip = StringField('ZIP', validators=[Optional()])
    clientcity = StringField('City', validators=[Optional()])
    clientinfo = TextAreaField('Info', validators=[Optional(), Length(max=2048)])  # Or TinyMCEField if you use it
    submit = SubmitField(label='Submit')
    cancel = SubmitField(label='Cancel', render_kw={'formnovalidate': True})

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        # Use GET form data (request.args) for searching by default
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        super().__init__(*args, **kwargs)