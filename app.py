from flask import Flask
from flask import request
from sso import sso_main
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'
@app.route("/gpa",methods=['POST'])
def sso_gpa():
    sno=request.form.get("sno")
    password=request.form.get("pwd")
    return sso_main(sno,password)

if __name__ == '__main__':
    app.run()
