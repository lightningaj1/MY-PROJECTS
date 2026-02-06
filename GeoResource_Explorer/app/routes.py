from app.auth import auth_routes
from app.minerals import mineral_routes
from app.admin import admin_routes
from app.prices import price_routes
from app.map import map_routes
from app.professional import professional_routes
from app.mapping import mapping_routes
from app.geospatial import geospatial_routes
from app.deposits import deposit_routes
from app.learning import learning_routes

def register_routes(app):
    auth_routes(app)
    mineral_routes(app)
    admin_routes(app)
    price_routes(app)
    map_routes(app)
    professional_routes(app)
    mapping_routes(app)
    geospatial_routes(app)
    deposit_routes(app)
    learning_routes(app)
