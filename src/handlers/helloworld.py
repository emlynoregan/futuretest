from flask import render_template#, request, redirect

def get_helloworld(app):
    @app.route('/', methods=["GET", "POST"])
    def helloworld():
        return render_template("helloworld.html")
