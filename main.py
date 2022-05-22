import sys

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
user_db = SQLAlchemy(app)
user_db.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SECRET_KEY'] = 'secret-key-goes-here'

login_manager = LoginManager()
login_manager.login_view = '/'
login_manager.init_app(app)


class User(UserMixin, user_db.Model):
    identifier = user_db.Column(user_db.Integer(), primary_key=True)
    username = user_db.Column(user_db.String())
    name = user_db.Column(user_db.String())
    password = user_db.Column(user_db.String())

    def get_id(self):
           return self.identifier


def add_example_user():
    user = User(username='leonardocavalcante', password='coxinha123', name='Teti')
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

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    @app.route('/', methods=['GET', 'POST'])
    def index():
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
                return redirect(url_for('index'))
            else:
                login_user(user, remember=remember)
                return redirect(url_for('profile_page'))

    @app.route('/profile')
    @login_required
    def profile_page():
        return render_template('profile.html', name=current_user.name)

    app.run(host=('192.168.0.97'), debug=True)


if __name__ == '__main__':
    main()




