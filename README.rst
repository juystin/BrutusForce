BRUTUS-FORCE
===============

This is a Python program utilizing ``requests`` and ``Selenium``
libraries to scrape building, classroom and class data from
The Ohio State University's `building index <https://content.osu.edu/v2/classes/>`_
and `class API <https://content.osu.edu/v2/classes/>`_. The data
is written into a local SQL database using ``sqlite3``.

All credits to finding the class API and documentation on its usage
belongs to `xanarin <https://github.com/xanarin/OSU-API-Documentation>`_.

The building, classroom and class data are all collected from
the Columbus campus.

---------------

To properly run the script, be sure to download `chromedriver <https://chromedriver.chromium.org/downloads>`_
and place in `sample/helpers`.