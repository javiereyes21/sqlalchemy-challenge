# Import the dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

from flask import Flask, jsonify




#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine)
# reflect the tables
measurement = Base.classes.measurement
station = Base.classes.station

# Save references to each table


# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        "<span style='font-size: 24px;'><strong>Welcome to the Hawaii Climate analysis</strong></span></p>"
        "Available Routes:<br/>"
        "<p>/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/temp/start<br/>"
        "/api/v1.0/temp/start/end<br/>"
        "<p>'start' and 'end' date should be in format MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= prev_year).all()
    
    session.close()
    precip = {date: prcp for date, prcp in precipitation}

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations= stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year= dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= prev_year).all()
    
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/start")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    start= dt.datetime.strptime(start, "%m%d%Y")
    end= dt.datetime.strptime(end, "%m%d%Y")

    results= session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    
    session.close

    temps = list(np.ravel(results))
    
    return jsonify(temps=temps)




def shutdown_session(exception=None):
    session.remove()

if __name__ == "__main__":
    app.run(debug=True)