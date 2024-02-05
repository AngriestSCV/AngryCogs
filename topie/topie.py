#!/usr/bin/env python3

import os
import json
import re
from redbot.core import commands
from redbot.core import Config
from red_commons.logging import getLogger

from hashlib import md5

import discord

log = getLogger("red.AngryCogs.topie")

class Topie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        name = "net.angrylabs.angrycogs.topie"
        self.config = Config.get_conf(self, identifier=md5(name.encode()).hexdigest())

        default_guild = {
            'topvotes': {},
            'bottomvotes': {},
        }
        self.config.register_guild(**default_guild)

    @commands.command("top-energy")
    async def incTop(self, ctx: command.Context, user: discord.Member) -> None:
        # Check if the command is called in a server (not DMs)
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return

        if user.id == ctx.bot.user.id:
            await ctx.send("Hell yes I am.")
            return

        if user.id == ctx.author.id:
            await ctx.send("That isn't for you to say")
            return

        user_id = str(user.id)

        cfg = self.config.guild(ctx.guild)

        votes = await vote(cfg, 'topvotes', user_id)

        # Send a message with the count
        await ctx.send(f"{user.mention} has been called top {votes} times.")


    @commands.command("bottom-energy")
    async def incTop(self, ctx: command.Context, user: discord.Member) -> None:
        # Check if the command is called in a server (not DMs)
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return

        if user.id == ctx.bot.user.id:
            await ctx.send(":3 UwU I didn't expect you to think of me that way.")
            return

        if user.id == ctx.author.id:
            await ctx.send("You sure are!")
            return

        user_id = str(user.id)

        cfg = self.config.guild(ctx.guild)

        votes = await vote(cfg, 'bottomvotes', user_id)

        # Send a message with the count
        await ctx.send(f"{user.mention} has been called bottom {votes} times.")


    async def vote(cfg, key, user_id):
        try:
            count = await cfg.get_raw('topvotes', user_id)
        except KeyError:
            count = 0

        count += 1
        await cfg.cuties.set_raw(user_id, value = count)

        return count


