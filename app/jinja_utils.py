
from app import app

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))
        return ""

    return dict(print=print_in_console)
