# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

import discord, aiohttp
from discord import app_commands
from discord.ext import commands
from datetime import date

from views.seasonsView import CreateSeasonView, SeasonListView
from views.seasonsView import (
    build_single_season_embed
)

# ------------------------------------------
# Holder for all commands in this Cog
# ------------------------------------------

class Seasons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------
    # Command for creating a season in RML
    # ------------------------------------------

    @app_commands.command(
        name = "create_season",
        description = "ADMIN COMMAND: Creates a season for RML."
    )
    async def create_season(
        self,
        interaction: discord.Interaction
    ):
        # ------------------------------------------
        # Sets required variables
        # ------------------------------------------

        user_role_ids = [
            role.id
            for role in interaction.user.roles
        ]

        view = CreateSeasonView(self.bot)
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

        message = await interaction.followup.send(
            embed = view.build_embed(),
            view = view,
            ephemeral = True
        )

        view.message = message

    # ------------------------------------------
    # Command for viewing a season
    # ------------------------------------------

    @app_commands.command(
        name = "view_season",
        description = "GENERAL COMMAND: Allows you to view a list of season, or one specific season."
    )
    async def view_season(
        self,
        interaction: discord.Interaction,
        season_id: int | None = None
    ):
        await interaction.response.defer(ephemeral = False)

        async with aiohttp.ClientSession() as session:

            # ------------------------------------------
            # Command to get the full list.
            # ------------------------------------------

            if season_id is None:
                url = f"{self.bot.apiURL}/season"

            # ------------------------------------------
            # Command to get a specific season
            # ------------------------------------------
            
            else:
                url = f"{self.bot.apiURL}/season/{season_id}"

            async with session.get(url) as response:

                data = await response.json()

                if response.status != 200:
                    await interaction.followup.send(
                        data.get(
                            "detail",
                            "Something went wrong."
                        ),
                        ephemeral = True
                    )
                    return

            # ------------------------------------------
            # Response for givine a list
            # ------------------------------------------

            if season_id is None:
                view = SeasonListView(data)

                await interaction.followup.send(
                    embed = view.build_embed(),
                    view = view
                )

            # ------------------------------------------
            # Specific season response
            # ------------------------------------------
            else:
                embed = build_single_season_embed(data)

                await interaction.followup.send(
                    embed = embed
                )

    # ------------------------------------------
    # Command for updating a season
    # ------------------------------------------

    @app_commands.command(
        name = "update_season",
        description = "ADMIN COMMAND: Update an existing season."
    )
    async def update_season(
        self,
        interaction: discord.Interaction,
        season_id: int
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

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.bot.apiURL}/season/{season_id}"
            ) as response:

                data = await response.json()

                if response.status != 200:
                    await interaction.followup.send(
                        data.get(
                            "detail",
                            "Something went wrong."
                        ),
                        ephemeral = True
                    )
                    return

        view = CreateSeasonView(
            bot = self.bot,
            season_id = data["season_id"],
            season_name = data["season_name"],
            start_date = date.fromisoformat(data["start_date"]),
            end_date = date.fromisoformat(data["end_date"]),
            free_agent_start = date.fromisoformat(data["free_agent_start"]),
            free_agent_end = date.fromisoformat(data["free_agent_end"])
        )

        message = await interaction.followup.send(
            embed = view.build_embed(),
            view = view,
            ephemeral = True,
            wait = True
        )

        view.message = message
    
# ------------------------------------------
# Allows the Cog to be initialized
# ------------------------------------------

async def setup(bot):
    await bot.add_cog(Seasons(bot))