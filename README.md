DjaoDjin answers
================

The Django app implements a simple questions/answers forum where questions
can be followed and upvoted.


Five minutes evaluation
=======================

The source code is bundled with a sample django project.

    $ virtualenv *virtual_env_dir*
    $ cd *virtual_env_dir*
    $ source bin/activate
    $ git clone https://github.com/djaodjin/djaodjin-answers.git
    $ pip install -r requirements.txt

    $ cd testsite
    $ python manage.py syncdb
    $ python manage.py runserver

    # Visit url at http://localhost:8000/

