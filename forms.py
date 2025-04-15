from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('farmer', 'Farmer'), ('company', 'Company')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class FarmerProfileForm(FlaskForm):
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[Length(max=200)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    bio = TextAreaField('Bio')
    submit = SubmitField('Save Profile')


class CompanyProfileForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    industry_type = StringField('Industry Type', validators=[Length(max=100)])
    address = StringField('Address', validators=[Length(max=200)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    description = TextAreaField('Company Description')
    submit = SubmitField('Save Profile')


class PelletListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    biomass_type = SelectField('Biomass Type', 
                               choices=[('wood', 'Wood Pellets'), 
                                        ('agricultural', 'Agricultural Residue'), 
                                        ('straw', 'Straw Pellets'),
                                        ('grass', 'Grass Pellets'),
                                        ('other', 'Other')], 
                               validators=[DataRequired()])
    quantity = FloatField('Quantity (tons)', validators=[DataRequired()])
    price_per_ton = FloatField('Price per Ton ($)', validators=[DataRequired()])
    description = TextAreaField('Description')
    availability_date = DateField('Available From', format='%Y-%m-%d', validators=[DataRequired()])
    location = StringField('Location', validators=[Length(max=100)])
    submit = SubmitField('List Pellets')


class RequirementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    biomass_type = SelectField('Biomass Type Needed', 
                              choices=[('wood', 'Wood Pellets'), 
                                      ('agricultural', 'Agricultural Residue'), 
                                      ('straw', 'Straw Pellets'),
                                      ('grass', 'Grass Pellets'),
                                      ('any', 'Any Type'),
                                      ('other', 'Other')], 
                              validators=[DataRequired()])
    quantity_needed = FloatField('Quantity Needed (tons)', validators=[DataRequired()])
    price_per_ton = FloatField('Budget per Ton ($)', validators=[])
    description = TextAreaField('Additional Details')
    needed_by_date = DateField('Needed By', format='%Y-%m-%d')
    submit = SubmitField('Post Requirement')


class OfferForm(FlaskForm):
    quantity = FloatField('Quantity (tons)', validators=[DataRequired()])
    price_per_ton = FloatField('Price per Ton ($)', validators=[DataRequired()])
    message = TextAreaField('Message')
    submit = SubmitField('Submit Offer')


class OrderForm(FlaskForm):
    quantity = FloatField('Quantity (tons)', validators=[DataRequired()])
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired()])
    delivery_date = DateField('Requested Delivery Date', format='%Y-%m-%d')
    submit = SubmitField('Place Order')
