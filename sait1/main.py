from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from cloudipsp import Api, Checkout

#working with date basa
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_DATABASE_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    

    def __repr__(self):
        return self.id

@app.route('/')
def index():
    items = Item.query.order_by(Item.id).all()[::-1]
    return render_template('index.html', data=items)


@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
def valid_login(name,password):
    return name == password
def log_the_user_in(name):
    return "Hello, you are an authorized user "+name
def log_the_user_notin(name):
    return "Hello, you are not an authorized user "+name

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'

    return render_template('login.html', error=error)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']
        items = Item(title=title, price=price, text = text)

        try:
            db.session.add(items)
            db.session.commit()
            return redirect('/')
        except:
            return "Error"
    else:
        return render_template('create.html')

@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)

@app.route('/posts')
def posts():
    items = Item.query.order_by(Item.id).all()
    return render_template('posts.html', data=items)


@app.route('/posts/<int:id>')
def post_detail(id):
    items = Item.query.get(id)
    return render_template('post_detail.html', data=items)


@app.route('/posts/<int:id>/delete')
def post_delete(id):
    items = Item.query.get_or_404(id)

    try:
        db.session.delete(Item)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'Error occurred while deleting Items.'



@app.route('/posts/<int:id>/edit', methods=['POST', 'GET'])
def post_edit(id):
    items = Item.query.get(id)
    if request.method == 'POST':
        items.title = request.form['title']
        items.price = request.form['price']
        items.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return 'Error occurred while editing posts.'
    else:
        return render_template('post_edit.html', data=items)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
