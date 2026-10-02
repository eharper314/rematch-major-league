# ------------------------------------------
# Imports all required libraries/packages
# ------------------------------------------

import aiohttp, discord, calendar
from datetime import date


# ------------------------------------------
# All Modals
# ------------------------------------------


class SeasonNameModal(discord.ui.Modal):
    def __init__(self, season_view):
        super().__init__(title = "Set Season Name")

        self.season_view = season_view
        
        self.season_name = discord.ui.TextInput(
            label = "Season Name",
            placeholder = "Example: Season 123"
        )

        self.add_item(self.season_name)

    async def on_submit(
            self, 
            interaction: discord.Interaction
            ):
        self.season_view.season_name = self.season_name.value.strip()

        await interaction.response.edit_message(
            embed = self.season_view.build_embed(),
            view = self.season_view
        )

# ------------------------------------------
# Class for year selection dropdown
# ------------------------------------------
class YearSelect(discord.ui.Select):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------
    def __init__(self, date_view):

        self.date_view = date_view

        current_year = date.today().year

        options = []

        for year in range(current_year, current_year + 6):
            options.append(
                discord.SelectOption(
                    label = str(year),
                    value = str(year),
                    default = (year == date_view.selected_year)
                )
            )

        super().__init__(
            placeholder = "Select Year",
            options = options,
            row = 0
        )

    # ------------------------------------------
    # Dropdown functionality
    # ------------------------------------------

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        self.date_view.selected_year = int(self.values[0])
        self.date_view.selected_day = None
        self.date_view.refresh_day_selects()

        # ------------------------------------------
        # Update the message
        # ------------------------------------------

        await interaction.response.edit_message(
            embed = self.date_view.build_embed(),
            view = self.date_view
        )

# ------------------------------------------
# Class for selecting a month
# ------------------------------------------

class MonthSelect(discord.ui.Select):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------

    def __init__(self, date_view):

        self.date_view = date_view

        options = []

        for month_number in range(1, 13):

            options.append(
                discord.SelectOption(
                    label = calendar.month_name[month_number],
                    value = str(month_number),
                    default = (month_number == date_view.selected_month)
                )
            )

        super().__init__(
            placeholder = "Select Month",
            options = options,
            row = 1
        )

    # ------------------------------------------
    # Dropdown functionality
    # ------------------------------------------

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        self.date_view.selected_month = int(self.values[0])
        self.date_view.selected_day = None

        self.date_view.refresh_day_selects()

        # ------------------------------------------
        # Update the embed
        # ------------------------------------------
        await interaction.response.edit_message(
            embed = self.date_view.build_embed(),
            view = self.date_view
        )

# ------------------------------------------
# Classes for picking days
# ------------------------------------------

class DaySelectFirst(discord.ui.Select):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------

    def __init__(self, date_view, days_in_month):
        self.date_view = date_view

        maximum = min(25, days_in_month)

        options = []

        for day in range(1, maximum + 1):
            options.append(
                discord.SelectOption(
                    label = str(day),
                    value = str(day)
                )
            )

        super().__init__(
            placeholder = "Day 1-25",
            options = options,
            row = 2
        )

    # ------------------------------------------
    # Dropdown functionality
    # ------------------------------------------

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        self.date_view.selected_day = int(
            self.values[0]
        )

        await interaction.response.edit_message(
            embed=self.date_view.build_embed(),
            view=self.date_view
        )    

class DaySelectSecond(discord.ui.Select):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------

    def __init__(self, date_view, days_in_month):

        self.date_view = date_view

        options = []

        for day in range(26, days_in_month + 1):
            options.append(
                discord.SelectOption(
                    label=str(day),
                    value=str(day)
                )
            )

        super().__init__(
            placeholder="Day 26-31",
            options=options,
            row=3
        )

    # ------------------------------------------
    # Dropdown functionality
    # ------------------------------------------

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        self.date_view.selected_day = int(
            self.values[0]
        )

        await interaction.response.edit_message(
            embed=self.date_view.build_embed(),
            view=self.date_view
        )

# ------------------------------------------
# Embed for picking a date
# ------------------------------------------

