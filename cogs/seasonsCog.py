# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

import discord
from discord import app_commands
from discord.ext import commands

from views.seasonsView import CreateSeasonView

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
        # Instant response so no timing out
        # ------------------------------------------
        await interaction.response.defer(ephemeral = True)
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
        # Command response
        # ------------------------------------------

        message = await interaction.followup.send(
            embed = view.build_embed(),
            view = view,
            ephemeral = True
        )

        view.message = message
# ------------------------------------------
# Allows the Cog to be initialized
# ------------------------------------------

async def setup(bot):
    await bot.add_cog(Seasons(bot))