import pickle

from main_app import User


def load_answers(answer_file):
    """Read database from file or create the file is none is found"""
    with open(answer_file, 'rb') as file:
        database = pickle.load(file)
        return database


def compute_scores(answers):
    """"Query the user database for the correct answer and comparare it to the guests answers, returning scores
        Criteria: +2 points for guessing character of different circle; +1 for same circle
                  +1 for guessing alignment of different circle; 0 for same circle"""

    guests = User.query.all()
    guest_scores = {}

    for user_contender in guests:
        user_score = 0
        contender = user_contender.username
        try:
            contender_answers = answers[contender]
            for guessed_person in contender_answers:
                guessed_person_user = User.query.filter_by(username=guessed_person).first()

                correct_alignment = guessed_person_user.alignment
                correct_character = guessed_person_user.character

                guesser_circle = user_contender.circle
                guessed_circle = guessed_person_user.circle

                guessed_alignment = contender_answers[guessed_person]['alignment'].lower()
                guessed_character = contender_answers[guessed_person]['character'].lower()

                if guesser_circle == guessed_circle:
                    if guessed_character == correct_character:
                        user_score += 1
                else:
                    if guessed_character == correct_character:
                        user_score += 2
                    if guessed_alignment == correct_alignment:
                        user_score += 1

            guest_scores[contender] = user_score

        except KeyError:
            guest_scores[contender] = 0
            pass

    return guest_scores


def get_winners(high_score):
    return sorted(high_score.items(), key=lambda x: x[1], reverse=True)


def announce_winners(winners):
    first_place_username, first_score = winners[0]
    second_place_username, second_score = winners[1]
    third_place_username, third_score = winners[2]

    first_place = User.query.filter_by(username=first_place_username).first().name.upper()
    second_place = User.query.filter_by(username=second_place_username).first().name.upper()
    third_place = User.query.filter_by(username=third_place_username).first().name.upper()

    print(f'Em terceiro lugar, com {third_score} pontos...')
    input()
    print(f'{third_place}!!!')

    print(f'Em segundo lugar, com {second_score} pontos...')
    input()
    print(f'{second_place}!!!')

    print(f'Em primeiro lugar, com {first_score} pontos...')
    input('...')
    input('...')
    input('...')
    print(f'{first_place}!!!')


def main():
    answers = load_answers('answerdb')
    score = compute_scores(answers)
    winners = get_winners(score)
    announce_winners(winners)


if __name__ == '__main__':
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    main()
