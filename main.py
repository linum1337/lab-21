import json
import argparse
import sqlite3


def create_tables():
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Scores (
            id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            FOREIGN KEY (team_id) REFERENCES Teams(id)
        )
    ''')
    conn.commit()
    conn.close()


def save_scores_to_db(scores_info):
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()

    for team, score in scores_info.items():
        cursor.execute('INSERT OR IGNORE INTO Teams (name) VALUES (?)', (team,))
        cursor.execute('SELECT id FROM Teams WHERE name = ?', (team,))
        team_id = cursor.fetchone()[0]
        cursor.execute('REPLACE INTO Scores (team_id, score) VALUES (?, ?)', (team_id, score))

    conn.commit()
    conn.close()


def load_scores_from_db():
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Teams.name, Scores.score
        FROM Scores
        JOIN Teams ON Scores.team_id = Teams.id
    ''')
    scores_info = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return scores_info


def save_scores_to_file(scores_info, filename):
    with open(filename, 'w') as file:
        json.dump(scores_info, file, indent=4)


def load_scores_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def main():
    create_tables()

    parser = argparse.ArgumentParser(description="Team Scores CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    save_parser = subparsers.add_parser('save', help="Save team scores to a JSON file or database")
    save_parser.add_argument('filename', type=str, nargs='?', help="The filename to save the scores")
    load_parser = subparsers.add_parser('load', help="Load team scores from a JSON file or database")
    load_parser.add_argument('filename', type=str, nargs='?', help="The filename to load the scores from")
    check_parser = subparsers.add_parser('check', help="Check team positions")
    check_parser.add_argument('filename', type=str, nargs='?', help="The filename to load the scores from")

    args = parser.parse_args()

    if args.command == "save":
        scores_info = {
            "First Team": 100,
            "Second Team": 90,
            "Third Team": 80,
            "Fourth Team": 50,
            "Fifth Team": 30,
        }
        if args.filename:
            save_scores_to_file(scores_info, args.filename)
            print(f"Scores saved to {args.filename}")
        else:
            save_scores_to_db(scores_info)
            print("Scores saved to database")

    elif args.command == "load":
        if args.filename:
            try:
                scores_info = load_scores_from_file(args.filename)
                print(f"Scores loaded from {args.filename}: {scores_info}")
            except FileNotFoundError:
                print(f"File {args.filename} not found")
        else:
            scores_info = load_scores_from_db()
            print(f"Scores loaded from database: {scores_info}")

    elif args.command == "check":
        if args.filename:
            try:
                scores_info = load_scores_from_file(args.filename)
            except FileNotFoundError:
                print(f"File {args.filename} not found")
                return
        else:
            scores_info = load_scores_from_db()

        team_list = [
            input(f"{i + 1}. Enter team name (First Team, Second Team, Third Team, Fourth Team, Fifth Team): \n")
            for i in range(5)
        ]

        if position_checker(scores_info, team_list):
            print("Team positions correct!")
        else:
            print("Team positions incorrect!")


def position_checker(scores_info: dict, team_list: list) -> bool:
    sorted_teams = sorted(scores_info.keys(), key=lambda x: scores_info[x], reverse=True)
    return sorted_teams == team_list


if __name__ == '__main__':
    main()
