# main.py
import database
from gui import run_app

def main():
    database.init_db()
    run_app()

if __name__ == "__main__":
    main()
