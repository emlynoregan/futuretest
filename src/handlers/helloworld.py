from flask import render_template#, request, redirect
from megatest import register_test
from taskutils.task import PermanentTaskFailure

def get_helloworld(app):
    @app.route('/hw', methods=["GET", "POST"])
    def helloworld():
        return render_template("helloworld.html")

@register_test
def firsttest(futurekey):
    pass

@register_test(tags=["fails"])
def secondtest(futurekey):
    raise PermanentTaskFailure("This test fails")

