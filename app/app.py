from flask import Flask, render_template, request
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_db, initialize_swagger
import requests, json, os


app = Flask(__name__)
totalhtml = "total.html"


def create_app(config=None) -> Flask:

    if config:
        app.config.from_object(get_config_by_name(config))


    # Initialize extensions
    initialize_db(app)

    # Register blueprints
    initialize_route(app)

    # Initialize Swagger
    initialize_swagger(app)

    return app


@app.route("/", methods=["GET", "POST"])
def home():
    total = None
    user_input = None
    error = None
    most_expensive = None
    most_expensive_price = 0
    
    if request.method == "POST":
        user_input = request.form.get("user_input")
        web = f"http://steamcommunity.com/inventory/{user_input}/730/2?l=english&count=5000"
        
        try:
            r = requests.get(web)
            r.raise_for_status()
            data = r.json()
            items = data.get("descriptions", [])

            json_path = os.path.join(app.root_path, 'data', 'skin_730_response.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                database = json.load(f)

            total_price = 0
            for item in items:
                if item.get("marketable") == 1:
                    price = get_price_by_id(item["classid"], database) / 1000
                    if(most_expensive_price < price):
                        most_expensive_price = price
                        most_expensive = item["name"]
                    
                    total_price += price
            
            total = round(total_price,2)
        
        except requests.RequestException:
            error = "Failed to fetch inventory from Steam."
        except json.JSONDecodeError:
            error = "Invalid JSON response from Steam."
        except Exception as e:
            error = f"Unexpected error: {e}"
    
    return render_template(totalhtml, total=total, item=most_expensive, cost = most_expensive_price)
    
    

def get_price_by_id(classid, database):
    classid_str = str(classid)
    for item in database:
        if str(item.get('class_id')) == classid_str:
            return int(item.get('suggested_price'))
    return 0


