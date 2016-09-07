#!/usr/bin/env python
from __future__ import print_function

import sqlite3
import os
import zipfile
import datetime

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
    def get_highlights(db_file, reverse=False, random=False, show_all=False):
        """
        Extract and present the highlights from your Kobo SQLite file. Each highlight will present
        the user with a choice: keep the highlight, remove it (set it to "hidden") or stop going through highlights.
        Once "stop" is entered or the user reaches the end of their highlights, the DB is saved.

        By default, highlights will be presented in first-last oder.

        :param db_file: Kobo SQLite file. (string)
        :param reverse: Show highlights in last-first order. (Boolean)
        :param random: Show highlights in random order. (Boolean)
        :return: None.
        """

        db = sqlite3.connect(db_file)
        cursor = db.cursor()

        cursor.execute('''SELECT BookmarkID, VolumeID, Text, DateCreated FROM Bookmark WHERE Hidden IS NOT 'true';''')

        bookmarks = [highlights for highlights in cursor]

        if show_all:
            for mark in bookmarks:
                print('\n {} \n\n {} \n'.format(mark[1], mark[2]))
            return

        if reverse:
            bookmarks.reverse()

        if random:
            shuffle(bookmarks)

        count = 0
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
    def backup_db():
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
        file_name = BASE_DIR + '/' + 'KoboDB_backup-{}'.format(now)
        zf = zipfile.ZipFile("{}.zip".format(file_name), "w", zipfile.ZIP_DEFLATED)
        zf.write(BASE_DIR + '/' + 'KoboReader.sqlite', 'Backup/KoboReader.sqlite')
        zf.close()


    @staticmethod
    def get_db():
        """
        Get the SQLite database from your Kobo device.
        :return: None.
        """
        get_decide = input('This will copy your Kobo\'s DB to disk. Are you sure you want to proceed? (y/n) ')
        if get_decide == 'y':
            try:
                print('Copying your Kobo\'s SQLite file to this directory...')
                copy2('/Volumes/KOBOeReader/.kobo/KoboReader.sqlite', BASE_DIR + '/KoboReader.sqlite')
                print('Done copying your Kobo\'s DB to this directory.')
            except FileNotFoundError:
                print('Your Kobo does not appear to be connected. Please plug your Kobo in and try again.')
        else:
            return

    @staticmethod
    def push_db():
        """
        Send your local version of the Kobo SQLite file to the device.
        :return: None.
        """
        push_decide = input('This will copy your local DB to your Kobo. Are you sure you want to proceed? (y/n) ')
        if push_decide == 'y':
            try:
                print('Copying your local Kobo SQLite file to your Kobo...')
                copy2(BASE_DIR + '/KoboReader.sqlite', '/Volumes/KOBOeReader/.kobo/KoboReader.sqlite')
                print('Done copying SQLite file to your Kobo.')
            except FileNotFoundError:
                print('Your Kobo does not appear to be connected. Please plug your Kobo in and try again.')
        else:
            return


if __name__ == '__main__':

    try:
        sqlite_file = 'KoboReader.sqlite'
        behavior_arg = argv[1]
        behavior_arg = behavior_arg.lower()

        if behavior_arg == 'reverse':
            KoboDB.get_highlights(sqlite_file, reverse=True)
        elif behavior_arg == 'random':
            KoboDB.get_highlights(sqlite_file, random=True)
        elif behavior_arg == 'all':
            KoboDB.get_highlights(sqlite_file, show_all=True)
        elif behavior_arg == 'get':
            KoboDB.get_db()
        elif behavior_arg == 'push':
            KoboDB.push_db()
        elif behavior_arg == 'backup':
            KoboDB.backup_db()

    except IndexError:
        KoboDB.get_highlights(sqlite_file)
