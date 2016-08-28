# Kobo Utilities
---

Being an avid reader and user of Anki, I've historically struggled to come up with a way to take text I want to remember from books and turn them into flashcards.
With physical books, I had exactly one option: type out the text on my computer. This didn't sit well with me at all, so several years ago I became a devout user of e-books.
E-books give me the ability to copy and paste text directly on my computer, transport lots of books all at once and are generally excellent for anyone who cares about maintaining
and organizing a large library. Unfortunately, most e-readers have only a very basic ability to highlight text and store it on the device. It wasn't until I bought a Kobo
e-reader that I found my solution. These devices hold data (including highlights) on a SQLite database that is easily accessible.

Since buying my Kobo, I've been using a simple SQLite extension in Firefox, but it came up short in some key areas (namely in my ability to quickly and easily remove highlights I don't need anymore).
My solution is this program (which may or may not transform into a set of programs). It looks at a Kobo database, collects all the highlights into a list and then presents them to the user,
along with a choice: do you want to keep this highlight? If you don't, you type 'n' and it will switch the "Hidden" field to "true" - meaning it will no longer show up on the reader, but it will still be there
for future reference. And, because of the query used to gather the data, it won't show up again in the execution of this program.

All you need to do to run the program is the place KoboReader.sqlite file that can be found on a Kobo reader within the .kobo directory into the same directory as the script. You can run the file within any arguments,
which will present highlights from first to last. Or, you can add 'reverse' or 'random' to have last-first ordering or random ordering, respectively.
 
