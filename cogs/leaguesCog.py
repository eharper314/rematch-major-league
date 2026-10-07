# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

import discord, aiohttp
from discord import app_commands
from discord.ext import commands
from datetime import date



# ------------------------------------------
# Holder for all commands in this Cog
# ------------------------------------------

class Leagues(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------
    # Command for creating a league in RML
    # ------------------------------------------

    @app_commands.commands(
        name = "create_league",
        description = "ADMIN COMMAND: Creates a league for RML."
    )
    async def create_league(
        self,
        interaction: discord.Interaction,
        season_id: int,
        league_name: str
    ):
        
        # ------------------------------------------
        # Sets required variables
        # ------------------------------------------

        user_role_ids = [
            role.id
            for role in interaction.user.roles
        ]

        # ------------------------------------------
        # Checks to see if the user has permissions
        # ------------------------------------------

        if not any(
            role_id in self.bot.adminRoles
            for role_id in user_role_ids
        ):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral = True
            )
            return

        # ------------------------------------------
        # Instant response so no timing out
        # ------------------------------------------

        await interaction.response.defer(ephemeral = True)

        # ------------------------------------------
        # Command response
        # ------------------------------------------

        payload = {
            "league_name": league_name
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.bot.apiURL}/seasons/{season_id}/leagues",
                json = payload
            ) as response:

                data = await response.json()

                if response.status != 200:
                    await interaction.followup.send(
                        data.get(
                            "detail",
                            "Something went wrong while creating the league."
                        ),
                        ephemeral = True
                    )
                    return

        await interaction.followup.send(
            f" League **{league_name} was created successfully!",
            ephemeral = True
        )


