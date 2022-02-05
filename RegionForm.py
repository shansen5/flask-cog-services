from wtforms import Form, HiddenField, SubmitField, SelectField, validators

class RegionForm( Form ):
    form_name = HiddenField('Region Selection')

    region_type = SelectField('Type of region:', id='select_state', validators=[validators.DataRequired()])
    submit = SubmitField('Select Type!')

    def validate_on_submit( self ):
        return True