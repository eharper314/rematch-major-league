# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date, datetime
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

class Player(BaseModel):
    discord_user_id: int
    ign: str = Field(min_length = 1, max_length = 32)

class PlayerIgnUpdate(BaseModel):
    ign: str = Field(min_length = 1, max_length = 32)

class PlayerWarning(BaseModel):
    warning_type: str = Field(min_length = 1, max_length = 100)
    reason: str = Field(min_length = 1)
    expires_at: datetime | None = None

class PlayerBan(BaseModel):
    reason: str = Field(min_length = 1)
    expires_at: datetime | None = None

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

            season = cur.fetchone()

            if season is None:
                raise HTTPException(
                    status_code = 404,
                    detail = "Season not found."
                )

            cur.execute(
                """
                SELECT
                    league_id,
                    league_name
                FROM leagues
                WHERE season_id = %s
                ORDER BY league_id;
                """,
                (season_id,)
            )

            leagues = cur.fetchall()

    return {
        "season_id": season[0],
        "season_name": season[1],
        "start_date": season[2],
        "end_date": season[3],
        "free_agent_start": season[4],
        "free_agent_end": season[5],
        "leagues": [
            {
                "league_id": league[0],
                "league_name": league[1]
            }
            for league in leagues
        ]
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

@app.post("/season/{season_id}/leagues")
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

# ------------------------------------------
# Endpoint to update a league in RML.
# ------------------------------------------

@app.patch("/league/{league_id}")
def update_league(league_id: int, league: League):

    # ------------------------------------------
    # Attempts to update a league
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE leagues
                    SET
                        league_name = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE league_id = %s
                    RETURNING league_id;
                    """,
                    (
                        league.league_name,
                        league_id
                    )
                )

                updated_league = cur.fetchone()


                # ------------------------------------------
                # Pops if the league ID isn't found
                # ------------------------------------------

                if updated_league is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = "That specified league does not exist."
                    )
        return {
            "message": "League has been updated successfully.",
            "league_id": updated_league[0]
        }

    # ------------------------------------------
    # Pops if you try to update a league
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

# ------------------------------------------
# Endpoint to register a player in RML.
# ------------------------------------------

@app.post("/players")
def create_player(player: Player):

    # ------------------------------------------
    # Attempts to register the player
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO players (
                        discord_user_id,
                        ign
                    )
                    VALUES (%s, %s)
                    RETURNING player_id;
                    """,
                    (
                        player.discord_user_id,
                        player.ign
                    )
                )

                player_id = cur.fetchone()[0]

        return {
            "message": "Player has been registered successfully!",
            "player_id": player_id
        }

    # ------------------------------------------
    # Pops if the Discord account is already
    # registered in RML.
    # ------------------------------------------

    except UniqueViolation:
        raise HTTPException(
            status_code = 409,
            detail = "That Discord user is already registered in RML."
        )

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while registering the player."
        )


# ------------------------------------------
# Endpoint to get a player using their
# Discord user ID.
# ------------------------------------------

@app.get("/players/discord/{discord_user_id}")
def get_player_by_discord(discord_user_id: int):

    # ------------------------------------------
    # Attempts to find the player
    # ------------------------------------------

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    player_id,
                    discord_user_id,
                    ign,
                    registered_at,
                    ign_updated_at
                FROM players
                WHERE discord_user_id = %s;
                """,
                (
                    discord_user_id,
                )
            )

            player = cur.fetchone()

    # ------------------------------------------
    # Pops if the player isn't registered
    # ------------------------------------------

    if player is None:
        raise HTTPException(
            status_code = 404,
            detail = "Player not found."
        )

    # ------------------------------------------
    # Returns the player's information
    # ------------------------------------------

    return {
        "player_id": player[0],
        "discord_user_id": player[1],
        "ign": player[2],
        "registered_at": player[3],
        "ign_updated_at": player[4]
    }


# ------------------------------------------
# Endpoint for a player to update their IGN.
# ------------------------------------------

@app.patch("/players/{player_id}/ign")
def update_player_ign(
    player_id: int,
    player: PlayerIgnUpdate
):

    # ------------------------------------------
    # Attempts to update the player's IGN
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                # ------------------------------------------
                # Gets the player's current IGN update
                # information.
                # ------------------------------------------

                cur.execute(
                    """
                    SELECT
                        player_id,
                        ign_updated_at,
                        (
                            ign_updated_at IS NULL
                            OR ign_updated_at <= CURRENT_TIMESTAMP - INTERVAL '7 days'
                        ) AS can_update
                    FROM players
                    WHERE player_id = %s;
                    """,
                    (
                        player_id,
                    )
                )

                current_player = cur.fetchone()

                # ------------------------------------------
                # Pops if the player ID isn't found
                # ------------------------------------------

                if current_player is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = "That specified player does not exist."
                    )

                # ------------------------------------------
                # Checks to see if the player is still
                # within the IGN update cooldown.
                # ------------------------------------------

                if not current_player[2]:
                    raise HTTPException(
                        status_code = 429,
                        detail = (
                            "You can only update your IGN once every 7 days."
                        )
                    )

                # ------------------------------------------
                # Updates the player's IGN
                # ------------------------------------------

                cur.execute(
                    """
                    UPDATE players
                    SET
                        ign = %s,
                        ign_updated_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE player_id = %s
                    RETURNING player_id;
                    """,
                    (
                        player.ign,
                        player_id
                    )
                )

                updated_player = cur.fetchone()

        return {
            "message": "Player IGN has been updated successfully!",
            "player_id": updated_player[0]
        }

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while updating the player's IGN."
        )

# ------------------------------------------
# Endpoint for staff to update a player's IGN.
# ------------------------------------------

@app.patch("/staff/players/{player_id}/ign")
def staff_update_player_ign(
    player_id: int,
    player: PlayerIgnUpdate
):

    # ------------------------------------------
    # Attempts to update the player's IGN
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE players
                    SET
                        ign = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE player_id = %s
                    RETURNING player_id;
                    """,
                    (
                        player.ign,
                        player_id
                    )
                )

                updated_player = cur.fetchone()

                # ------------------------------------------
                # Pops if the player ID isn't found
                # ------------------------------------------

                if updated_player is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = "That specified player does not exist."
                    )

        return {
            "message": "Player IGN has been updated successfully!",
            "player_id": updated_player[0]
        }

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while updating the player's IGN."
        )

