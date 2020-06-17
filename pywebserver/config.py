class Configuration:
    filestructure = {
            "/": "./www/index.html",
            "/app": "./www/helloworld.py",
            404: "./www/404.html",
            None: "./www/"
            }

    security = {
            "PathTraversal": True # redirects the user to / if .. is found in the requested path
            }

    access = {
            "PreDefAlternateFile": False # redirects the user to the directory specified in None in case of 404
            }

    parsing = {
            "Python": True,   # Allow execution of Python apps
            "Oxidian": False, # Allow execution of Oxidian apps
            "App": False      # Allow execution of sh scripts or other executables
            }
