from wtforms import Form, HiddenField, SubmitField, SelectField, validators

class CDForm( Form ):
    form_name = HiddenField('CD Selection')

    state = SelectField('State:', id='select_state', validators=[validators.DataRequired()])
    cd = SelectField('Congressional District:', id='select_cd', validators=[validators.DataRequired()])
    submit = SubmitField('Select District!')

    def validate_on_submit( self ):
        return True