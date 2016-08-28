#!/usr/bin/env python

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class KoboDB:

    def __init__(self, db_file):
        self.db_file = db_file

    def get_highlights(self):

        db_file = self.db_file

        db = sqlite3.connect(db_file)
        cursor = db.cursor()

        cursor.execute('''select BookmarkID, VolumeID, Text, DateCreated from Bookmark WHERE Hidden IS NOT 'true';''')

        bookmarks = [highlights for highlights in cursor]
        count = 0

        while count < len(bookmarks):
            print('\n', bookmarks[count][2], '\n')
            decide = input('Do you want to keep this bookmark (y/n/stop)? ')
            if decide == 'n':
                cursor.execute('''UPDATE "main"."Bookmark" SET "Hidden" = "true" WHERE  "BookmarkID" = ?''', (bookmarks[count][0],))
                count += 1
            elif decide == 'stop':
                break
            else:
                count += 1

        # Do not delete!
        print('Commiting changes to the DB...')
        db.commit()
        print('Closing connection to DB...')
        db.close()

if __name__ == '__main__':

    kobo = KoboDB('KoboReader.sqlite')
    kobo.get_highlights()

