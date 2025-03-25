import sys
import os
from werkzeug.middleware.profiler import ProfilerMiddleware
from backend import app


app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
app.run(port=8000, debug = True)