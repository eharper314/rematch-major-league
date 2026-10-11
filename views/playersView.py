# ------------------------------------------
# Imports all required libraries/packages
# ------------------------------------------

import aiohttp, discord


# ------------------------------------------
# Modal for registering a player
# ------------------------------------------

class RegisterPlayerModal(discord.ui.Modal):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------

    def __init__(self, bot):
        super().__init__(
            title = "Register for RML"
        )

        self.bot = bot

        self.ign = discord.ui.TextInput(
            label = "In-Game Name",
            placeholder = "Enter your REMATCH IGN",
            min_length = 1,
            max_length = 32
        )

        self.add_item(self.ign)

    # ------------------------------------------
    # Handles submission of the modal
    # ------------------------------------------

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        # ------------------------------------------
        # Instant response so no timing out
        # ------------------------------------------

        await interaction.response.defer(
            ephemeral = True
        )

        # ------------------------------------------
        # Sets required variables
        # ------------------------------------------

        ign = self.ign.value.strip()

        payload = {
            "discord_user_id": interaction.user.id,
            "ign": ign
        }

        # ------------------------------------------
        # Attempts to register the player
        # ------------------------------------------

        try:

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.bot.apiURL}/players",
                    json = payload
                ) as response:

                    data = await response.json()

                    # ------------------------------------------
                    # Player was registered successfully
                    # ------------------------------------------

                    if response.status == 200:

                        registered_role = interaction.guild.get_role(
                            self.bot.registeredRoleID
                        )

                        # ------------------------------------------
                        # Gives the Registered role
                        # ------------------------------------------

                        if registered_role is not None:

                            if registered_role not in interaction.user.roles:

                                await interaction.user.add_roles(
                                    registered_role,
                                    reason = "RML player registration"
                                )

                        # ------------------------------------------
                        # Updates the player's Discord nickname
                        # ------------------------------------------

                        try:

                            await interaction.user.edit(
                                nick = ign,
                                reason = "RML player registration"
                            )

                        except discord.Forbidden:

                            await interaction.followup.send(
                                (
                                    "You were registered successfully, but I "
                                    "could not update your server nickname."
                                ),
                                ephemeral = True
                            )

                            return

                        # ------------------------------------------
                        # Command response
                        # ------------------------------------------

                        await interaction.followup.send(
                            (
                                f"You have successfully registered for RML "
                                f"with the IGN **{ign}**."
                            ),
                            ephemeral = True
                        )

                        return

                    # ------------------------------------------
                    # Player is already registered
                    # ------------------------------------------

                    if response.status == 409:

                        registered_role = interaction.guild.get_role(
                            self.bot.registeredRoleID
                        )

                        # ------------------------------------------
                        # Repairs the Registered role if needed
                        # ------------------------------------------

                        if registered_role is not None:

                            if registered_role not in interaction.user.roles:

                                await interaction.user.add_roles(
                                    registered_role,
                                    reason = "Restoring RML Registered role"
                                )

                        await interaction.followup.send(
                            (
                                "You are already registered in RML. "
                                "Use **Update IGN** if you need to "
                                "change your IGN."
                            ),
                            ephemeral = True
                        )

                        return

                    # ------------------------------------------
                    # Error handling
                    # ------------------------------------------

                    await interaction.followup.send(
                        data.get(
                            "detail",
                            "Something went wrong while registering."
                        ),
                        ephemeral = True
                    )

        # ------------------------------------------
        # API connection error
        # ------------------------------------------

        except aiohttp.ClientError:

            await interaction.followup.send(
                "Could not connect to the RML API.",
                ephemeral = True
            )


# ------------------------------------------
# Modal for updating a player's IGN
# ------------------------------------------

