import pytest
import discord.ext.test as dpytest
from test import MyTestableBot
import discord

@pytest.fixture
def bot(event_loop):
    intents = discord.Intents.all()
    bot = MyTestableBot("/", loop=event_loop, intents=intents)
    dpytest.configure(bot, num_guilds=2, num_members=3)
    return bot

@pytest.mark.asyncio
async def test_neko(bot: MyTestableBot):
    await dpytest.message("/neko")
    assert dpytest.verify().message().content("にゃーん")

@pytest.mark.asyncio
async def test_ping(bot: MyTestableBot):
    guild: discord.Guild = bot.guilds[0]
    await dpytest.message("/ping")
    assert dpytest.verify().message().contains().content("pong!")
