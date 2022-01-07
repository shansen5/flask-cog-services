from flask import Flask, render_template, url_for, jsonify, request, flash, redirect
# from flask_debugtoolbar import DebugToolbarExtension
import translate
import folium
from RegionForm import RegionForm

from sqlalchemy import create_engine, text, Column, Integer, String, select
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()

class State(Base):
    __tablename__ = 'States'

    rowid = Column(Integer, primary_key=True)
    state = Column(String(4))

    def __repr__(self):
        return f"State(rowid={self.rowid!r}, state={self.state!r})"

class County(Base):
    __tablename__ = 'Counties'

    rowid = Column(Integer, primary_key=True)
    county = Column(String(40))
    state = Column(String(4))

    def __repr__(self):
        return f"County(rowid={self.rowid!r}, county={self.county!r}, state={self.state!r})"
    
engine = create_engine("sqlite:///geographies.db?check_same_thread=false", echo=True, future=True)

session = Session(engine)

def get_all_states():
    rows = session.execute(select(State.state)).all()
    result = []
    for row in rows:
        # pdb.set_trace()
        state = row[0]
        result.append((state,state))
    return result

def get_all_counties(state=None):
    if state:
        rows = session.execute(select(County).where(County.state==state))
    else:
        rows = session.execute(select(County)).all()
    result = []
    for row in rows:
        # pdb.set_trace()
        county = row[0]
        result.append((county.rowid, county.county))
    return result

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.debug = True
# toolbar = DebugToolbarExtension(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map') 
def map():
    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location=start_coords, zoom_start=14)
    folium_map.save('templates/map.html')
    return render_template('show_map.html')

@app.route('/pick_region', methods=['GET', 'POST'])
def pick_region():
    form = RegionForm()
    form.form_name = 'PickCounty'
    # form.state.choices = [(row.ID, row.Name) for row in State.query.all()]
    # form.county.choices = [(row.ID, row.Name) for row in County.query.all()]
    form.state.choices = get_all_states()
    form.county.choices = get_all_counties()
    if request.method == 'GET':
        return render_template('pick_region.html', form=form)
    # Todo: Why doesn't request.form['form_name'] exist?
    # if form.validate_on_submit() and request.form['form_name'] == 'PickCounty':
    if form.validate_on_submit():
        # code to process form
        flash('state: %s, county: %s' % (form.state.data, form.county.data))
        return redirect(url_for('county_report'))
    return redirect(url_for('pick_region'))

@app.route('/_get_counties/')
def _get_counties():
    state = request.args.get('state', '01', type=str)
    # counties = [(row.rowid, row.county) for row in get_all_counties(state)]
    return jsonify(get_all_counties(state))

@app.route('/county_report')
def county_report():
    return render_template('county_report.html')

@app.route('/translate-text', methods=['POST'])
def translate_text():
    data = request.get_json()
    text_input = data['text']
    translation_output = data['to']
    response = translate.get_translation(text_input, translation_output)
    return jsonify(response)