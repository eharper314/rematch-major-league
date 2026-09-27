# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

from fastapi import FastAPI


# ------------------------------------------
# To run the API locally, run this command:
# uvicorn api:app --reload
# ------------------------------------------

# ------------------------------------------
# Global Variables
# ------------------------------------------

app = FastAPI()

# ------------------------------------------
# Starting endpoint for health check
# ------------------------------------------
@app.get('/')
def root():
    return {'message': 'RML API is up and running'}