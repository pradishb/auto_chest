''' Main script of the program '''
import csv
from easygui import fileopenbox

from settings import CSV_DELIMITERS


def main():
    ''' Main function of the program '''
    file_path = fileopenbox()

    with open(file_path, newline='') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=CSV_DELIMITERS)
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        for row in reader:
            print(row['username'], row['password'])


if __name__ == '__main__':
    main()
