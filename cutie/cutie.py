#!/usr/bin/env python3

import os
import json
import re
from redbot.core import commands
from redbot.core import Config
from red_commons.logging import getLogger

import discord

log = getLogger("red.AngryCogs.cutie")

class CallCute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=hash("net.angrylabs.angrycogs.cutie"))

        default_guild = {
            'cuties': {},
        }
        self.config.register_guild(**default_guild)

    @commands.command("cutie")
    async def call(self, ctx: commands.Context, user: discord.Member) -> None:
        # Check if the command is called in a server (not DMs)
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return

        if user.id == ctx.bot.user.id:
            await ctx.send("No U!")
            return

        user_id = str(user.id)

        cfg = self.config.guild(ctx.guild)

        try:
            count = await cfg.get_raw('cuties', user_id)
        except KeyError:
            count = 0

        count += 1

        # Send a message with the count
        await ctx.send(f"{user.mention} has been called cute {count} times.")

        # Save the updated counts
        await cfg.cuties.set_raw(user_id, value = count)
