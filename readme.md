
# nkwo

a simple wip for a forum application in python.

features:

- sqlite database, interacted with an orm
- python backend
- basic https security? maybe?
- terribly hand written ui in plain html + css


## running

install dependencies using

```bash
pip install -r requirements.txt
```

create a copy of the `instanceconfigtemplate.py` file in the `instance` folder, rename it to `config.py`. fill out `SECRET_KEY` with a sufficiently random key, and fill out `SQLALCHEMY_DATABASE_URI` with a uri to the location of your database (I recommend keeping it in the same directory as the repo for simplicity)

initialize a database with

```bash
flask db init
flask db migrate
flask db upgrade
```

(make sure to run those last two commands after pulling)

then finally run with

```bash
python main.py
```


