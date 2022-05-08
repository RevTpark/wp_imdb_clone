from wsgiref.validate import validator
from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo, ValidationError
from models import User

class RegisterUserForm(FlaskForm):
    email = StringField(label='Email Address',validators=[InputRequired(), Email(message="Enter a valid email"),Length(max=255)], render_kw={"placeholder": "john.smith@gmail.com"})
    name = StringField(label='Name', validators=[InputRequired(),Length(max=200)], render_kw={"placeholder": "John Smith"})
    address = StringField(label='Address', validators=[InputRequired()], render_kw={"placeholder": "123 Main St"})
    city = StringField(label='City', validators=[InputRequired(),Length(max=100)], render_kw={"placeholder": "Mumbai"})
    state = SelectField(label='State',choices=["Maharashtra", "Goa", "Kerela"], validators=[InputRequired()])
    pin_code = StringField(label='Pincode', validators=[InputRequired(), Regexp('^\d{6}$', message="Pincode must be 6 digits only.")], description="Pincode must be 6 digits only.", render_kw={"placeholder": "422007"})
    phone_number = StringField(label='Mobile Number', validators=[InputRequired(), Regexp('^\d{10}$', message="Mobile Number must be 10 digits only.")], description="Mobile Number must be 10 digits only.", render_kw={"placeholder": "9876543210"})
    password = PasswordField('Password', validators=[InputRequired(), Length(max=255), Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', message='There must be at minumum 8 characters, at least one uppercase and one lowercase letter, one digit and one special character from @$!%*?&')], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(max=255), EqualTo('password', message='Password must match')], render_kw={"placeholder": "Re-enter Password"})

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("User with this email already exists")


class LoginForm(FlaskForm):
    email = StringField(label='Email Address',validators=[InputRequired(), Email(message="Enter a valid email"),Length(max=255)], render_kw={"placeholder": "john.smith@gmail.com"})
    password = PasswordField('Password', validators=[InputRequired(), Length(max=255)], render_kw={"placeholder": "Password"})

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError("Email does not match our records.")


class UpdateUserForm(FlaskForm):
    name = StringField(label='Name', validators=[InputRequired(),Length(max=200)], render_kw={"placeholder": "John Smith"})
    address = StringField(label='Address', validators=[InputRequired()], render_kw={"placeholder": "123 Main St"})
    city = StringField(label='City', validators=[InputRequired(),Length(max=100)], render_kw={"placeholder": "Mumbai"})
    state = SelectField(label='State',choices=["Maharashtra", "Goa", "Kerela"], validators=[InputRequired()])
    pin_code = StringField(label='Pincode', validators=[InputRequired(), Regexp('^\d{6}$', message="Pincode must be 6 digits only.")], description="Pincode must be 6 digits only.", render_kw={"placeholder": "422007"})
    phone_number = StringField(label='Mobile Number', validators=[InputRequired(), Regexp('^\d{10}$', message="Mobile Number must be 10 digits only.")], description="Mobile Number must be 10 digits only.", render_kw={"placeholder": "9876543210"})