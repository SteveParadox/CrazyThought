from flaskblog import create_app, db, io
from flask_sslify import SSLify


app, celery = create_app()
app.app_context().push()

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
else:
    app.debug = False
    threaded = True


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        #db.drop_all()
    app.run(host="0.0.0.0", port=5000)
        
        

 