# ------------------------------------------
# Endpoint to give a player a warning.
# ------------------------------------------

@app.post("/players/{player_id}/warnings")
def create_player_warning(
    player_id: int,
    warning: PlayerWarning
):

    # ------------------------------------------
    # Attempts to give the player a warning
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                # ------------------------------------------
                # Checks to see if the player exists
                # ------------------------------------------

                cur.execute(
                    """
                    SELECT player_id
                    FROM players
                    WHERE player_id = %s;
                    """,
                    (
                        player_id,
                    )
                )

                player = cur.fetchone()

                if player is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = "That specified player does not exist."
                    )

                # ------------------------------------------
                # Creates the warning
                # ------------------------------------------

                cur.execute(
                    """
                    INSERT INTO player_warnings (
                        player_id,
                        warning_type,
                        reason,
                        expires_at
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING warning_id;
                    """,
                    (
                        player_id,
                        warning.warning_type,
                        warning.reason,
                        warning.expires_at
                    )
                )

                warning_id = cur.fetchone()[0]

        return {
            "message": "Player warning has been created successfully!",
            "warning_id": warning_id
        }

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while warning the player."
        )


# ------------------------------------------
# Endpoint to get a player's active warnings.
# ------------------------------------------

@app.get("/players/{player_id}/warnings")
def get_player_warnings(player_id: int):

    with get_connection() as conn:
        with conn.cursor() as cur:

            # ------------------------------------------
            # Checks to see if the player exists
            # ------------------------------------------

            cur.execute(
                """
                SELECT player_id
                FROM players
                WHERE player_id = %s;
                """,
                (
                    player_id,
                )
            )

            player = cur.fetchone()

            if player is None:
                raise HTTPException(
                    status_code = 404,
                    detail = "That specified player does not exist."
                )

            # ------------------------------------------
            # Gets the lifetime warning amount
            # ------------------------------------------

            cur.execute(
                """
                SELECT COUNT(*)
                FROM player_warnings
                WHERE player_id = %s;
                """,
                (
                    player_id,
                )
            )

            warning_amount = cur.fetchone()[0]

            # ------------------------------------------
            # Gets all current warnings
            # ------------------------------------------

            cur.execute(
                """
                SELECT
                    warning_id,
                    warning_type,
                    reason,
                    issued_at,
                    expires_at
                FROM player_warnings
                WHERE player_id = %s
                AND removed_at IS NULL
                AND (
                    expires_at IS NULL
                    OR expires_at > CURRENT_TIMESTAMP
                )
                ORDER BY issued_at DESC;
                """,
                (
                    player_id,
                )
            )

            warnings = cur.fetchall()

    return {
        "player_id": player_id,
        "warning_amount": warning_amount,
        "current_warnings": len(warnings),
        "warnings": [
            {
                "warning_id": warning[0],
                "warning_type": warning[1],
                "reason": warning[2],
                "issued_at": warning[3],
                "expires_at": warning[4]
            }
            for warning in warnings
        ]
    }

# ------------------------------------------
# Endpoint to remove a player's warning.
# ------------------------------------------

