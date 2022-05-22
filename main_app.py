import sys

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
user_db = SQLAlchemy(app)
user_db.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SECRET_KEY'] = 'secret-key-goes-here'

login_manager = LoginManager()
login_manager.login_view = '/'
login_manager.init_app(app)

# TODO: Fix the add/edit guess bug. Problem is storing a dictionary in the SQL table; try to store it in JSON.

class User(UserMixin, user_db.Model):
    identifier = user_db.Column(user_db.Integer(), primary_key=True)
    username = user_db.Column(user_db.String(), unique=True)
    name = user_db.Column(user_db.String())
    password = user_db.Column(user_db.String())
    guesses = user_db.Column(user_db.PickleType())
    character = user_db.Column(user_db.String())
    alignment = user_db.Column(user_db.String())
    circle = user_db.Column(user_db.String())

    def get_id(self):
           return self.identifier


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
        return render_template('profile.html', name=current_user.name, character=current_user.character.capitalize())

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return(redirect(url_for('index')))

    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_guesses():
        if request.method == 'GET':
            guests = User.query.all()
            return render_template('add.html', guests=guests, user=current_user.username)
        else:
            form = request.form
            person = form['pessoas']
            alignment = form['alignment']
            character = form['character']
            if person not in current_user.guesses:
                current_user.guesses[person] = {'alignment': alignment, 'character': character}
                user_db.session.commit()
                flash(f'Convidado adicionado com sucesso')
                return redirect(url_for('profile_page'))
            else:
                flash('Você já adicionou essa pessoa')
                return redirect(url_for('add_guesses'))


    @app.route('/edit')
    @login_required
    def edit():
        guesses = current_user.guesses
        if guesses:
            guesses_names = [guest for guest in guesses]
            return render_template('edit.html', guesses_names = guesses_names)
        else:
            flash('Você ainda não adicionou ninguém!')
            return redirect(url_for('profile_page'))


    app.run(host='192.168.0.97', debug=True)


if __name__ == '__main__':
    main()




