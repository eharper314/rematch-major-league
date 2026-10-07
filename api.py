# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date
from dbconn import get_connection
from psycopg.errors import CheckViolation, DatabaseError, ForeignKeyViolation, UniqueViolation

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

class League(BaseModel):
    league_name: str = Field(min_length = 1, max_length = 100)

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
    except DatabaseError as e:
        print("DATABASE ERROR:", e)
        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while creating the season."
        )

# ------------------------------------------
# Endpoint to view the list of 
# seasons in RML.
# ------------------------------------------

@app.get("/season")
def list_seasons():

    # ------------------------------------------
    # Pulls all seasons in the database
    # ------------------------------------------

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    season_id,
                    season_name,
                    start_date,
                    end_date,
                    free_agent_start,
                    free_agent_end
                FROM seasons
                ORDER BY start_date ASC;
                """
            )

            rows = cur.fetchall()

    return [
        {
            "season_id": row[0],
            "season_name": row[1],
            "start_date": row[2],
            "end_date": row[3],
            "free_agent_start": row[4],
            "free_agent_end": row[5]
        }
        for row in rows
    ]

# ------------------------------------------
# Endpoint to get a specific season in RML.
# ------------------------------------------

@app.get("/season/{season_id}")
def get_season(season_id: int):

    # ------------------------------------------
    # Pulls one specific season from the 
    # database.
    # ------------------------------------------

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    season_id,
                    season_name,
                    start_date,
                    end_date,
                    free_agent_start,
                    free_agent_end
                FROM seasons
                WHERE season_id = %s;
                """,
                (season_id,)
            )

            row = cur.fetchone()

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail = "Season not found."
        )

    return {
        "season_id": row[0],
        "season_name": row[1],
        "start_date": row[2],
        "end_date": row[3],
        "free_agent_start": row[4],
        "free_agent_end": row[5]      
    }

# ------------------------------------------
# Endpoint to update a season in RML.
# ------------------------------------------

@app.patch("/season/{season_id}")
def update_season(season_id: int, season: Season):

    # ------------------------------------------
    # Attempts to update a season in the 
    # database.
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE seasons
                    SET
                        season_name = %s,
                        start_date = %s,
                        end_date = %s,
                        free_agent_start = %s,
                        free_agent_end = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE season_id = %s
                    RETURNING season_id;                    
                    """,
                    (
                    season.season_name,
                    season.start_date,
                    season.end_date,
                    season.free_agent_start,
                    season.free_agent_end,
                    season_id
                    )  
                )
                updated_season = cur.fetchone()

                # ------------------------------------------
                # If the requested season doesn't exist,
                # then this pops.
                # ------------------------------------------

                if updated_season is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = "Season not found."
                    )

        return {
            "message": "Season has been updated successfully!"
        }
              
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
    except DatabaseError as e:
        print("DATABASE ERROR:", e)
        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while updating the season."
        )

# ------------------------------------------
# Endpoint to create a league in RML.
# ------------------------------------------

@app.post("/season/{season_id}/league")
def create_league(season_id: int, league: League):

    # ------------------------------------------
    # Attempts to create a league
    # ------------------------------------------
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO leagues (
                        season_id,
                        league_name
                    )
                    VALUES (%s, %s)
                    RETURNING league_id;
                    """,
                    (
                        season_id,
                        league.league_name
                    )
                )

                league_id = cur.fetchone()[0]

        return {
            "message": "League has been created successfully!",
            "league_id": league_id
        }

    # ------------------------------------------
    # Pops if the season_id isn't found
    # ------------------------------------------

    except ForeignKeyViolation:
        raise HTTPException(
            status_code = 404,
            detail = "The specified season does not exist."
        )

    # ------------------------------------------
    # Pops if you try to create a league
    # with the same name within the same season.
    # ------------------------------------------

    except UniqueViolation:
        raise HTTPException(
            status_code = 409,
            detail = "A league with that name already exists in this season."
        )

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while creating the league."
        )



