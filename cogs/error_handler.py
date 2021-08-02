import sys
import traceback
import logging

from discord.ext import commands
import discord


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def autodel_msg(msg: discord.Message, second: int = 5):
        """渡されたメッセージを指定秒数後に削除する関数

        Args:
            msg (discord.Message): 削除するメッセージオブジェクト
            second (int, optional): 秒数. Defaults to 5.
        """
        try:
            await msg.delete(delay=second)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):  # ローカルのハンドリングがあるコマンドは除く
            return

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.DisabledCommand):
            msg = await ctx.reply(f'{ctx.command} has been disabled.')
            await self.autodel_msg(msg)
            return

        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(f'you have no permission to execute {ctx.command}.')
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.reply(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                print("couldn't send direct message")

        elif isinstance(error, commands.BadArgument):
            msg = await ctx.reply("無効な引数です")
            await self.autodel_msg(msg)

        elif isinstance(error, commands.MissingRequiredArgument):
            msg = await ctx.reply("引数が足りません")
            await self.autodel_msg(msg)

        else:
            error = getattr(error, 'original', error)
            print(
                'Ignoring exception in command {}:'.format(
                    ctx.command),
                file=sys.stderr)
            traceback.print_exception(
                type(error),
                error,
                error.__traceback__,
                file=sys.stderr)
            error_content = f'error content: {error}\nmessage_content: {ctx.message.content}\nmessage_author : {ctx.message.author}\n{ctx.message.jump_url}'

            logging.error(error_content, exc_info=True)
            server = self.bot.get_guild(747714295382540305)
            ch = 833070882133508186
            embed = discord.Embed(title="エラー情報", description="", color=0xf00)
            embed.add_field(name="サーバー名", value=ctx.guild.name, inline=False)
            embed.add_field(name="サーバーID", value=ctx.guild.id, inline=False)
            embed.add_field(name="ユーザー名", value=ctx.author.name, inline=False)
            embed.add_field(name="ユーザーID", value=ctx.author.id, inline=False)
            embed.add_field(name="コマンド", value=ctx.message.content, inline=False)
            embed.add_field(name="発生エラー", value=error_content, inline=False)
            m = await server.get_channel(ch).send(embed=embed)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
