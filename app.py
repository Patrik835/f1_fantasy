from flask_app import create_app

# Create the Flask app using the factory so CLI and WSGI servers get a ready app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
