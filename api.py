# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from dbconn import get_connection
from psycopg.errors import CheckViolation, DatabaseError

# ------------------------------------------
# To run the API locally, run this command:
# uvicorn api:app --reload
# ------------------------------------------

# ------------------------------------------
# Global Variables
# ------------------------------------------

app = FastAPI()


# ------------------------------------------
# Global Classes
# ------------------------------------------

class Season(BaseModel):
    season_name: str
    start_date: date
    end_date: date
    free_agent_start: date | None = None
    free_agent_end: date | None = None


# ------------------------------------------
# Starting endpoint for health check
# ------------------------------------------
@app.get("/")
def root():
    return {"message": "RML API is up and running"}

# ------------------------------------------
# Endpoint to create a season in RML
# ------------------------------------------
@app.post("/season")
def create_season(season: Season):

    # ------------------------------------------
    # Attempt to create the season, the 
    # database already has built in checks.
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO seasons (
                    season_name,
                    start_date,
                    end_date,
                    free_agent_start,
                    free_agent_end
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING season_id;
                    """,
                    (
                        season.season_name,
                        season.start_date,
                        season.end_date,
                        season.free_agent_start,
                        season.free_agent_end
                    )
                )
                season_id = cur.fetchone()[0]

        return {
            "message": "Season has been created successfully!",
            "Season ID: ": season_id
        }
    
    # ------------------------------------------
    # Exceptions if a built in check gets
    # raised from the database.
    # ------------------------------------------

    except CheckViolation as e:
        constraint = e.diag.constraint_name

        messages = {
            "valid_season_dates":
                "Season end date must be on or after the season start date.",
            "valid_free_agent_dates":
                "Free agent end date must be on or after the free agent start date.",
            "free_agent_after_season_start":
                "Free agent period cannot begin before the season starts.",
            "free_agent_before_season_end":
                "Free agent period cannot end after the season ends."
        }

    # ------------------------------------------
    # If something goes wrong with the
    # check-specific rules, this message pops.
    # ------------------------------------------

        raise HTTPException(
            status_code = 400,
            detail = messages.get(
                constraint, 
                "Season violates a database rule."
                )
        )

    # ------------------------------------------
    # If the database fails for some unknown 
    # reason, then this error raises.
    # ------------------------------------------
    except DatabaseError:
        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while creating the season."
        )



