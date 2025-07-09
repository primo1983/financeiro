from app import create_app

app = create_app()

if __name__ == '__main__':
    # Usando debug=True para nos ajudar caso surja outro problema.
    app.run(debug=True)