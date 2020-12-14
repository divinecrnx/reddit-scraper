RedditScraper
=============

Saved too many posts? Are they images that you saved and want to download for personal use but couldn't be bothered? (Wallpapers, avatars). 
Then look no further! This program scrapes your profile, unsaves said posts (keeping your profile clean), and downloads them to subreddit 
specific folders ready to be viewed at your leisure. It even does posts, albeit to a simpler degree as in it simply scrapes a post's content 
and writes it to a txt file. I made this because my saves were getting cluttered with image posts and I wanted to navigate it better and also because 
I was bored. Special thanks to PRAW for doing the heavy work!

.. _installation:

Installation
------------

Before using, you need to install all the required python packages like so:

.. code-block:: bash

   pip install -r requirements.txt

Usage
-----

Before you can use the program, you need to have a reddit account and a reddit `developer application <https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps/>`_. 
You also need to specify a user agent. Reddit prefers it to be like this: ``ChangeMeClient/0.1 by YourUsername``. 
Finally, uncomment the first line of the praw.ini file so that it looks something like this:

.. code-block:: ini

    [RS]
    client_id=id
    client_secret=secret
    password=1234
    username=Joe
    user_agent=ChangeMeClient/0.1 by YourUsername

Then, you need to specify in ``subreddits.txt`` what subreddits you want to scrape. Each subreddit needs to be on its own line, and it doesn't matter 
what order you put them in, the program sorts it alphabetically later. You can then run the program in a terminal like so:

.. code-block:: bash

    python main.py None

If you want a limit to how many posts it scrapes, you can replace ``None`` with an integer. You can also add -sort afterwards if your downloaded 
content has incorrect indexes and you want it fixed.