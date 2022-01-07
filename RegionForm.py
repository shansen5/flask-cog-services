from wtforms import Form, HiddenField, SubmitField, SelectField

class RegionForm( Form ):
    form_name = HiddenField('Region Selection')

    state = SelectField('State:', id='select_state')
    county = SelectField('County:', id='select_county')
    submit = SubmitField('Select County!')

    def validate_on_submit( self ):
        return True