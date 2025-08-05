from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, IntegerField, FloatField, FieldList, FormField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    is_active = BooleanField('Active', default=True)
    version = StringField('Version', validators=[Optional(), Length(max=50)], default='v1')

class QuestionOptionForm(FlaskForm):
    option = StringField('Option', validators=[DataRequired(), Length(min=1, max=200)])

class QuestionForm(FlaskForm):
    quiz_id = IntegerField('Quiz ID', validators=[DataRequired()])
    page_number = IntegerField('Page Number', validators=[DataRequired(), NumberRange(min=1)])
    question_type = SelectField('Question Type', 
                               choices=[
                                   ('demographics', 'Demographics'),
                                   ('multiple_choice', 'Multiple Choice'),
                                   ('yes_no', 'Yes/No'),
                                   ('rating', 'Rating Scale')
                               ],
                               validators=[DataRequired()])
    question_text = TextAreaField('Question Text', validators=[DataRequired(), Length(min=1, max=1000)])
    options = TextAreaField('Options (one per line)', validators=[Optional()], 
                           description='For multiple choice questions, enter one option per line')
    required = BooleanField('Required', default=True)
    order_index = IntegerField('Order Index', validators=[DataRequired(), NumberRange(min=1)])
    weight = FloatField('Weight', validators=[Optional(), NumberRange(min=0)], default=1.0)
    is_active = BooleanField('Active', default=True)
    
    def validate_options(self, field):
        if self.question_type.data == 'multiple_choice' and not field.data:
            raise ValidationError('Options are required for multiple choice questions')
    
    def get_options_list(self):
        if self.options.data:
            return [opt.strip() for opt in self.options.data.split('\n') if opt.strip()]
        return []
    
    def set_options_from_list(self, options_list):
        if options_list:
            self.options.data = '\n'.join(options_list)