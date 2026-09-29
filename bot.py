# ------------------------------------------
# Imports for all needed libraries/packages
# ------------------------------------------

import os, discord
from discord import app_commands
from dotenv import load_dotenv

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
allowed_mentions = discord.AllowedMentions(
    everyone=True,
    users=True,
    roles=True,
    replied_user=True
)

client = discord.Client(intents=intents, allowed_mentions=allowed_mentions)
tree = app_commands.CommandTree(client)

# ------------------------------------------
# Bot initialization
# ------------------------------------------
@client.event
async def on_ready():
    synced = await tree.sync()
    print(f"Logged in as {client.user}")
    print(f"Synced {len(synced)} commands!")
    print(f"Commands synced: ")

    for command in synced:
        print(f"- {command.name}")






# ------------------------------------------
# Command for bot to actually run
# ------------------------------------------
client.run(botToken)