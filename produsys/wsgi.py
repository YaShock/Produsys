from produsys import create_app

app = create_app('Prod')

if __name__ == '__main__':
    app.run()