class DatePickerView(discord.ui.View):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------

    def __init__(
        self,
        season_view,
        field_name,
        title
    ):
        super().__init__(timeout = 300)

        self.season_view = season_view
        self.field_name = field_name
        self.title = title

        today = date.today()

        self.selected_year = today.year
        self.selected_month = today.month
        self.selected_day = None

        self.add_item(YearSelect(self))
        self.add_item(MonthSelect(self))

        self.refresh_day_selects()


    # ------------------------------------------
    # Layout of the embed
    # ------------------------------------------

    def build_embed(self):

        embed = discord.Embed(
            title = f"{self.title}",
            description = "Choose the year, month, and day."
        )

        # ------------------------------------------
        # Field for the year
        # ------------------------------------------

        embed.add_field(
            name = "Year",
            value = str(self.selected_year),
            inline = True
        )

        # ------------------------------------------
        # Field for the month
        # ------------------------------------------

        embed.add_field(
            name = "Month",
            value = calendar.month_name[self.selected_month],
            inline = True
        )

        # ------------------------------------------
        # Field for the day
        # ------------------------------------------

        embed.add_field(
            name = "Day",
            value = (
                str(self.selected_day)
                if self.selected_day 
                else "Not selected"
            ),
            inline = True
        )
        
        return embed

    # ------------------------------------------
    # Refreshes the dropdown lists
    # ------------------------------------------

    def refresh_day_selects(self):

        # ------------------------------------------
        # Remove old day dropdowns
        # ------------------------------------------

        for item in list(self.children):

            if isinstance(
                item,
                (
                    DaySelectFirst,
                    DaySelectSecond
                )
            ):
                self.remove_item(item)

        days_in_month = calendar.monthrange(
            self.selected_year,
            self.selected_month
        )[1]

        # ------------------------------------------
        # Adds the first day dropdown
        # ------------------------------------------

        self.add_item(
            DaySelectFirst(
                self,
                days_in_month
            )
        )

        # ------------------------------------------
        # Adds the dropdown if there are more than
        # 25 days in a month (duh, but just in case)
        # ------------------------------------------
        if days_in_month > 25:
            self.add_item(
                DaySelectSecond(
                    self,
                    days_in_month
                )
            )


    # ------------------------------------------
    # Confrim button
    # ------------------------------------------

    @discord.ui.button(
        label = "Confirm Date",
        style = discord.ButtonStyle.success,
        row = 4
    )

    async def confirm_date(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        # ------------------------------------------
        # Error handling
        # ------------------------------------------

        if self.selected_day is None:

            await interaction.response.send_message(
                "Please select a day first.",
                ephemeral = True
            )

            return

        # ------------------------------------------
        # Package to send the information
        # ------------------------------------------

        selected_date = date(
            self.selected_year,
            self.selected_month,
            self.selected_day
        )

        setattr(
            self.season_view,
            self.field_name,
            selected_date
        )

        # ------------------------------------------
        # Update the original embed
        # ------------------------------------------

        if self.season_view.message:

            await self.season_view.message.edit(
                embed = self.season_view.build_embed(),
                view = self.season_view
            )

        # ------------------------------------------
        # Updates this message to show confirmation
        # ------------------------------------------

        await interaction.response.edit_message(
            content = (
                f"Selected "
                f"{selected_date.strftime("%B, %d, %Y")}"
            ),
            embed = None,
            view = None
        )

        self.stop()


# ------------------------------------------
# Embed for creating a season
# (/create_season)
# ------------------------------------------

class CreateSeasonView(discord.ui.View):

    # ------------------------------------------
    # Initialization of the class
    # ------------------------------------------
    def __init__(
        self,
        bot,
        season_id = None,
        season_name = None,
        start_date = None,
        end_date = None,
        free_agent_start = None,
        free_agent_end = None
    ):
        super().__init__(timeout = 300)

        self.bot = bot

        self.season_id = season_id
        self.season_name = season_name
        self.start_date = start_date
        self.end_date = end_date
        self.free_agent_start = free_agent_start
        self.free_agent_end = free_agent_end

        if self.season_id is not None:
            self.confirm_create_season.label = "Update Season"

    # ------------------------------------------
    # Funtion to edit the date format
    # ------------------------------------------

    def format_date(self, value):
        if value is None:
            return "Not Set"

        return value.strftime("%B %d, %Y")


    # ------------------------------------------
    # Layout of the embed
    # ------------------------------------------

    def build_embed(self):

        if self.season_id is None:
            title = "Create a Season"
        else:
            title = "Update a Season"

        embed = discord.Embed(
            title = title,
            description = "Set each field down below, then create the season."
        )
        # ------------------------------------------
        # Field for the season name
        # ------------------------------------------

        embed.add_field(
            name = "Season Name",
            value = self.season_name or "Not set",
            inline = False
        )

        # ------------------------------------------
        # Field for the season start and end dates
        # ------------------------------------------

        embed.add_field(
            name = "Season Dates",
            value = (
                f"**Start:** {self.format_date(self.start_date)}\n"
                f"**End:** {self.format_date(self.end_date)}"
            ),
            inline = False
        )

        # ------------------------------------------
        # Field for Free Agent start and end dates
        # ------------------------------------------

        embed.add_field(
            name = "Free Agent Dates",
            value = (
                f"**Start:** {self.format_date(self.free_agent_start)}\n"
                f"**End:** {self.format_date(self.free_agent_end)}"
            ),
            inline = False
        )

        # ------------------------------------------
        # Returns the actual embed
        # ------------------------------------------
        
        return embed
    
    # ------------------------------------------
    # Button for season name
    # ------------------------------------------

    @discord.ui.button(
        label = "Set Name",
        style = discord.ButtonStyle.secondary,
        row = 0
    )
    async def set_name(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            SeasonNameModal(self)
        )

    # ------------------------------------------
    # Button for season start date
    # ------------------------------------------

    @discord.ui.button(
    label="Set Start Date",
    style=discord.ButtonStyle.secondary,
    row = 1
    )
    async def set_start_date(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        date_view = DatePickerView(
            season_view = self,
            field_name = "start_date",
            title = "Select Season Start Date"
        )

        await interaction.response.send_message(
            embed = date_view.build_embed(),
            view = date_view,
            ephemeral = True
        )

    # ------------------------------------------
    # Button for season end date
    # ------------------------------------------

    @discord.ui.button(
        label = "Set End Date",
        style = discord.ButtonStyle.secondary,
        row = 1
    )
    async def set_end_date(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        date_view = DatePickerView(
            season_view = self,
            field_name = "end_date",
            title = "Select Season End Date"
        )

        await interaction.response.send_message(
            embed = date_view.build_embed(),
            view = date_view,
            ephemeral = True
        )

    # ------------------------------------------
    # Button for free agent start date
    # ------------------------------------------

    @discord.ui.button(
        label = "Set FA Start Date",
        style = discord.ButtonStyle.secondary,
        row = 2
    )
    async def set_fa_start_date(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        date_view = DatePickerView(
            season_view = self,
            field_name = "free_agent_start",
            title = "Select Free Agent Start Date"
        )

        await interaction.response.send_message(
            embed = date_view.build_embed(),
            view = date_view,
            ephemeral = True
        )

    # ------------------------------------------
    # Button for free agent end date
    # ------------------------------------------

    @discord.ui.button(
        label = "Set FA End Date",
        style = discord.ButtonStyle.secondary,
        row = 2
    )
    async def set_fa_end_date(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        date_view = DatePickerView(
            season_view = self,
            field_name = "free_agent_end",
            title = "Select Free Agent End Date"
        )

        await interaction.response.send_message(
            embed = date_view.build_embed(),
            view = date_view,
            ephemeral = True
        )

    # ------------------------------------------
    # Button for confirming
    # ------------------------------------------

    @discord.ui.button(
        label = "Create Season",
        style = discord.ButtonStyle.success,
        row = 3
    )
    async def confirm_create_season(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        # ------------------------------------------
        # Make sure all fields are filled
        # ------------------------------------------
        if not all([
            self.season_name,
            self.start_date,
            self.end_date,
            self.free_agent_start,
            self.free_agent_end
        ]):

            await interaction.response.send_message(
                "Please fill out all areas before creating the season.",
                ephemeral = True
            )
            return

        # ------------------------------------------
        # Gets the payload ready to be put into the
        # database.
        # ------------------------------------------
        
        payload = {
            "season_name": self.season_name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "free_agent_start": self.free_agent_start.isoformat(),
            "free_agent_end": self.free_agent_end.isoformat()
        }

        await interaction.response.defer(ephemeral = True)

        # ------------------------------------------
        # Attempts to write to the database
        # ------------------------------------------

        try:

            async with aiohttp.ClientSession() as session:

                # ------------------------------------------
                # Checks to see if it's in create mode or
                # update mode for the bot.
                # ------------------------------------------

                if self.season_id is None:
                    async with session.post(
                        f"{self.bot.apiURL}/season",
                        json = payload
                    ) as response:
                        data = await response.json()

                else:
                    async with session.patch(
                        f"{self.bot.apiURL}/season/{self.season_id}",
                        json = payload
                    ) as response:
                        data = await response.json()

                if response.status == 200:
                    self.stop()

                    success_embed = discord.Embed(
                        title = "Season Created",
                        description = (f"**{self.season_name}** was created successfully.")
                    )

                    await interaction.edit_original_response(
                        embed = success_embed,
                        view = None
                    )
                    return

                await interaction.followup.send(
                    data.get(
                        "detail",
                        "Something went wrong while creating the season."
                    ),
                    ephemeral = True
                )
        except aiohttp.ClientError:
            await interaction.followup.send(
                "Could not connect to the RML API.",
                ephemeral = True
            )
        

    # ------------------------------------------
    # Button for cancelling
    # ------------------------------------------
    
    @discord.ui.button(
        label = "Cancel",
        style = discord.ButtonStyle.danger,
        row = 3
    )

    async def cancelAction(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        self.stop()

        await interaction.response.edit_message(
            content = "Season creation cancelled.",
            embed = None,
            view = None
        )

# ------------------------------------------
# Embed for seeing a list of seasons in RML
# ------------------------------------------

class SeasonListView(discord.ui.View):
    # ------------------------------------------
    # Class initializaton
    # ------------------------------------------

    def __init__(self, seasons, per_page = 5):
        super().__init__(timeout = 300)

        self.seasons = seasons
        self.per_page = per_page
        self.current_page = 0

        self.total_pages = max(
            1,
            (len(seasons) + per_page - 1) // per_page
        )

        self.update_buttons()

    # ------------------------------------------
    # Building the embed
    # ------------------------------------------

    def build_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page

        page_seasons = self.seasons[start:end]

        embed = discord.Embed(
            title = "RML Seasons",
            description = (
                f"Page {self.current_page + 1} "
                f"of {self.total_pages}"
            )
        )
        # ------------------------------------------
        # If there are no seasons
        # ------------------------------------------

        if not page_seasons:
            embed.description = "No seasons are currently available."
            return embed

        # ------------------------------------------
        # Handles the formatting for each season.
        # ------------------------------------------

        for season in page_seasons:
            embed.add_field(
                name = (
                    f"{season['season_name']} "
                    f"- ID {season['season_id']}"
                ),
                value = (
                    f"**Start:** {season['start_date']}\n"
                    f"**End:** {season['end_date']}\n"
                    f"**Free Agent:** "
                    f"{season['free_agent_start']} → "
                    f"{season['free_agent_end']}"
                ),
                inline = False
            )

        return embed

    # ------------------------------------------
    # Updates the button each time
    # ------------------------------------------

    def update_buttons(self):
        self.previous_button.disabled = (
            self.current_page == 0
        )

        self.next_button.disabled = (
            self.current_page >= self.total_pages - 1
        )

    # ------------------------------------------
    # Button for Previous Page
    # ------------------------------------------

    @discord.ui.button(
        label = "Previous",
        style = discord.ButtonStyle.secondary
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed = self.build_embed(),
            view = self
        )

    # ------------------------------------------
    # Button for Next page
    # ------------------------------------------
    @discord.ui.button(
        label = "Next",
        style = discord.ButtonStyle.secondary
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed = self.build_embed(),
            view = self
        )

# ------------------------------------------
# Embed for seeing a specific season in RML.
# ------------------------------------------

def build_single_season_embed(season):
    embed = discord.Embed(
        title = season["season_name"]
    )

    embed.add_field(
        name = "Season ID",
        value = season["season_id"],
        inline = False
    )

    embed.add_field(
        name = "Start Date",
        value = season["start_date"],
        inline = True
    )

    embed.add_field(
        name ="End Date",
        value = season["end_date"],
        inline = True
    )

    embed.add_field(
        name = "Free Agent Start",
        value = season["free_agent_start"],
        inline = True
    )

    embed.add_field(
        name = "Free Agent End",
        value = season["free_agent_end"],
        inline = True
    )

    return embed