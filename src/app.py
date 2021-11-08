from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:785213@localhost:5432/pythonFlaskDB'
app.config['SECRET_KEY'] = 'thisismyflasksecretkey'

db = SQLAlchemy(app)


def refactoreCoinName(coin): # For example "Binance Coin" -> "binance-coin"
    result = str(coin.lower())
    splittedCoin = result.split()
    if len(splittedCoin) > 1:
      result = str(splittedCoin[0])
      for i in range(1, len(splittedCoin)):
        result += "-" + splittedCoin[i]
    return result


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/news', methods=['POST'])
def find_coin_news():
    coin_name = refactoreCoinName(request.form.get('coin_name'))

    res = News.query.filter_by(coin=coin_name).all()

    if not res:
        URL = "https://coinmarketcap.com/currencies/" + coin_name +"/news/"
        opts = webdriver.ChromeOptions()
        opts.headless =True
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=opts)

        r = browser.get(URL)

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        headers_list = soup.find_all('h3', {'class': 'sc-1q9q90x-0 gEZmSc'})
        p_list = soup.find_all('p', {'class': 'sc-1eb5slv-0 svowul-3 ddtKCV'})
        headers_text = [h.text for h in headers_list]
        p_text = [p.text for p in p_list]

        for i in range(0, len(headers_text)):
            news = News(coin=coin_name, header=headers_text[i], paragraph=p_text[i])
            db.session.add(news)
        db.session.commit()

        res = News.query.filter_by(coin=coin_name).all()
        return render_template('news.html', results=res)
    
    return render_template('news.html', results=res)
    

@app.route('/news', methods=['GET'])
def coin_news():
    return render_template('news.html')


@app.route('/paragraphs', methods=['POST'])
def find_coin_paragraphs():
    coin_name = refactoreCoinName(request.form.get('coin_name'))

    res = News.query.filter_by(coin=coin_name).all()

    if not res:
        URL = "https://coinmarketcap.com/currencies/" + coin_name +"/"
        r = requests.get(URL)

        soup = BeautifulSoup(r.text, 'html.parser')
        header_tags = soup.find_all(['h1'])
        paragraph_tags = soup.find_all(['p'])
        
        for p in paragraph_tags:
            paragraphs = Paragraphs(coin=coin_name, header=header_tags[0].text, paragraph=p.text)
            db.session.add(paragraphs)
        db.session.commit()

        res = Paragraphs.query.filter_by(coin=coin_name).all()
        return render_template('paragraphs.html', results=res)

    return render_template('paragraphs.html', results=res)


@app.route('/paragraphs', methods=['GET'])
def coin_paragraphs():
    return render_template('paragraphs.html')


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


class Paragraphs(db.Model):
    __tablename__ = 'Paragraphs'
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