class UpdateIgnModal(discord.ui.Modal):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------

    def __init__(self, bot):
        super().__init__(
            title = "Update IGN"
        )

        self.bot = bot

        self.ign = discord.ui.TextInput(
            label = "New In-Game Name",
            placeholder = "Enter your new REMATCH IGN",
            min_length = 1,
            max_length = 32
        )

        self.add_item(self.ign)

    # ------------------------------------------
    # Handles submission of the modal
    # ------------------------------------------

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        # ------------------------------------------
        # Instant response so no timing out
        # ------------------------------------------

        await interaction.response.defer(
            ephemeral = True
        )

        # ------------------------------------------
        # Sets required variables
        # ------------------------------------------

        new_ign = self.ign.value.strip()

        # ------------------------------------------
        # Attempts to find the player
        # ------------------------------------------

        try:

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    (
                        f"{self.bot.apiURL}/players/discord/"
                        f"{interaction.user.id}"
                    )
                ) as response:

                    data = await response.json()

                    # ------------------------------------------
                    # Player is not registered
                    # ------------------------------------------

                    if response.status == 404:

                        await interaction.followup.send(
                            (
                                "You are not currently registered in RML. "
                                "Use the **Register** button first."
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
                                "Something went wrong while finding your player account."
                            ),
                            ephemeral = True
                        )

                        return

                    player_id = data["player_id"]
                    old_ign = data["ign"]

                # ------------------------------------------
                # Gets the update payload ready
                # ------------------------------------------

                payload = {
                    "ign": new_ign
                }

                # ------------------------------------------
                # Attempts to update the player's IGN
                # ------------------------------------------

                async with session.patch(
                    (
                        f"{self.bot.apiURL}/players/"
                        f"{player_id}/ign"
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
                                "Something went wrong while updating your IGN."
                            ),
                            ephemeral = True
                        )

                        return

        # ------------------------------------------
        # API connection error
        # ------------------------------------------

        except aiohttp.ClientError:

            await interaction.followup.send(
                "Could not connect to the RML API.",
                ephemeral = True
            )

            return

        # ------------------------------------------
        # Updates the player's Discord nickname
        # ------------------------------------------

        try:

            await interaction.user.edit(
                nick = new_ign,
                reason = "RML IGN update"
            )

        except discord.Forbidden:

            await interaction.followup.send(
                (
                    f"Your IGN was updated from **{old_ign}** to "
                    f"**{new_ign}**, but I could not update your "
                    f"server nickname."
                ),
                ephemeral = True
            )

            return

        # ------------------------------------------
        # Command response
        # ------------------------------------------

        await interaction.followup.send(
            (
                f"Your IGN has been updated from "
                f"**{old_ign}** to **{new_ign}**."
            ),
            ephemeral = True
        )


# ------------------------------------------
# Persistent player registration view
# ------------------------------------------

class RegistrationView(discord.ui.View):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------

    def __init__(self, bot):
        super().__init__(
            timeout = None
        )

        self.bot = bot

    # ------------------------------------------
    # Button for registering a player
    # ------------------------------------------

    @discord.ui.button(
        label = "Register",
        style = discord.ButtonStyle.success,
        custom_id = "rml_player_register"
    )
    async def register_player(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            RegisterPlayerModal(
                self.bot
            )
        )

    # ------------------------------------------
    # Button for updating an IGN
    # ------------------------------------------

    @discord.ui.button(
        label = "Update IGN",
        style = discord.ButtonStyle.secondary,
        custom_id = "rml_player_update_ign"
    )
    async def update_ign(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            UpdateIgnModal(
                self.bot
            )
        )


# ------------------------------------------
# Embed for the player registration panel
# ------------------------------------------

def build_registration_embed():

    embed = discord.Embed(
        title = "RML Player Registration",
        description = (
            "Register yourself as an RML player below.\n\n"
            "If you are already registered and need to change "
            "your IGN, use the **Update IGN** button."
        )
    )

    # ------------------------------------------
    # Registration information
    # ------------------------------------------

    embed.add_field(
        name = "Register",
        value = (
            "Use this if you have never registered for RML before."
        ),
        inline = False
    )

    # ------------------------------------------
    # IGN update information
    # ------------------------------------------

    embed.add_field(
        name = "Update IGN",
        value = (
            "Use this if you are already registered and need "
            "to update your current IGN."
        ),
        inline = False
    )

    return embed


