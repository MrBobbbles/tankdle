from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tanks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)




class Tank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year_first_built = db.Column(db.String(100), nullable=False)
    year_entered_service = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    number_built = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.String(100), nullable=False)
    engine_power = db.Column(db.String(100), nullable=False)




    def __repr__(self):
        return f'<Tank {self.name}>'

@app.route('/')
def home():
    tanks = Tank.query.all()
    return render_template('home.html', tanks=tanks)

@app.route('/setTank', methods=['GET', 'POST'])
def set_tank():
    tanks = Tank.query.all()
    if request.method == 'POST':
        selected_tank_id = request.form.get('selected_tank_id')
        if selected_tank_id:
            # You can perform actions with the selected tank ID here
            session['selected_tank_id'] = selected_tank_id
            return f"Tank with ID {selected_tank_id} selected!"

        else:
            return "No tank selected!"
    return render_template('set_tank.html', tanks=tanks)



@app.route('/scrape')
def scrape():
    # Clear the Tank table
    db.session.query(Tank).delete()
    db.session.commit()

    url = 'https://en.wikipedia.org/wiki/List_of_main_battle_tanks_by_generation'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    tank_tables = soup.find_all('table', {'class': 'wikitable'})[:3]
    for tank_table in tank_tables:
        rows = tank_table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) > 8:
                name_cell = cols[0]
                rowspan = int(name_cell.get('rowspan', 1))  # Get rowspan attribute, default to 1
                name = name_cell.text.strip().split('[')[0]  # Remove footnotes
                year_first_built_text = cols[1].text.strip().split(' ')[0].split('(')[0]
                year_first_built = None
                if year_first_built_text.isdigit():
                    year_first_built = int(year_first_built_text)
                else:
                    year_first_built = "NA"  # Replace with "NA" if not a valid year
                year_entered_service_text = cols[2].text.strip().split(' ')[0].split('(')[0]
                year_entered_service = None
                if year_entered_service_text.isdigit():
                    year_entered_service = int(year_entered_service_text)
                else:
                    year_entered_service = "NA"  # Replace with "NA" if not a valid year
                
                origin = cols[3].text.strip().split('|')[-1]        
            
                number_built = None
                number_built = cols[4].text.strip().replace(",","").split('[')[0]   # Remove footnotes

                weight = None
                weight = cols[5].text.strip().split(" ")[0].replace(",","").split('[')[0]   # Remove footnotes
                
                engine_power = None
                engine_power = cols[6].text.strip().split(" ")[0].replace(",","").split('[')[0]  # Remove footnotes

                add_tank(name, year_first_built, year_entered_service, origin, number_built, weight, engine_power)

    
    return 'Scraped and saved tank data successfully!'


def add_tank(name, year_first_built, year_entered_service, origin, number_built, weight, engine_power):
    tank = Tank(
        name=name,
        year_first_built=year_first_built,
        year_entered_service=year_entered_service,
        origin=origin,
        number_built = number_built,
        weight = weight,
        engine_power = engine_power
    )
    db.session.add(tank)
    db.session.commit()

@app.route('/choose')
def choose():
    tanks = Tank.query.all()
    return render_template('chose.html', tanks=tanks)

@app.route('/compare', methods=['POST'])
def compare():
    selected_tank_id = request.form.get('tankSelect')
    selected_tank = Tank.query.get(selected_tank_id)
    random_tank_id = session.get('selected_tank_id')
    random_tank = Tank.query.get(random_tank_id)
    comparison_result = {
        'selected_tank': {
            'name': selected_tank.name,
            'year_first_built': selected_tank.year_first_built,
            'year_entered_service': selected_tank.year_entered_service,
            'origin': selected_tank.origin,
            'number_built': selected_tank.number_built
        },
        'random_tank': {
            'name': random_tank.name,
            'year_first_built': random_tank.year_first_built,
            'year_entered_service': random_tank.year_entered_service,
            'origin': random_tank.origin,
            'number_built': random_tank.number_built
        },
        'is_same_properties': {
            'name': selected_tank.name == random_tank.name,
            'year_first_built': selected_tank.year_first_built == random_tank.year_first_built,
            'year_entered_service': selected_tank.year_entered_service == random_tank.year_entered_service,
            'origin': selected_tank.origin == random_tank.origin,
            'number_built': selected_tank.number_built == random_tank.number_built
        }
    }

    return jsonify(comparison_result)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
