from flask import Flask, render_template, url_for, jsonify, request, flash, redirect
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
        result.append(state)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map') 
def map():
    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location=start_coords, zoom_start=14)
    folium_map.save('templates/map.html')
    return render_template('show_map.html')

@app.route('/pick_region')
def pick_region():
    form = RegionForm(form_name='PickCounty')
    # form.state.choices = [(row.ID, row.Name) for row in State.query.all()]
    # form.county.choices = [(row.ID, row.Name) for row in County.query.all()]
    form.state.choices = get_all_states()
    form.county.choices = get_all_counties()
    if request.method == 'GET':
        return render_template('pick_region.html', form=form)
    if form.validate_on_submit() and request.form['form_name'] == 'PickCounty':
        # code to process form
        flash('state: %s, county: %s' % (form.state.data, form.county.data))
    return redirect(url_for('pick_region'))

@app.route('/_get_counties/')
def _get_counties():
    state = request.args.get('state', '01', type=str)
    # counties = [(row.rowid, row.county) for row in get_all_counties(state)]
    return jsonify(get_all_counties(state))