# ------------------------------------------
# Embed for seeing a specific player in RML.
# ------------------------------------------

def build_player_embed(
    player,
    member
):

    # ------------------------------------------
    # Determines the player's standing
    # ------------------------------------------

    if player.get("is_banned", False):

        standing = "⛔ Banned"

    elif player.get("current_warnings", 0) > 0:

        standing = "⚠️ Warned"

    else:

        standing = "✅ Good Standing"

    # ------------------------------------------
    # Gets the player's current team
    # ------------------------------------------

    current_team = player.get(
        "current_team"
    )

    if current_team is None:

        current_team_name = "No Team"

    else:

        current_team_name = current_team["team_name"]

    # ------------------------------------------
    # Determines if they played this season
    # ------------------------------------------

    if player.get("played_this_season", False):

        played_this_season = "Yes"

    else:

        played_this_season = "No"

    # ------------------------------------------
    # Creates the embed
    # ------------------------------------------

    embed = discord.Embed(
        title = f"Player Overview: {member.display_name}"
    )

    # ------------------------------------------
    # General Info
    # ------------------------------------------

    embed.add_field(
        name = "General Info",
        value = (
            f"**IGN:** {player['ign']}\n"
            f"**Player ID:** {player['player_id']}"
        ),
        inline = False
    )

    # ------------------------------------------
    # Team Info
    # ------------------------------------------

    embed.add_field(
        name = "Team Info",
        value = (
            f"**Current Team:** {current_team_name}\n"
            f"**Played This Season:** {played_this_season}"
        ),
        inline = False
    )

    # ------------------------------------------
    # Standing Info
    # ------------------------------------------

    embed.add_field(
        name = "Standing Info",
        value = (
            f"**Standing:** {standing}\n"
            f"**Warning Amount:** "
            f"{player.get('warning_amount', 0)}\n"
            f"**Current Warnings:** "
            f"{player.get('current_warnings', 0)}"
        ),
        inline = False
    )

    # ------------------------------------------
    # Gets active warnings
    # ------------------------------------------

    warnings = player.get(
        "warnings",
        []
    )

    # ------------------------------------------
    # Formats active warnings
    # ------------------------------------------

    if warnings:

        warning_text = ""

        for warning in warnings:

            warning_text += (
                f"**ID {warning['warning_id']} "
                f"— {warning['warning_type']}**\n"
            )

            if warning.get("reason"):

                warning_text += (
                    f"{warning['reason']}\n"
                )

            if warning.get("expires_at"):

                warning_text += (
                    f"Expires: {warning['expires_at']}\n"
                )

            warning_text += "\n"

        warning_text = warning_text.strip()

    else:

        warning_text = "No active warnings."

    # ------------------------------------------
    # Active Warnings
    # ------------------------------------------

    embed.add_field(
        name = "Active Warnings",
        value = warning_text,
        inline = False
    )

    # ------------------------------------------
    # Gets active bans
    # ------------------------------------------

    bans = player.get(
        "bans",
        []
    )

    # ------------------------------------------
    # Formats active bans
    # ------------------------------------------

    if bans:

        ban_text = ""

        for ban in bans:

            ban_text += (
                f"**ID {ban['ban_id']}**\n"
                f"{ban.get('reason', 'No reason provided.')}\n"
            )

            if ban.get("expires_at"):

                ban_text += (
                    f"Expires: {ban['expires_at']}\n"
                )

            else:

                ban_text += (
                    "Expires: Never\n"
                )

            ban_text += "\n"

        ban_text = ban_text.strip()

    else:

        ban_text = "No active bans."

    # ------------------------------------------
    # Active Bans
    # ------------------------------------------

    embed.add_field(
        name = "Active Bans",
        value = ban_text,
        inline = False
    )

    return embed
