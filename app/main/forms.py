from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length


# Forms
class PostForm(FlaskForm):
    clientname = StringField('Name', validators=[DataRequired()])
    clientss = StringField('Social security number', validators=[Optional()])
    clientemail = StringField('Email', validators=[DataRequired()])
    clientphone = StringField('Phone', validators=[DataRequired()])
    clientaddress = StringField('Address', validators=[Optional()])
    clientzip = StringField('ZIP', validators=[Optional()])
    clientcity = StringField('City', validators=[Optional()])
    clientinfo = TextAreaField('Info',
                               validators=[Optional(), Length(max=2048)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')
