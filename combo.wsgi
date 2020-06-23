import os
import sys

# add this directory to the Python search path
sys.path.append(os.path.dirname(__file__))

from werkzeug.wsgi import DispatcherMiddleware
from viewer import app as viewer_app
from editor import app as editor_app

application = DispatcherMiddleware(viewer_app, { '/editor': editor_app })
