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
    app.run(host="0.0.0.0", port=5000)
    #app.run(ssl_context=(r'C:\Users\USER\Desktop\CrazyThought\certs\certificate.pem', r'C:\Users\USER\Desktop\CrazyThought\certs\private_key.pem'))    
    #with app.app_context():
        #db.drop_all()
        #db.create_all()
        
        

 