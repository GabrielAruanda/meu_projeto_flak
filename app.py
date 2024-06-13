import string
import random
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'url_shortener'

mysql = MySQL(app)

def generate_short_url(long_url):
    letters = string.ascii_lowercase
    short_url = ''.join(random.choice(letters) for i in range(4))  # 4 letras aleatórias
    short_url += ''.join(random.choice(string.digits) for i in range(5))  # 5 números aleatórios
    return short_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']

        cur = mysql.connection.cursor()
        cur.execute("SELECT short_url FROM urls WHERE long_url = %s", (long_url,))
        existing_short_url = cur.fetchone()

        if existing_short_url:
            short_url = existing_short_url[0]
        else:
            short_url = generate_short_url(long_url)
            cur.execute("INSERT INTO urls (long_url, short_url, clicks) VALUES (%s, %s, %s)", (long_url, short_url, 0))
            mysql.connection.commit()

        cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT long_url, short_url, clicks FROM urls")
    urls = cur.fetchall()
    cur.close()

    return render_template('index.html', urls=urls)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    cur = mysql.connection.cursor()
    cur.execute("SELECT long_url FROM urls WHERE short_url = %s", (short_url,))
    long_url = cur.fetchone()
    if long_url:
        cur.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_url = %s", (short_url,))
        mysql.connection.commit()
        cur.close()
        return redirect(long_url[0])
    else:
        return 'URL não encontrada', 404

if __name__ == '__main__':
    app.run(debug=True)
