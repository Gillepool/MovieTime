from flask import Flask
from webassets.loaders import PythonLoader

from movieapp import assets
from movieapp.models import db
from movieapp.controllers.main import main

from movieapp.extensions import (
    cache,
    assets_env,
    debug_toolbar,
    login_manager
)

def create_app(object_name):
    app = Flask(__name__)

    app.config.from_object(object_name)
    cache.init_app(app)
    debug_toolbar.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    assets_env.init_app(app)
    assets_loader = PythonLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    app.register_blueprint(main)
    return app