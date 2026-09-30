# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

import os, discord
from dotenv import load_dotenv
from discord.ext import commands

# ------------------------------------------
# To run the bot locally, run this:
# python bot.py
# ------------------------------------------

# ------------------------------------------
# Global Variables
# ------------------------------------------

# Nothing... for now >:)

# ------------------------------------------
# Global classes
# ------------------------------------------

# Nothing... for now >:)

# ------------------------------------------
# .env initalization and variables
# ------------------------------------------

load_dotenv()

apiURL = os.getenv("API_URL")
botToken = os.getenv("DISCORD_BOT_TOKEN")
adminRoleID = int(os.getenv("ADMIN_ROLE_ID"))
coAdminRoleID = int(os.getenv("CO_ADMIN_ROLE_ID"))
staffRoleID = int(os.getenv("STAFF_ROLE_ID"))
managerRoleID = int(os.getenv("MANAGER_ROLE_ID"))
asstManagerRoleID = int(os.getenv("ASST_MANAGER_ROLE_ID"))

# ------------------------------------------
# Bot-specific Variables
# ------------------------------------------


adminRoles = [adminRoleID, coAdminRoleID]
staffRoles = [adminRoleID, coAdminRoleID, staffRoleID]
managerRoles = [managerRoleID, asstManagerRoleID]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
allowed_mentions = discord.AllowedMentions(
    everyone=True,
    users=True,
    roles=True,
    replied_user=True
)

bot = commands.Bot(
    command_prefix = "!",
    intents = intents,
    allowed_mentions = allowed_mentions
)

# ------------------------------------------
# Making the role IDs accessible to cogs
# ------------------------------------------

bot.apiURL = apiURL

bot.adminRolID = adminRoleID
bot.coAdminRoleID = coAdminRoleID
bot.staffRoleID = staffRoleID
bot.manager_RoleID = managerRoleID
bot.asstManagerRoleID = asstManagerRoleID

bot.adminRoles = adminRoles
bot.staffRoles = staffRoles
bot.managerRoles = managerRoles

# ------------------------------------------
# Loads all the cogs into the bot
# ------------------------------------------

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.seasonsCog")

    await bot.tree.sync()
# ------------------------------------------
# Bot initialization
# ------------------------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ------------------------------------------
# Command for bot to actually run
# ------------------------------------------
bot.run(botToken)
