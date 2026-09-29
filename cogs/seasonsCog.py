# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

import discord
from discord import app_commands
from discord.ext import commands

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
        # Captures the user's roles
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
        # Command response
        # ------------------------------------------

        await interaction.response.send_message(
            "Season command works!",
            ephemeral = True
        )

# ------------------------------------------
# Allows the Cog to be initialized
# ------------------------------------------

async def setup(bot):
    await bot.add_cog(Seasons(bot))