# File: run.py

from remoteui import SimpleCameraApp

if __name__ == "__main__":
    # Pas hier de grootte eventueel aan
    app = SimpleCameraApp(width=800, height=480)
    app.run()
