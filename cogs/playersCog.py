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
            # Gets the player's warning information
            # ------------------------------------------

            async with session.get(
                (
                    f"{self.bot.apiURL}/players/"
                    f"{data['player_id']}/warnings"
                )
            ) as response:

                warning_data = await response.json()

                # ------------------------------------------
                # Error handling
                # ------------------------------------------

                if response.status != 200:

                    await interaction.followup.send(
                        warning_data.get(
                            "detail",
                            "Something went wrong."
                        ),
                        ephemeral = True
                    )

                    return

            # ------------------------------------------
            # Gets the player's ban information
            # ------------------------------------------

            async with session.get(
                (
                    f"{self.bot.apiURL}/players/"
                    f"{data['player_id']}/bans"
                )
            ) as response:

                ban_data = await response.json()

                # ------------------------------------------
                # Error handling
                # ------------------------------------------

                if response.status != 200:

                    await interaction.followup.send(
                        ban_data.get(
                            "detail",
                            "Something went wrong."
                        ),
                        ephemeral = True
                    )

                    return

        # ------------------------------------------
        # Adds warning information to the player
        # ------------------------------------------

        data["warning_amount"] = warning_data["warning_amount"]
        data["current_warnings"] = warning_data["current_warnings"]
        data["warnings"] = warning_data["warnings"]

        # ------------------------------------------
        # Adds ban information to the player
        # ------------------------------------------

        data["is_banned"] = ban_data["is_banned"]
        data["bans"] = ban_data["bans"]

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
    # Command for warning a player
    # ------------------------------------------

    @app_commands.command(
        name = "warn_player",
        description = "STAFF COMMAND: Gives an RML player a warning."
    )
    async def warn_player(
        self,
        interaction: discord.Interaction,
        player: discord.Member,
        warning_type: str,
        reason: str
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
            # Sets required variables
            # ------------------------------------------

            player_id = data["player_id"]
            player_ign = data["ign"]

            payload = {
                "warning_type": warning_type,
                "reason": reason,
                "expires_at": None
            }

            # ------------------------------------------
            # Attempts to warn the player
            # ------------------------------------------

            async with session.post(
                (
                    f"{self.bot.apiURL}/players/"
                    f"{player_id}/warnings"
                ),
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
        # Command response
        # ------------------------------------------

        embed = discord.Embed(
            title = "Player Warned",
            description = (
                f"{player.mention} has received an RML warning."
            )
        )

        embed.add_field(
            name = "Player",
            value = player_ign,
            inline = False
        )

        embed.add_field(
            name = "Warning Type",
            value = warning_type,
            inline = False
        )

        embed.add_field(
            name = "Reason",
            value = reason,
            inline = False
        )

        embed.add_field(
            name = "Warning ID",
            value = data["warning_id"],
            inline = False
        )

        await interaction.followup.send(
            embed = embed,
            ephemeral = True
        )

    # ------------------------------------------
    # Command for removing a player warning
    # ------------------------------------------

    @app_commands.command(
        name = "remove_warning",
        description = "STAFF COMMAND: Removes an active player warning."
    )
    async def remove_warning(
        self,
        interaction: discord.Interaction,
        warning_id: int
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
        # Attempts to remove the warning
        # ------------------------------------------

        async with aiohttp.ClientSession() as session:
            async with session.patch(
                (
                    f"{self.bot.apiURL}/warnings/"
                    f"{warning_id}/remove"
                )
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
        # Command response
        # ------------------------------------------

        embed = discord.Embed(
            title = "Warning Removed",
            description = (
                f"Warning ID **{warning_id}** has been removed."
            )
        )

        await interaction.followup.send(
            embed = embed,
            ephemeral = True
        )    

    # ------------------------------------------
    # Command for banning a player
    # ------------------------------------------

    @app_commands.command(
        name = "ban_player",
        description = "STAFF COMMAND: Bans an RML player."
    )
    async def ban_player(
        self,
        interaction: discord.Interaction,
        player: discord.Member,
        reason: str
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
            # Sets required variables
            # ------------------------------------------

            player_id = data["player_id"]
            player_ign = data["ign"]

            payload = {
                "reason": reason,
                "expires_at": None
            }

            # ------------------------------------------
            # Attempts to ban the player
            # ------------------------------------------

            async with session.post(
                (
                    f"{self.bot.apiURL}/players/"
                    f"{player_id}/bans"
                ),
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
        # Command response
        # ------------------------------------------

        embed = discord.Embed(
            title = "Player Banned",
            description = (
                f"{player.mention} has been banned from RML."
            )
        )

        embed.add_field(
            name = "Player",
            value = player_ign,
            inline = False
        )

        embed.add_field(
            name = "Reason",
            value = reason,
            inline = False
        )

        embed.add_field(
            name = "Ban ID",
            value = data["ban_id"],
            inline = False
        )

        await interaction.followup.send(
            embed = embed,
            ephemeral = True
        )

    # ------------------------------------------
    # Command for lifting a player ban
    # ------------------------------------------

    @app_commands.command(
        name = "unban_player",
        description = "STAFF COMMAND: Lifts an active player ban."
    )
    async def unban_player(
        self,
        interaction: discord.Interaction,
        ban_id: int
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
        # Attempts to lift the player's ban
        # ------------------------------------------

        async with aiohttp.ClientSession() as session:
            async with session.patch(
                (
                    f"{self.bot.apiURL}/bans/"
                    f"{ban_id}/lift"
                )
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
        # Command response
        # ------------------------------------------

        embed = discord.Embed(
            title = "Player Unbanned",
            description = (
                f"Ban ID **{ban_id}** has been lifted."
            )
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