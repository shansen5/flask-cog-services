import pdb

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
    
engine = create_engine("sqlite:///geographies.db", echo=True, future=True)

# stmt = text("select County from Counties where State = :state").bindparams(state='CO')

# with Session(engine) as session:
#     result = session.execute(stmt)
#     for row in result:
#         print(f"County: {row.County}")

session = Session(engine)

counties = session.execute(select(County).where(County.state == 'WY')).all()

for county in counties:
    print(county)

states = session.execute(select(State)).all()
for row in states:
    # pdb.set_trace()
    state = row[0]
    print( state.state )