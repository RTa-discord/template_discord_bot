from discord.ext import commands
import time
import traceback
import os

class Admin(commands.Cog, name='管理用コマンド群'):
    """
    管理用のコマンドです
    """

    def __init__(self, bot):
        self.bot = bot


    async def cog_check(self, ctx):
        return ctx.guild and await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['p'], hidden=False, description='疎通確認')
    async def ping(self, ctx):
        """Pingによる疎通確認を行うコマンド"""
        start_time = time.time()
        mes = await ctx.reply("Pinging....")
        await mes.edit(content="pong!\n" + str(round(time.time() - start_time, 3) * 1000) + "ms")

    @commands.command(aliases=['wh'], hidden=True)
    async def where(self, ctx):
        """今どこにいるかを確認する関数
        """
        await ctx.reply("現在入っているサーバーは以下です", mention_author=False)
        server_list = '\n'.join(
            [i.name.replace('\u3000', ' ') + ' : ' + str(i.id) for i in ctx.bot.guilds])

        await ctx.reply(f"{server_list}", mention_author=False)

    @commands.command(aliases=['mem'], hidden=True)
    async def num_of_member(self, ctx):
        """そのサーバーに何人いるかを確認する関数
        """
        await ctx.reply(f"{ctx.guild.member_count}", mention_author=False)

def setup(bot):
    bot.add_cog(Admin(bot))
