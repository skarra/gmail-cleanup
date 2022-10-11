This program uses the Gmail API to bulk delete emails with a
specific label.

I wrote this program to workaround a long standing bug in Gmail that
makes it impossible to delete very large number of messages through a
bulk UI operation. This bug also affects many other bulk operations,
but it is the delete that affected me personally as I was running out
of quota and found myself unable to delete messages I no longer cared
about.

This is intended for personal use and offered without any sort of
warranty, under the very permissive "Do Whatever the Hell You Want
With It" license.


Installation
===

1. You will need to set up your local environment for using the Gmail API.

  - For basic instructions on getting started, including pointers on how you
    can create a GCP project etc, start here:
    https://developers.google.com/gmail/api/quickstart/python

    Some instructions specific to this project:

    - Recommended to set up a separate python3 virtuanenv, because why not.
    - The GCP project can be set up as a desktop app and download the client_id credentials as a json file.
    - The app requires a very powerful and sensitive scope - https://mail.google.com - you to avoid having to go through an app verification process, you can set up the project as "Testing" project, and add specific test accounts that you want to work with.

2. Clone this repo

3. Move the credentials file to the cloned repo, and call it 'credentials.json'

4. Do a dry run to see how many mssages of your label will get nuked,
and then invoke the command to actually nuke them.

5. I would recommended is to look at the other inspection code (commented
out by default) to first dry run the program before you start deleting
stuff from your gmail.

Sample Usage
===

A successful run looks something like this:

```
$ python main.py -h

usage: main.py [-h] [--op {dry-run,delete-all,delete-ten,print-label-names}]
               [--label-name LABEL_NAME]

optional arguments:
  -h, --help            show this help message and exit
  --op {dry-run,delete-all,delete-ten,print-label-names}
                        What to do. Default to 'dry-run'
  --label-name LABEL_NAME
                        specify name of label to operate on

$ python main.py --op delete-all --label-name 'Lists/Linux/Kernel'
Processing label name:  Lists/Linux Kernel ; ID:  Label_76
Iteration 0...
  Total Messages: 379966; Total Threads: 168425
  Batch deleting 500 messages...

Iteration 1...
  Total Messages: 379466; Total Threads: 168175
  Batch deleting 500 messages...

Iteration 2...
  Total Messages: 378966; Total Threads: 167917
  Batch deleting 500 messages...

Iteration 3...
  Total Messages: 378466; Total Threads: 167717
  Batch deleting 500 messages...

Iteration 4...
  Total Messages: 377966; Total Threads: 167501
  Batch deleting 500 messages...

Iteration 5...
  Total Messages: 377466; Total Threads: 167273
  Batch deleting 500 messages...

Iteration 6...
  Total Messages: 376966; Total Threads: 167052
  Batch deleting 500 messages...

Iteration 7...
  Total Messages: 376466; Total Threads: 166882
  Batch deleting 500 messages...

Iteration 8...
  Total Messages: 375966; Total Threads: 166675
  Batch deleting 500 messages...
```

The number of iterations and number of messages per iteration are
configurable within limits. The proram will terminate if no messages
are left to be deleted.