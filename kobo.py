#!/usr/bin/env python

import sqlite3

from sys import argv
from random import shuffle


class KoboDB:
    def __init__(self, db_file):
        self.db_file = db_file

    def get_highlights(self, reverse=False, random=False):

        db_file = self.db_file

        db = sqlite3.connect(db_file)
        cursor = db.cursor()

        cursor.execute('''SELECT BookmarkID, VolumeID, Text, DateCreated FROM Bookmark WHERE Hidden IS NOT 'true';''')

        bookmarks = [highlights for highlights in cursor]
        count = 0

        if reverse:
            bookmarks.reverse()

        if random:
            shuffle(bookmarks)

        while count < len(bookmarks):
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


if __name__ == '__main__':

    kobo = KoboDB('KoboReader.sqlite')

    try:
        args = argv[1]

        if args == 'reverse':
            kobo.get_highlights(reverse=True)
        if args == 'random':
            kobo.get_highlights(random=True)
        else:
            kobo.get_highlights()

    except IndexError:
        kobo.get_highlights()
