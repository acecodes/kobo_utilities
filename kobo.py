#!/usr/bin/env python
from __future__ import print_function

import sqlite3
import os

from sys import argv
from random import shuffle
from shutil import copy2

# Backward compatibility
try:
    input = raw_input
except NameError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class KoboDB:
    @staticmethod
    def get_highlights(db_file, reverse=False, random=False):

        db = sqlite3.connect(db_file)
        cursor = db.cursor()

        cursor.execute('''SELECT BookmarkID, VolumeID, Text, DateCreated FROM Bookmark WHERE Hidden IS NOT 'true';''')

        bookmarks = [highlights for highlights in cursor]
        count = 0

        if reverse:
            bookmarks.reverse()

        if random:
            shuffle(bookmarks)

        bookmarks_length = len(bookmarks)

        while count < bookmarks_length:
            print('\n', bookmarks[count][1], '\n\n', bookmarks[count][2], '\n')
            decide = str(input('Do you want to keep this bookmark (y/n/stop)? '))
            if decide == 'n':
                cursor.execute('''UPDATE "main"."Bookmark" SET "Hidden" = "true" WHERE  "BookmarkID" = ?''',
                               (bookmarks[count][0],))
                count += 1
            elif decide == 'stop':
                break
            elif decide == 'y':
                count += 1

        # Do not delete!
        print('Commiting changes to the DB...')
        db.commit()
        print('Closing connection to DB...')
        db.close()

    @staticmethod
    def get_db():
        get_decide = input('This will copy your Kobo\'s DB to disk. Are you sure you want to proceed? (y/n) ')
        if get_decide == 'y':
            print('Copying your Kobo\'s SQLite file to this directory...')
            copy2('/Volumes/KOBOeReader/.kobo/KoboReader.sqlite', BASE_DIR + '/KoboReader.sqlite')
            print('Done copying.')
        else:
            pass

    @staticmethod
    def push_db():
        push_decide = input('This will copy your local DB to your Kobo. Are you sure you want to proceed? (y/n) ')
        if push_decide == 'y':
            print('Copying your local Kobo SQLite file to your Kobo...')
            copy2(BASE_DIR + '/KoboReader.sqlite', '/Volumes/KOBOeReader/.kobo/KoboReader.sqlite')
            print('Done copying SQLite file to your Kobo.')
        else:
            pass


if __name__ == '__main__':

    try:
        sqlite_file = 'KoboReader.sqlite'
        behavior_arg = argv[1]
        behavior_arg = behavior_arg.lower()

        if behavior_arg == 'reverse':
            KoboDB.get_highlights(sqlite_file, reverse=True)
        elif behavior_arg == 'random':
            KoboDB.get_highlights(sqlite_file, random=True)
        elif behavior_arg == 'get':
            KoboDB.get_db()
        elif behavior_arg == 'push':
            KoboDB.push_db()

    except IndexError:
        KoboDB.get_highlights(sqlite_file)
