#!/usr/bin/env python
from __future__ import print_function
from argparse import ArgumentParser

import sqlite3
import os
import zipfile
import datetime
import time

from sys import argv
from random import shuffle
from shutil import copy2


# Backward compatibility
try:
    input = raw_input
except NameError:
    pass

# The file you want to use for the 'highlights' series of commands
if 'KOBO_DB' not in os.environ:
    KOBO_DB = 'KoboReader.sqlite'
else:
    KOBO_DB = os.environ['KOBO_DB']

# The path to your Kobo reader's SQLite file once plugged in via USB
if 'KOBO_READER' not in os.environ:
    # Defaults to Mac OS X location
    KOBO_READER = '/Volumes/KOBOeReader/.kobo/KoboReader.sqlite'
else:
    KOBO_READER = os.environ['KOBO_READER']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class KoboDB:
    @staticmethod
    def get_highlights(db_file, reverse=False, random=False, 
        show_all=False, grouped=False, half=False, custom_start=False,
        delete=False):
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

        if not grouped:
            cursor.execute('''SELECT BookmarkID, VolumeID, Text, DateCreated FROM Bookmark WHERE Hidden IS NOT 'true';''')
        else:
            cursor.execute('''SELECT BookmarkID, VolumeID, Text, DateCreated FROM Bookmark WHERE Hidden IS NOT 'true' ORDER BY VolumeID;''')

        bookmarks = [highlights for highlights in cursor]

        if delete:
            if type(delete) == int:
                content = '\n {} \n {} \n'.format(bookmarks[delete][1], bookmarks[delete][2])
                cursor.execute('''UPDATE "main"."Bookmark" SET "Hidden" = "true" WHERE  "BookmarkID" = ?''',
                                   (bookmarks[delete][0],))
                print('Highlight number {} deleted (technically, hidden).'.format(delete))
                print('\n Content of deleted (hidden) highlight: {}'.format(content))

            elif type(delete) == bool and delete == True:
                remove_these_highlights = [int(i) for i in input('\nPlease enter the numbers (separated by commas) of all the highlights you would like to remove (hide):\n').split(',')]
                for hi in remove_these_highlights:
                    content = '\n {} \n {} \n'.format(bookmarks[hi][1], bookmarks[hi][2])
                    print('Highlight number:', hi)
                    cursor.execute('''UPDATE "main"."Bookmark" SET "Hidden" = "true" WHERE  "BookmarkID" = ?''',
                                   (bookmarks[hi][0],))
                    print('Highlight number {} deleted (technically, hidden).'.format(hi))
                    print('\n Content of deleted (hidden) highlight: {}'.format(content))
            
            # Do not delete!
            print('Commiting changes to the DB...')
            db.commit()
            print('Closing connection to DB...')
            db.close()
            return

        if show_all:
            mark_num = 0
            for mark in bookmarks:
                print('\n Highlight number: {} \n {} \n\n {} \n'.format(mark_num, mark[1], mark[2]))
                mark_num += 1
            return

        if reverse:
            bookmarks.reverse()

        if random:
            shuffle(bookmarks)

        count = 0
        bookmarks_length = len(bookmarks)

        if half:
            count = int(bookmarks_length / 2)

        if custom_start:
            count = custom_start

        while count < bookmarks_length:
            print('\n Highlight number {} \n'.format(count))
            print(bookmarks[count][1], '\n\n', bookmarks[count][2], '\n')
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
        :param: output_dir: Where you want your backup file to go. Default is ./Backups/
        :return: None
        """

        if not output_dir:
            output_dir = BASE_DIR + '/Backups/'

        now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
        file_name = output_dir + 'KoboDB_backup-{}'.format(now)

        print('Backing up your Kobo DB to the following location:\n{}.zip...'.format(file_name))
        zf = zipfile.ZipFile("{}.zip".format(file_name), "w", zipfile.ZIP_DEFLATED)
        zf.write(BASE_DIR + '/' + 'KoboReader.sqlite', 'Backups/KoboReader.sqlite')
        zf.close()
        print('Finished backing up your Kobo DB.')

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
                copy2(KOBO_READER, BASE_DIR + '/KoboReader.sqlite')
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
            highlights half - Get highlights from the halfway point (can be combined with reverse)
            highlights all - Show all highlights in your DB
            highlights [number] - Start from highlight number N (must be LAST command)

            highlights delete [number] - Delete (hide) highlight number N

            get - Pull the KoboReader.sqlite DB file from your connected reader
            push - Send the local KoboReader.sqlite DB file to your connected reader
            backup - Create a compressed backup of your DB file in the "Backup" directory
            help - Show this screen again

            Environment variables:

            $KOBO_DB - The file you want to use for the 'highlights' series of commands
            Default: {KOBO_DB}

            $KOBO_READER - The path to your Kobo reader's SQLite file once plugged in via USB
            Default: {KOBO_READER}
            """.format(KOBO_DB=KOBO_DB, KOBO_READER=KOBO_READER)
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
                copy2(BASE_DIR + '/KoboReader.sqlite', KOBO_READER)
                print('Done copying SQLite file to your Kobo.')
            except FileNotFoundError:
                print('Your Kobo does not appear to be connected. Please plug your Kobo in and try again.')
        else:
            return


if __name__ == '__main__':

    try:
        start = time.perf_counter()

        behavior_arg = argv[1].lower()

        operations = {
            'highlights': KoboDB.get_highlights,
            'get': KoboDB.get_db,
            'push': KoboDB.push_db,
            'backup': KoboDB.backup_db,
            'help': KoboDB.help,
        }

        try:
            if type(int(argv[-1])) == int:
                custom_start_num = int(argv[-1])
            else:
                custom_start_num = False
        except ValueError:
            custom_start_num = False

        delete_num = False

        if behavior_arg == 'highlights':

            try:
                if argv[2] == 'delete':
                    delete_num = True
                else:
                    try:
                        if type(int(argv[-1])) == int and 'delete' in argv:
                            delete_num = int(argv[-1])
                    except ValueError:
                        pass
            except IndexError:
                pass

            sqlite_file = KOBO_DB

            reverse = True if len(argv) > 2 and 'reverse' in argv else False
            random = True if len(argv) > 2 and 'random' in argv else False
            show_all = True if len(argv) > 2 and argv[2] == 'all' else False
            grouped = True if len(argv) > 2 and 'group' in argv else False
            half = True if len(argv) > 2 and 'half' in argv else False
            custom_start = custom_start_num
            delete = delete_num

            operations[behavior_arg](sqlite_file,
                                     reverse=reverse,
                                     random=random,
                                     show_all=show_all,
                                     grouped=grouped,
                                     half=half,
                                     custom_start=custom_start,
                                     delete=delete_num)
        else:
            operations[behavior_arg]()

        end = time.perf_counter()

        if 'debug' in argv:
            print('Execution time: {}'.format(end - start))

    except (KeyError) as e:
        KoboDB.help()
        print('Error: {}'.format(e))