@app.patch("/warnings/{warning_id}/remove")
def remove_player_warning(warning_id: int):

    # ------------------------------------------
    # Attempts to remove the warning
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE player_warnings
                    SET
                        removed_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE warning_id = %s
                    AND removed_at IS NULL
                    RETURNING warning_id;
                    """,
                    (
                        warning_id,
                    )
                )

                removed_warning = cur.fetchone()

                # ------------------------------------------
                # Pops if the warning ID isn't found
                # ------------------------------------------

                if removed_warning is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = (
                            "That warning does not exist or has "
                            "already been removed."
                        )
                    )

        return {
            "message": "Player warning has been removed successfully!",
            "warning_id": removed_warning[0]
        }

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while removing the warning."
        )

# ------------------------------------------
# Endpoint to ban a player in RML.
# ------------------------------------------

@app.post("/players/{player_id}/bans")
def create_player_ban(
    player_id: int,
    ban: PlayerBan
):

    # ------------------------------------------
    # Attempts to ban the player
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                # ------------------------------------------
                # Checks to see if the player exists
                # ------------------------------------------

                cur.execute(
                    """
                    SELECT player_id
                    FROM players
                    WHERE player_id = %s;
                    """,
                    (
                        player_id,
                    )
                )

                player = cur.fetchone()

                if player is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = "That specified player does not exist."
                    )

                # ------------------------------------------
                # Checks to see if the player is already
                # actively banned.
                # ------------------------------------------

                cur.execute(
                    """
                    SELECT ban_id
                    FROM player_bans
                    WHERE player_id = %s
                    AND lifted_at IS NULL
                    AND (
                        expires_at IS NULL
                        OR expires_at > CURRENT_TIMESTAMP
                    )
                    LIMIT 1;
                    """,
                    (
                        player_id,
                    )
                )

                active_ban = cur.fetchone()

                if active_ban is not None:
                    raise HTTPException(
                        status_code = 409,
                        detail = "That player is already actively banned."
                    )

                # ------------------------------------------
                # Creates the ban
                # ------------------------------------------

                cur.execute(
                    """
                    INSERT INTO player_bans (
                        player_id,
                        reason,
                        expires_at
                    )
                    VALUES (%s, %s, %s)
                    RETURNING ban_id;
                    """,
                    (
                        player_id,
                        ban.reason,
                        ban.expires_at
                    )
                )

                ban_id = cur.fetchone()[0]

        return {
            "message": "Player has been banned successfully!",
            "ban_id": ban_id
        }

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while banning the player."
        )


# ------------------------------------------
# Endpoint to get a player's active bans.
# ------------------------------------------

@app.get("/players/{player_id}/bans")
def get_player_bans(player_id: int):

    # ------------------------------------------
    # Pulls the player's active bans
    # ------------------------------------------

    with get_connection() as conn:
        with conn.cursor() as cur:

            # ------------------------------------------
            # Checks to see if the player exists
            # ------------------------------------------

            cur.execute(
                """
                SELECT player_id
                FROM players
                WHERE player_id = %s;
                """,
                (
                    player_id,
                )
            )

            player = cur.fetchone()

            if player is None:
                raise HTTPException(
                    status_code = 404,
                    detail = "That specified player does not exist."
                )

            # ------------------------------------------
            # Gets all active bans
            # ------------------------------------------

            cur.execute(
                """
                SELECT
                    ban_id,
                    reason,
                    banned_at,
                    expires_at
                FROM player_bans
                WHERE player_id = %s
                AND lifted_at IS NULL
                AND (
                    expires_at IS NULL
                    OR expires_at > CURRENT_TIMESTAMP
                )
                ORDER BY banned_at DESC;
                """,
                (
                    player_id,
                )
            )

            bans = cur.fetchall()

    return {
        "player_id": player_id,
        "is_banned": len(bans) > 0,
        "bans": [
            {
                "ban_id": ban[0],
                "reason": ban[1],
                "banned_at": ban[2],
                "expires_at": ban[3]
            }
            for ban in bans
        ]
    }


# ------------------------------------------
# Endpoint to lift a player's ban.
# ------------------------------------------

@app.patch("/bans/{ban_id}/lift")
def lift_player_ban(ban_id: int):

    # ------------------------------------------
    # Attempts to lift the ban
    # ------------------------------------------

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE player_bans
                    SET
                        lifted_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE ban_id = %s
                    AND lifted_at IS NULL
                    RETURNING ban_id;
                    """,
                    (
                        ban_id,
                    )
                )

                lifted_ban = cur.fetchone()

                # ------------------------------------------
                # Pops if the ban ID isn't found
                # ------------------------------------------

                if lifted_ban is None:
                    raise HTTPException(
                        status_code = 404,
                        detail = (
                            "That ban does not exist or has "
                            "already been lifted."
                        )
                    )

        return {
            "message": "Player ban has been lifted successfully!",
            "ban_id": lifted_ban[0]
        }

    # ------------------------------------------
    # Other errors not specifically caught
    # ------------------------------------------

    except DatabaseError as e:
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code = 500,
            detail = "A database error has occurred while lifting the ban."
        )

