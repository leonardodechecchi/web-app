from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('public/home.html')

@app.route('/about')
def about():
    return render_template('public/about.html')

if __name__ == '__main__':
    app.run(debug=True)
