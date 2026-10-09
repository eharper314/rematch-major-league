# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

import discord, aiohttp
from discord import app_commands
from discord.ext import commands

from views.playersView import RegistrationView
from views.playersView import (
    build_registration_embed,
    build_player_embed
)

# ------------------------------------------
# Holder for all commands in this Cog
# ------------------------------------------

class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------
    # Command for setting up player registration
    # ------------------------------------------

    @app_commands.command(
        name = "setup_registration",
        description = "ADMIN COMMAND: Sets up the RML player registration panel."
    )
    async def setup_registration(
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

        view = RegistrationView(self.bot)

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
            embed = build_registration_embed(),
            view = view
        )

    # ------------------------------------------
    # Command for viewing a player
    # ------------------------------------------

    @app_commands.command(
        name = "view_player",
        description = "STAFF COMMAND: Allows you to view a specific player."
    )
    async def view_player(
        self,
        interaction: discord.Interaction,
        player: discord.Member
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
            role_id in self.bot.staffRoles
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

        await interaction.response.defer(
            ephemeral = True
        )

        # ------------------------------------------
        # Attempts to get the player information
        # ------------------------------------------

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.bot.apiURL}/players/discord/{player.id}"
            ) as response:

                data = await response.json()

                # ------------------------------------------
                # Player is not registered
                # ------------------------------------------

                if response.status == 404:

                    await interaction.followup.send(
                        (
                            f"{player.mention} is not currently "
                            f"registered in RML."
                        ),
                        ephemeral = True
                    )

                    return

                # ------------------------------------------
                # Error handling
                # ------------------------------------------

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
        # Command response
        # ------------------------------------------

        embed = build_player_embed(
            data,
            player
        )

        await interaction.followup.send(
            embed = embed,
            ephemeral = True
        )

    # ------------------------------------------
    # Command for updating a player's IGN
    # ------------------------------------------

    @app_commands.command(
        name = "update_ign",
        description = "STAFF COMMAND: Updates a player's REMATCH IGN."
    )
    async def update_ign(
        self,
        interaction: discord.Interaction,
        player: discord.Member,
        new_ign: str
    ):
        # ------------------------------------------
        # Sets required variables
        # ------------------------------------------

        user_role_ids = [
            role.id
            for role in interaction.user.roles
        ]

        new_ign = new_ign.strip()

        # ------------------------------------------
        # Checks to see if the user has permissions
        # ------------------------------------------

        if not any(
            role_id in self.bot.staffRoles
            for role_id in user_role_ids
        ):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral = True
            )
            return

        # ------------------------------------------
        # Checks to see if the IGN is valid
        # ------------------------------------------

        if len(new_ign) < 1 or len(new_ign) > 32:

            await interaction.response.send_message(
                "The IGN must be between 1 and 32 characters.",
                ephemeral = True
            )

            return

        # ------------------------------------------
        # Instant response so no timing out
        # ------------------------------------------

        await interaction.response.defer(
            ephemeral = True
        )

        # ------------------------------------------
        # Attempts to get the player information
        # ------------------------------------------

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.bot.apiURL}/players/discord/{player.id}"
            ) as response:

                data = await response.json()

                # ------------------------------------------
                # Player is not registered
                # ------------------------------------------

                if response.status == 404:

                    await interaction.followup.send(
                        (
                            f"{player.mention} is not currently "
                            f"registered in RML."
                        ),
                        ephemeral = True
                    )

                    return

                # ------------------------------------------
                # Error handling
                # ------------------------------------------

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
            # Sets required variables
            # ------------------------------------------

            player_id = data["player_id"]
            old_ign = data["ign"]

            payload = {
                "ign": new_ign
            }

            # ------------------------------------------
            # Attempts to update the player's IGN
            # ------------------------------------------

            async with session.patch(
                f"{self.bot.apiURL}/staff/players/{player_id}/ign",
                json = payload
            ) as response:

                data = await response.json()

                # ------------------------------------------
                # Error handling
                # ------------------------------------------

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
        # Updates the player's Discord nickname
        # ------------------------------------------

        try:

            await player.edit(
                nick = new_ign,
                reason = "RML staff IGN update"
            )

        except discord.Forbidden:

            await interaction.followup.send(
                (
                    f"{player.mention}'s IGN was updated from "
                    f"**{old_ign}** to **{new_ign}**, but I could "
                    f"not update their server nickname."
                ),
                ephemeral = True
            )

            return

        # ------------------------------------------
        # Command response
        # ------------------------------------------

        embed = discord.Embed(
            title = "IGN Updated",
            description = (
                f"{player.mention}'s IGN has been updated."
            )
        )

        embed.add_field(
            name = "Old IGN",
            value = old_ign,
            inline = True
        )

        embed.add_field(
            name = "New IGN",
            value = new_ign,
            inline = True
        )

        await interaction.followup.send(
            embed = embed,
            ephemeral = True
        )

# ------------------------------------------
# Allows the Cog to be initialized
# ------------------------------------------

async def setup(bot):
    await bot.add_cog(Players(bot))