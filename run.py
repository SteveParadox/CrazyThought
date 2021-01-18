from flaskblog import create_app, io, db

app = create_app()
app.app_context().push()

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
else:
    app.debug = False
    threaded = True


if __name__ == '__main__':
    io.run(app, debug=True, port=5000)
    #db.drop_all(app=create_app())
    #db.create_all(app=create_app())