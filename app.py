from flask import Flask, render_template, url_for, jsonify, request, flash, redirect
# from flask_debugtoolbar import DebugToolbarExtension
import translate
import folium
from CountyForm import CountyForm
from RegionForm import RegionForm
from CDForm import CDForm

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
    
class CD(Base):
    __tablename__ = 'real_cds'

    rowid = Column(Integer, primary_key=True)
    cd = Column(String(40))
    state = Column(String(4))

    def __repr__(self):
        return f"CD(rowid={self.rowid!r}, cd={self.cd!r}, state={self.state!r})"
    
engine_region = create_engine("sqlite:///region.db?check_same_thread=false", echo=True, future=True)
engine_geo = create_engine("sqlite:///geographies.db?check_same_thread=false", echo=True, future=True)

session_region = Session(engine_region)
session_geo = Session(engine_geo)

def get_all_states():
    rows = session_geo.execute(select(State.state)).all()
    result = []
    for row in rows:
        # pdb.set_trace()
        state = row[0]
        result.append((state,state))
    return result

def get_all_counties(state=None):
    if state:
        rows = session_geo.execute(select(County).where(County.state==state))
    else:
        rows = session_geo.execute(select(County)).all()
    result = []
    for row in rows:
        # pdb.set_trace()
        county = row[0]
        result.append((county.rowid, county.county))
    return result

def get_all_CDs(state=None):
    if state:
        rows = session_region.execute(select(CD).where(CD.state==state))
    else:
        rows = session_region.execute(select(CD)).all()
    result = []
    for row in rows:
        # pdb.set_trace()
        cd = row[0]
        result.append((cd.rowid, cd.cd))
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

@app.route('/region_type', methods=['GET', 'POST'])
def region_type():
    form = RegionForm()
    form.form_name = 'PickRegion'
    form.region_type.choices = ['State', 'Congressional District', 'Zip Code', 
         'Watershed', 'County']
    # form.region_type.choices = [(1,'State'), (2,'Congressional Disctict'), (3,'Zip Code'), 
    #     (4,'Watershed'), (5,'County')]
    if request.method == 'GET':
        return render_template('pick_region.html', form=form)
    # Todo: Why doesn't request.form['form_name'] exist?
    # if form.validate_on_submit() and request.form['form_name'] == 'PickRegion':
    if form.validate_on_submit():
        # code to process form
        flash('region: %s' % (form.region_type.data))
        if request.form['region_type'] == 'County':
            return redirect(url_for('pick_county'))
        if request.form['region_type'] == 'Congressional District':
            return redirect(url_for('pick_CD'))
    return redirect(url_for('region_type'))

@app.route('/pick_county', methods=['GET', 'POST'])
def pick_county():
    form = CountyForm()
    form.form_name = 'PickCounty'
    # form.state.choices = [(row.ID, row.Name) for row in State.query.all()]
    # form.county.choices = [(row.ID, row.Name) for row in County.query.all()]
    form.state.choices = get_all_states()
    form.county.choices = get_all_counties()
    if request.method == 'GET':
        return render_template('pick_county.html', form=form)
    # Todo: Why doesn't request.form['form_name'] exist?
    # if form.validate_on_submit() and request.form['form_name'] == 'CountyForm':
    if form.validate_on_submit():
        form.populate_obj(request.form)
        # code to process form
        flash('state: %s, county: %s' % (form.state.data, form.county.data))
        return redirect(url_for('county_report', state=request.form['state'], county=request.form['county']))
    return redirect(url_for('pick_county'))

@app.route('/pick_CD', methods=['GET', 'POST'])
def pick_CD():
    form = CDForm()
    form.form_name = 'PickCD'
    # form.state.choices = [(row.ID, row.Name) for row in State.query.all()]
    # form.county.choices = [(row.ID, row.Name) for row in County.query.all()]
    form.state.choices = get_all_states()
    form.cd.choices = get_all_CDs()
    if request.method == 'GET':
        return render_template('pick_CD.html', form=form)
    # Todo: Why doesn't request.form['form_name'] exist?
    # if form.validate_on_submit() and request.form['form_name'] == 'CountyForm':
    if form.validate_on_submit():
        form.populate_obj(request.form)
        # code to process form
        # flash('state: %s, county: %s' % (form.state.data, form.county.data))
        return redirect(url_for('cd_report', state=request.form['state'], cd=request.form['cd']))
    return redirect(url_for('pick_cd'))

@app.route('/_get_counties/')
def _get_counties():
    state = request.args.get('state', '01', type=str)
    # counties = [(row.rowid, row.county) for row in get_all_counties(state)]
    return jsonify(get_all_counties(state))

@app.route('/_get_CDs/')
def _get_CDs():
    state = request.args.get('state', '01', type=str)
    # counties = [(row.rowid, row.county) for row in get_all_counties(state)]
    return jsonify(get_all_CDs(state))

@app.route('/cd_report')
def cd_report():
    state = request.args.get('state')
    cd = request.args.get('cd')
    return render_template('cd_report.html', state=state, cd=cd)

@app.route('/county_report')
def county_report():
    state = request.args.get('state')
    county = request.args.get('county')
    return render_template('county_report.html', state=state, county=county)

@app.route('/translate-text', methods=['POST'])
def translate_text():
    data = request.get_json()
    text_input = data['text']
    translation_output = data['to']
    response = translate.get_translation(text_input, translation_output)
    return jsonify(response)