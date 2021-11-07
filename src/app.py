from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/python_flask_db'
app.config['SECRET_KEY'] = 'thisismyflasksecretkey'

db = SQLAlchemy(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/coin', methods=['POST'])
def find_coin():
    coin_name = request.form.get('coin_name')

    res = News.query.filter_by(coin=coin_name).all()

    if not res:
        URL = "https://coinmarketcap.com/currencies/" + coin_name +"/"
        r = requests.get(URL)

        soup = BeautifulSoup(r.text, 'html.parser')
        header_tags = soup.find_all(['h1'])
        paragraph_tags = soup.find_all(['p'])
        
        for p in paragraph_tags:
            news = News(coin=coin_name, header=header_tags[0].text, paragraph=p.text)
            db.session.add(news)
        db.session.commit()

        res = News.query.filter_by(coin=coin_name).all()
        return render_template('coin.html', results=res)
    

    return render_template('coin.html', results=res)
    

@app.route('/coin', methods=['GET'])
def coin():
    return render_template('coin.html')


class News(db.Model):
    __tablename__ = 'News'
    id = db.Column('id', db.Integer, primary_key=True)
    coin = db.Column('coin', db.String(80))
    header = db.Column('header', db.Text)
    paragraph = db.Column('paragraph', db.Text)

    def __init__(self, coin, header, paragraph):
        self.coin = coin
        self.header = header
        self.paragraph = paragraph


    def __repr__(self):
        return f"News('{self.header}', '{self.paragraph}')"



db.drop_all()
db.create_all()


if __name__ == "__main__":
    app.run(debug=True)







