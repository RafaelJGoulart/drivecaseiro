from flask import Flask,render_template
from services.storage import info
app = Flask(__name__)

#Rotas
@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/dashboards")
def dashboard():
    return {
            "storage": info()
    }

if __name__ == "__main__":
    app.run(debug=True)
