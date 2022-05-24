import sys
import pickle

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

# TODO: Create function to compute all points and sum up the results

class User(UserMixin, user_db.Model):
    identifier = user_db.Column(user_db.Integer(), primary_key=True)
    username = user_db.Column(user_db.String(), unique=True)
    name = user_db.Column(user_db.String())
    password = user_db.Column(user_db.String())
    character = user_db.Column(user_db.String())
    alignment = user_db.Column(user_db.String())
    circle = user_db.Column(user_db.String())

    def get_id(self):
           return self.identifier


def init_answers_db(database_name):
    """Read database from file or create the file is none is found"""
    try:
        with open(database_name, 'rb') as file:
            database = pickle.load(file)
            return database
    except FileNotFoundError:
        return {}


def save_answers_db(dictionary):
    """Save answer database to file"""
    save_name = 'answerdb'
    try:
        with open(save_name, 'wb') as file:
            pickle.dump(dictionary, file)
    except Exception as error:
        print('Unexpected exception: ', error)


def read_answer_keys():
    """"Read the answers from CSV file"""
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

    answers_dict = init_answers_db('answerdb')

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

            if current_user.username not in answers_dict:
                answers_dict[current_user.username] = {}
                user_dict = answers_dict[current_user.username]
            else:
                user_dict = answers_dict[current_user.username]

            if person not in user_dict:
                user_dict[person] = {'alignment': alignment, 'character': character}
                save_answers_db(answers_dict)
                flash(f'Convidado adicionado com sucesso')
                return redirect(url_for('profile_page'))
            else:
                flash('Você já adicionou essa pessoa')
                return redirect(url_for('add_guesses'))


    @app.route('/edit')
    @login_required
    def edit():
        user = current_user.username
        try:
            guests_usernames = [guest for guest in answers_dict[user]]
            guests = [User.query.filter_by(username=username).first() for username in guests_usernames]
            return render_template('edit_main.html', usernames=guests)
        except KeyError:
            flash('Você ainda não adicionou ninguém!')
            return redirect(url_for('profile_page'))


    @app.route('/edit/<i>', methods=['GET', 'POST'])
    @login_required
    def edit_guess(i):
        if request.method == 'GET':
            guest = User.query.filter_by(username=i).first()
            guess_alignment = answers_dict[current_user.username][guest.username]['alignment']
            guess_character = answers_dict[current_user.username][guest.username]['character']
            return render_template('edit_person.html', guess=guest, alignment=guess_alignment,
                                   character = guess_character)
        else:
            guest = User.query.filter_by(username=i).first().username

            form = request.form
            alignment = form['alignment']
            character = form['character']

            answers_dict[current_user.username][guest] = {'alignment': alignment, 'character': character}
            save_answers_db(answers_dict)
            flash('Convidado editado com sucesso')
            return redirect(url_for('profile_page'))


    app.run(host='192.168.0.97', debug=True)


if __name__ == '__main__':
    main()




