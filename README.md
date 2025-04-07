# anesthesia-whiteboard

This is a Python Django project.

To get started:

1. Clone the repo: `git clone git@github.com:keatonhoyle/anesthesia-whiteboard.git`
2. Make a virtual environment `python -m venv .venv`
3. Activate it. Probably something like `source .venv/bin/activate` but depends on the operating system
4. Go into the folder `cd anesthesia-whiteboard`
5. Install all the stuff. `pip install -r requirements.txt`
6. I had to make migrations. Ideally they're stored in the repo, though.  `python manage.py makemigrations`
7. Don't remember why but I think I did this `python manage.py migrate`
8. If you need a super user because there isn't one, `python manage.py createsuperuser`
9. Run it. `python manage.py runserver`

## Prompt generator
I got ChatGPT to update my Godot prompt generator script for your Django project. Here's how I use it:

1. Modify the `new_feature` variable in the script. 
2. Execute the script. `python3 prompt-manager.py > prompt.txt`
3. Open prompt.txt, review it quickly to make sure you aren't going to copy/paste anything you shouldn't to Grok/Claude/ChatGPT. Paste it, and follow the instructions.
