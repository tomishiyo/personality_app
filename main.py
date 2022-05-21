import sys

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
user_db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SECRET_KEY'] = 'secret-key-goes-here'


class User(user_db.Model):
    identifier = user_db.Column(user_db.Integer(), primary_key=True)
    username = user_db.Column(user_db.String())
    password = user_db.Column(user_db.String())


def add_example_user():
    user = User(username='example', password='12345')
    user_db.session.add(user)
    user_db.session.commit()


def read_answer_keys():
    input_name = 'gabarito.csv'
    header = True
    answer_keys = {}
    try:
        with open(input_name) as file:
            for line in file:
                if header:
                    header = False
                else:
                    values = line.strip().split(';')
                    name, alignment, character = values
                    answer_keys[name] = {'alignment': alignment, 'character': character}
        return answer_keys
    except FileNotFoundError:
        print(f'Error: {input_name} file not found!')
        sys.exit()



def main():

    answer_keys = read_answer_keys()
    user_db.create_all()

    # add_example_user()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        if request.method == 'GET':
            return render_template('login.html')
        else:
            form = request.form
            username = form['User']
            password = form['password']
            remember = True if form.get('remember') else False
            user = User.query.filter_by(username=username).first()

            if not user or not user.password == password:
                flash('Login ou senha incorretos')
                return redirect(url_for('login_page'))
            else:
                return 'Success!'


    app.run(host=('192.168.0.97'), debug=True)


if __name__ == '__main__':
    main()




