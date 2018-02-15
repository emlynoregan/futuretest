import logging

from flask import Flask
from megatest_flask import register_tests_api
from taskutils import setuptasksforflask
  
app = Flask(__name__)

from handlers.helloworld import get_helloworld

get_helloworld(app)
register_tests_api(app)
setuptasksforflask(app)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


