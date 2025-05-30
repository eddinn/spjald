from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Optional,
    Length, ValidationError
)
from app.models import Post


# Forms
class PostForm(FlaskForm):
    clientname = StringField('Name', validators=[DataRequired()])
    clientss = StringField('Social security number', validators=[Optional()])
    clientemail = StringField(
        'Email',
        validators=[Optional(), EqualTo('clientemail'), Email()]
    )
    clientphone = StringField('Phone', validators=[Optional()])
    clientaddress = StringField('Address', validators=[Optional()])
    clientzip = StringField('ZIP', validators=[Optional()])
    clientcity = StringField('City', validators=[Optional()])
    clientinfo = TextAreaField(
        'Info', validators=[Optional(), Length(max=2048)]
    )
    submit = SubmitField(label='Submit')
    cancel = SubmitField(
        label='Cancel',
        render_kw={'formnovalidate': True}
    )

    @staticmethod
    def validate_clientss(form, clientss):
        clientss_obj = Post.query.filter_by(clientss=clientss.data).first()
        if clientss_obj is not None:
            raise ValidationError('Social security number must be unique.')

    @staticmethod
    def validate_clientemail(form, clientemail):
        clientemail_obj = Post.query.filter_by(clientemail=clientemail.data).first()
        if clientemail_obj is not None:
            raise ValidationError('Email already registered.')


class EditPostForm(FlaskForm):
    clientname = StringField('Name', validators=[DataRequired()])
    clientss = StringField('Social security number', validators=[Optional()])
    clientemail = StringField(
        'Email',
        validators=[Optional(), EqualTo('clientemail'), Email()]
    )
    clientphone = StringField('Phone', validators=[Optional()])
    clientaddress = StringField('Address', validators=[Optional()])
    clientzip = StringField('ZIP', validators=[Optional()])
    clientcity = StringField('City', validators=[Optional()])
    clientinfo = TextAreaField(
        'Info', validators=[Optional(), Length(max=2048)]
    )
    submit = SubmitField(label='Submit')
    cancel = SubmitField(
        label='Cancel',
        render_kw={'formnovalidate': True}
    )


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

    class Meta:
        # Disable CSRF for GET-based search form
        csrf = False

    def __init__(self, *args, **kwargs):
        # Populate from query string instead of form body
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        super().__init__(*args, **kwargs)