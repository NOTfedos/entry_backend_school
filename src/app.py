import uvicorn
from setup import init_app

app = init_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, debug=True)
