This program uses the Gmail API to bulk delete emails with a
specific label.

This is meant to workaround a long standing bug in Gmail that makes it
impossible to delete very large number of messages at one shot. This
bug also applies to many other bulk operations, but it is the delete
that affected me personally.

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

4. Open main.py and edit the label name, and NUM_LOOPS constants to match your requirements.

5. Also recommended is to look at the other inspection code (commented
out by default) to first dry run the program before you start deleting
stuff from your gmail.