Simple PyQt4 app to tell you how many days until your AD/LDAP password needs to be reset.

It will create a config file in ~/pyADExpiry.ini by default.

Edit the file and change `full_name` to your display name in the AD/LDAP system.

You may also like to change the `edir_uri` option if you are using a dirrent endpoint.

Then just start pyADExpiry.py and it will check for expiration every 24 hours and pop up an alert whenever your password is 14 days or less from expiration.

![Screenshot](screenshot.png?raw=true "Screenshot")

That's all folks.
