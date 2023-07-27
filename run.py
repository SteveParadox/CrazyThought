from flaskblog import create_app, db, io
from flaskblog.tasks import data_task


app, celery = create_app()
app.app_context().push()

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
else:
    app.debug = False
    threaded = True


if __name__ == '__main__':
    #data_task.delay()
    io.run(app, port=5000, debug=True)
    #with app.app_context():
        #db.drop_all()
        #db.create_all()
        
        

 