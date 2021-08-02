import pytest
import discord.ext.test as dpytest
from main import MyBot
import discord

@pytest.fixture
def bot(event_loop):
    intents = discord.Intents.all()
    bot = MyBot("/", loop=event_loop, intents=intents)
    dpytest.configure(bot, num_guilds=2, num_members=3)
    return bot

@pytest.mark.asyncio
async def test_mem(bot: MyBot):
    await dpytest.message("/mem")
    assert dpytest.verify().message().content("4")

@pytest.mark.asyncio
async def test_nothing(bot: MyBot):
    await dpytest.message("/neko")
    assert dpytest.verify().message().nothing()
