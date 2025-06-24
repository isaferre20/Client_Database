from client_data_backend import db, app

with app.app_context():
    db.create_all()
    print("✅ Database has been created successfully!")

