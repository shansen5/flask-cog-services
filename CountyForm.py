from wtforms import Form, HiddenField, SubmitField, SelectField, validators

class CountyForm( Form ):
    form_name = HiddenField('County Selection')

    state = SelectField('State:', id='select_state', validators=[validators.DataRequired()])
    county = SelectField('County:', id='select_county', validators=[validators.DataRequired()])
    submit = SubmitField('Select County!')

    def validate_on_submit( self ):
        return True