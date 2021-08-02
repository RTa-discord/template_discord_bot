import discord
import json
from discord.ext import commands
from dotenv import load_dotenv
import traceback
import os

intents = discord.Intents.default()
intents.members = True

class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, intents=intents)

        for cog in os.listdir(currentpath + "/cogs"):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f'cogs.{cog[:-3]}')
                except Exception:
                    traceback.print_exc()

        with open(currentpath + "/data/setting.json", encoding='utf-8') as f:
            self.json_data = json.load(f)

        self.admin_id = self.json_data['admin']["id"]
        self.status = self.json_data['status']

    async def on_ready(self):
        print('-----')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await bot.change_presence(activity=discord.Game(name=self.status))

if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    token = os.getenv('DISCORD_BOT_TOKEN')
    currentpath = os.path.dirname(os.path.abspath(__file__))

    bot = MyBot(command_prefix=commands.when_mentioned_or('/'))
    with open(currentpath + "/data/specific_setting.json", encoding='utf-8') as f:
        json_data = json.load(f)
    bot.run(token)
    # bot.run(os.environ.get("DISCORD_TOKEN"))
