# Import the dependencies.
from flask import Flask, jsonify
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

app = Flask(__name__)

#################################################
# Database Setup
#################################################
current_directory = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_directory, 'Resources', 'hawaii.sqlite')

# Create the engine
engine = create_engine(f"sqlite:///{database_path}")
# Reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

@app.route("/")
def home():
    """List all available routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def get_precipitation():
    """Return the last 12 months of precipitation data."""
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date_value = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date_value - dt.timedelta(days=365)
    
    # Query the precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def get_stations():
    """Return a list of stations."""
    # Query the list of station names
    stations = session.query(Station.station).all()
    
    # Convert the data to a list
    station_list = [station[0] for station in stations]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def get_tobs():
    """Return temperature observations for the most active station for the last year."""
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()[0]
    
    # Calculate the date one year ago from the most recent date
    one_year_ago = most_recent_date_value - dt.timedelta(days=366)
    
    # Query temperature observations for the most active station for the last year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the data to a list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def get_temps_start(start):
    """Return temperature statistics for dates greater than or equal to the start date."""
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    temps_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        first()
    temp_stats = {
        "min_temperature": temps_stats[0],
        "avg_temperature": temps_stats[1],
        "max_temperature": temps_stats[2]
    }
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    """Return temperature statistics for dates between start and end dates."""
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    temps_stats_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        first()
    temp_stats_range = {
        "min_temperature": temps_stats_range[0],
        "avg_temperature": temps_stats_range[1],
        "max_temperature": temps_stats_range[2]
    }
    return jsonify(temp_stats_range)

#################################################
# Flask Run
#################################################
if __name__ == '__main__':
    app.run(debug=True)
