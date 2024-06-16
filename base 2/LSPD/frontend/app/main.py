from flask import Flask, render_template, request
import requests
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

FASTAPI_BACKEND_HOST = 'http://backend'
BACKEND_URL = f'{FASTAPI_BACKEND_HOST}/query/'

logging.basicConfig(level=logging.DEBUG)

class QueryForm(FlaskForm):
    region = SelectField('Region')
    submit = SubmitField('Submit')


def fetch_date_from_backend():
    backend_url = 'http://backend/get-date'
    try:
        response = requests.get(backend_url)
        response.raise_for_status()
        return response.json().get('date', 'Date not available')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching date from backend: {e}")
        return 'Date not available'


def fetch_regions_from_backend():
    backend_url = 'http://backend/regions'
    try:
        response = requests.get(backend_url)
        response.raise_for_status()
        return response.json().get("regions", [])
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching regions: {e}")
        return []


@app.route('/')
def index():
    date_from_backend = fetch_date_from_backend()
    return render_template('index.html', date_from_backend=date_from_backend)


@app.route('/internal', methods=['GET', 'POST'])
def internal():
    form = QueryForm()
    error_message = None

    regions = fetch_regions_from_backend()
    app.logger.debug(f"Fetched regions: {regions}")
    if isinstance(regions, str):
        error_message = regions
        return render_template('internal.html', form=form, result=None, error_message=error_message)

    form.region.choices = [(r["code"], r["name"]) for r in regions]

    if form.validate_on_submit():
        region = form.region.data
        fastapi_url = f'{FASTAPI_BACKEND_HOST}/query/{region}'
        app.logger.debug(f"Querying FastAPI backend: {fastapi_url}")
        try:
            response = requests.get(fastapi_url)
            response.raise_for_status()
            data = response.json()
            app.logger.debug(f"Received data: {data}")
            if 'parapharmacies' in data:
                result = data['parapharmacies'] or f'Error: No parapharmacies available in region {region}'
                return render_template('internal.html', form=form, result=result, error_message=error_message)
            else:
                error_message = f'Invalid region code {region}'
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error fetching parapharmacies: {e}")
            error_message = ('Error: Unable to fetch available parapharmacies '
                             f'in region {region} from FastAPI Backend')

    return render_template('internal.html', form=form, result=None, error_message=error_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
