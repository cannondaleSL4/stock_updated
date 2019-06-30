from const import all_instruments

from database import select_from_database_last_record


def check_database(list_of_instruments):
    for instrument in list_of_instruments:
        temp = select_from_database_last_record(all_instruments.get(instrument))
        print("ee")


if __name__ == "__main__":
    check_database(list(all_instruments.keys()))