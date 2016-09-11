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
    def backup_db(output_dir=False):
        """
        Compress your Kobo database file and save it to a backup folder.
        :return: None
        """

        if not output_dir:
            output_dir = BASE_DIR + '/Backups/'

        now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
        file_name = output_dir + 'KoboDB_backup-{}'.format(now)

        zf = zipfile.ZipFile("{}.zip".format(file_name), "w", zipfile.ZIP_DEFLATED)
        zf.write(BASE_DIR + '/' + 'KoboReader.sqlite', 'Backups/KoboReader.sqlite')
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
    def help():
        print(
            """
            How to use:
            ./kobo.py $command1 $command2

            Second commands only apply to the "highlights" feature.

            This program assumes you have a KoboReader.sqlite file in the same directory.

            Available commands:

            highlights - Get highlights, starting from the oldest highlight
            highlights reverse - Get highlights, starting from the newest highlight
            highlights random - Get highlights in random order
            highlights all - Show all highlights in your DB

            get - Pull the KoboReader.sqlite DB file from your connected reader
            push - Send the local KoboReader.sqlite DB file to your connected reader
            backup - Create a compressed backup of your DB file in the "Backup" directory
            help - Show this screen again
            """
        )

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
        behavior_arg = argv[1].lower()

        operations = {
            'highlights': KoboDB.get_highlights,
            'get': KoboDB.get_db,
            'push': KoboDB.push_db,
            'backup': KoboDB.backup_db,
            'help': KoboDB.help
        }

        if behavior_arg == 'highlights':
            sqlite_file = 'KoboReader.sqlite'

            reverse = True if len(argv) > 2 and argv[2] == 'reverse' else False
            random = True if len(argv) > 2 and argv[2] == 'random' else False
            show_all = True if len(argv) > 2 and argv[2] == 'all' else False

            operations[behavior_arg](sqlite_file,
                                     reverse=reverse,
                                     random=random,
                                     show_all=show_all)
        else:
            operations[behavior_arg]()

    except (KeyError) as e:
        KoboDB.help()
        print(e)
