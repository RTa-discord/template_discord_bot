# !/usr/bin/env python3

import os
import time
from datetime import datetime
import asyncio
import aiohttp
import discord
from discord import Forbidden
import tzlocal
from discord.ext import commands, tasks, components

from .utils.common import CommonUtil


ret = {}

class Admin(commands.Cog, name='管理用コマンド群'):
    """
    管理用のコマンドです
    """

    def __init__(self, bot):
        self.bot = bot
        self.c = CommonUtil()

        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

        self.local_timezone = tzlocal.get_localzone()

        self.auto_backup.stop()
        self.auto_backup.start()

    async def cog_check(self, ctx):
        return ctx.guild and await self.bot.is_owner(ctx.author)


    @commands.command(aliases=['re'], hidden=True)
    async def reload(self, ctx, cogname: str = "ALL"):
        if cogname == "ALL":
            reloaded_list = []
            for cog in os.listdir(self.master_path + "/cogs"):
                if cog.endswith(".py"):
                    try:
                        cog = cog[:-3]
                        self.bot.unload_extension(f'cogs.{cog}')
                        self.bot.load_extension(f'cogs.{cog}')
                        reloaded_list.append(cog)
                    except Exception as e:
                        print(e)
                        await ctx.reply(e, mention_author=False)
            await ctx.reply(f"{reloaded_list}をreloadしました", mention_author=False)
        else:
            try:
                self.bot.unload_extension(f'cogs.{cogname}')
                self.bot.load_extension(f'cogs.{cogname}')
                await ctx.reply(f"{cogname}をreloadしました", mention_author=False)
            except Exception as e:
                print(e)
                await ctx.reply(e, mention_author=False)

    @commands.command(aliases=['st'], hidden=True)
    async def status(self, ctx, word: str):
        try:
            await self.bot.change_presence(activity=discord.Game(name=word))
            await ctx.reply(f"ステータスを{word}に変更しました", mention_author=False)
        except BaseException:
            pass

    @commands.command(aliases=['p'], hidden=False, description='疎通確認')
    async def ping(self, ctx):
        """Pingによる疎通確認を行うコマンド"""
        start_time = time.time()
        mes = await ctx.reply("Pinging....")
        await mes.edit(content="pong!\n" + str(round(time.time() - start_time, 3) * 1000) + "ms")

    @commands.command(aliases=['wh'], hidden=True)
    async def where(self, ctx):
        await ctx.reply("現在入っているサーバーは以下です", mention_author=False)
        server_list = [i.name.replace('\u3000', ' ')
                       for i in ctx.bot.guilds]
        await ctx.reply(f"{server_list}", mention_author=False)

    @commands.command(aliases=['mem'], hidden=True)
    async def num_of_member(self, ctx):
        await ctx.reply(f"{ctx.guild.member_count}", mention_author=False)

    @commands.command(hidden=True)
    async def back_up(self, ctx):
        SQLite_files = [
            filename for filename in os.listdir(self.master_path + "/data")
            if filename.endswith(".sqlite")]

        my_files = [discord.File(f'{self.master_path}/data/{i}')
                    for i in SQLite_files]

        await ctx.send(files=my_files,content="back_up")

    @commands.command(hidden=True)
    async def restore_one(self, ctx):
        if ctx.message.attachments is None:
            await ctx.send('ファイルが添付されていません')

        for attachment in ctx.message.attachments:
            await attachment.save(f"{self.master_path}/data/{attachment.filename}")
            await ctx.send(f'{attachment.filename}を追加しました')

    @commands.command(hidden=True)
    async def restore(self, ctx):
        async for message in ctx.channel.history(limit=100):
            if message.author.id == self.bot.user.id:
                if len(message.attachments) != 0:
                    attachments_name = ' '.join(
                        [i.filename for i in message.attachments])
                    msg_time = message.created_at.strftime('%m-%d %H:%M')
                    await ctx.send(f'{msg_time}の{attachments_name}を取り込みます')
                    for attachment in message.attachments:
                        await attachment.save(f"{self.master_path}/data/{attachment.filename}")
                    break

    @tasks.loop(minutes=1.0)
    async def auto_backup(self):
        now = datetime.now(self.local_timezone)
        now_HM = now.strftime('%H:%M')

        if now_HM == '04:00':
            channel = self.bot.get_channel(873842519438426132)

            json_files = [
                filename for filename in os.listdir(
                    self.master_path +
                    "/data")if filename.endswith(".json")]

            sql_files = [
                filename for filename in os.listdir(
                    self.master_path +
                    "/data")if filename.endswith(".sqlite3")]

            # json_files.extend(sql_files)
            my_files = [
                discord.File(f'{self.master_path}/data/{i}')for i in sql_files]

            await channel.send(files=my_files)

    @auto_backup.before_loop
    async def before_printer(self):
        print('admin waiting...')
        await self.bot.wait_until_ready()



    @commands.command(hidden=True, name="exec")
    @commands.is_owner()
    async def _exec(self, ctx, *, script):
        script = script.removeprefix("```py").removesuffix("```")
        async with aiohttp.ClientSession() as session:
            ret[ctx.message.id] = ""

            async def get_msg(url):
                return await commands.MessageConverter().convert(ctx, url)

            def _print(*txt):
                ret[ctx.message.id] += " ".join(map(str, txt)) + "\n"
            exec(
                'async def __ex(self,_bot,_ctx,ctx,session,print,get_msg): '
                + '\n'.join(f'    {l}' for l in script.split('\n'))
            )
            r = await locals()['__ex'](self, self.bot, ctx, ctx, session, _print, get_msg)
        try:
            if ret[ctx.message.id]:
                await ctx.send(f"stdout:```py\n{str(ret[ctx.message.id])[:1980]}\n```".replace(self.bot.http.token, "[Token]"))
            if r:
                await ctx.send(f"return:```py\n{str(r)[:1980]}\n```".replace(self.bot.http.token, "[Token]"))
        except BaseException:
            pass
        await ctx.message.add_reaction("\U0001f44d")
        del ret[ctx.message.id]

    @commands.command(hidden=True, name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, script):
        await ctx.send(
            eval(script.replace("```py", "").replace("```", ""))
        )


def setup(bot):
    bot.add_cog(Admin(bot))
