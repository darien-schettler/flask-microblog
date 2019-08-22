# A Flask Application to Learn More About Flask and Back-End Web Development

A small social-network application with the following functionality
  - Elasticsearch
  - AJAX Translate through Azure Text Translate API
  - User Notifications
  - Following/Followed
  - Posts
  - Timestamps
  - Profiles
  - Avatars
  - Register/Login/Forgot-Your-Password etc (including smtp server setup)
  - Home Timeline (Following and Self)
  - Explore Timeline (All)
  - Profile Timeline (Self)
  - Hover Popup (JS)
  - Much more...

## Getting Started

```
1. Clone this repository
2. Create an environment (and activate it) and install the requirements.txt file
3. Ensure sqlite is installed as well as any other dependencies
4. in your command prompt launch the app
5. Enjoy
```


## Prerequisites

```
TBD
```

## Installation
**NOTE: all shell commands are via the windows command line... you can find alternatives for linux fairly easily**

1. Clone this repository and navigate into it within the command line

2. Create and activate an environment<br>
` python -m venv env `<br>
` env\scripts\activate `<br>
` python -m pip install --upgrade pip `<br>

3. Execute the following commands to install all the requiremets<br>
` pip install -r requirements.txt`<br>

4. Adhere to the following folder structure<br>
```
flask-microblog
|---- requirements.txt
|
|---- .flaskenv
|---- config.py
|---- .gitignore
|---- microblog.py
|---- tests.py
|
|------ app
|\
| \
|  \
|   |---- __init__.py
|   |---- email.py
|   |---- forms.py
|   |---- models.py
|   |---- routes.py
|   |---- translate.py
|   |
|   |------ auth
|   |\
|   | \
|   |  |---- __init__.py
|   |  |---- email.py
|   |  |---- forms.py
|   |  |---- routes.py
|   | /
|   |
|   |------ errors
|   |\
|   | \
|   |  |---- __init__.py
|   |  |---- handlers.py
|   | /
|   |
|   |------ main
|   |\
|   | \
|   |  |---- __init__.py
|   |  |---- forms.py
|   |  |---- routes.py
|   | /
|    /
|   |
|   |------ static
|   |\
|   | \
|   |  |---- css <folder>
|   |  |---- loading.gif
|   | /
|    /
|   |
|   |------ templates
|   |\
|   | \
|   |  |---- auth <folder>
|   |  |---- email <folder>
|   |  |---- errors <folder>
|   |  |---- _post.html
|   |  |---- base.html
|   |  |---- edit_profile.html
|   |  |---- index.html
|   |  |---- user.html
|   | /
|    /
|  /
| /
|/
|
|------ archive
|\
| \
|  \
|   |---- __init__.py
|   |---- email.py
|   |---- forms.py
|   |---- models.py
|   |---- routes.py
|   |---- translate.py
|   |
|   |
|  /
| /
|/
|
|
|------ logs
|\
| \
|  \
|   |---- <logfile>
|   |---- <logfile>
|   |---- ...etc...
|  /
| /
|/
|
|------ migrations
|\
| \
|  \
|   |---- README
|   |---- alembic.ini
|   |---- env.py
|   |---- script.py.mako
|   |
|   |------ versions
|   |\
|   | \
|   |  |---- 02c3de5a934d_users_table.py
|   |  |---- 4a84fd416eda_add_language_to_posts.py
|   |  |---- c8a885bf2dff_followers.py
|   |  |---- ce73075bc40f_posts_table.py
|   |  |---- ceb11b56f48e_new_fields_in_user_model.py
|   | /
|   |
|---- README.md
|---- LICENSE.md
|---- CONTRIBUTING.md
```

5. Navigate to the cloned directory and use the following command
```
flask run
```

## Deployment

To deploy this on a system ... TBD (docker... or something)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## Authors

**Darien Schettler** -- [Portfolio](http://darienschettler.ca/) -- [Github](https://github.com/darien-schettler)


## Licensing

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
