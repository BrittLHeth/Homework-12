# import libraries
from sqlalchemy import create_engine
from sqlalchemy import inspect
from flask_sqlalchemy import SQLAlchemy
from flask import (
    Flask,
    render_template,
    jsonify,
    redirect)

import pandas as pd
import os

# #################################################
# # Database setup
# #################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db/belly_button_biodiversity.sqlite"

db = SQLAlchemy(app)

engine = create_engine(os.environ.get('DATABASE_URL', '') or "sqlite:///db/belly_button_biodiversity.sqlite")


# #################################################
# # tables setup
# #################################################
class Otu(db.Model):
    __tablename__ = "otu"
    otu_id = db.Column(db.Integer, primary_key=True)
    lowest_taxonomic_unit_found = db.Column(db.String)


class Metadata(db.Model):
    __tablename__ = "samples_metadata"
    sampleid = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String)
    ethnicity = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)
    wfreq = db.Column(db.Float)
    bbtype = db.Column(db.String)
    location = db.Column(db.String)
    country012 = db.Column(db.String)
    zip012 = db.Column(db.Integer)
    country1319 = db.Column(db.String)
    zip1319 = db.Column(db.Integer)
    dog = db.Column(db.String)
    cat = db.Column(db.String)
    impsurface013 = db.Column(db.Integer)
    npp013 = db.Column(db.Float)
    mmaxtemp013 = db.Column(db.Float)
    pfc013 = db.Column(db.Float)
    impsurface1319 = db.Column(db.Integer)
    npp1319 = db.Column(db.Float)
    mmaxtemp1319 = db.Column(db.Float)
    pfc1319 = db.Column(db.Float)


# #################################################
# # routes configurations
# #################################################
@app.route("/")
def home():
    """Return the dashboard homepage."""
    return render_template("index.html")


@app.route('/names')
def names():
    sample_names = []
    inspector = inspect(engine)
    columns = iter(inspector.get_columns('samples'))
    next(columns)

    for column in columns:
        sample_names.append(column['name'])

    return jsonify(sample_names)


@app.route('/otu')
def otu():
    low_units_list = db.session.query(Otu.lowest_taxonomic_unit_found).all()
    low_units = [l[0] for l in low_units_list]

    return jsonify(low_units)


@app.route('/metadata/<sample>')
@app.route('/metadata')
def metadata(sample="None"):
    metadata = []


    for i in db.session.query(Metadata.age, Metadata.bbtype, Metadata.ethnicity, Metadata.gender, Metadata.location, Metadata.sampleid).all():
        sample_item = {}

        sample_item['SAMPLEID'] = i[5]
        sample_item['AGE'] = i[0]
        sample_item['BBTYPE'] = i[1]
        sample_item['ETHNICITY'] = i[2]
        sample_item['GENDER'] = i[3]
        sample_item['LOCATION'] = i[4]

        metadata.append(sample_item)

    for selection in metadata:
        if sample[3:] == str(selection['SAMPLEID']):
            return jsonify(selection)

    return jsonify(metadata)


@app.route('/wfreq/<sample>')
@app.route('/wfreq')
def wfreq(sample="None"):
    wfreq = []

    for i in db.session.query(Metadata.wfreq, Metadata.sampleid).all():
        wfreq.append(i)

        if sample[3:] == str(i[1]):
            return jsonify(i[0])

    wfreq = ["{}, {}".format(l[0], l[1]) for l in wfreq]

    return jsonify(wfreq)


@app.route('/samples/<sample>')
def samples(sample="None"):
    df = pd.read_sql('SELECT * FROM samples', engine).set_index('otu_id')

    otu_ids = df['BB_{}'.format(sample[3:])].sort_values(ascending=False).index.tolist()
    sample_values = df['BB_{}'.format(sample[3:])].sort_values(ascending=False).tolist()

    otu_ids = [int(i) for i in otu_ids]
    sample_values = [int(i) for i in sample_values]

    result = {'otu_ids': otu_ids, 'sample_values': sample_values}

    return jsonify(result)


if __name__ == "__main__":
    app.run()