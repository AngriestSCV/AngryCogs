#!/usr/bin/env python3

import os
import json
import re
from redbot.core import commands
from redbot.core import Config
from red_commons.logging import getLogger

from hashlib import md5

import discord
from discord.ext import tasks

import datetime

breederTime = datetime.time(hour=0, minute=8)

cog_name = "net.angrylabs.angrycogs.breeder"

logger = getLogger(cog_name)

bottomKey = "bottomVotes"
topKey = "topVotes"

class Breeder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        global cog_name
        name = cog_name
        self.config = Config.get_conf(self, identifier=md5(name.encode()).hexdigest())

        default_guild = {
            topKey: {},
            bottomKey: {},
            "breeder_channel": None,
        }
        self.config.register_guild(**default_guild)


    @commands.command("top-energy")
    @commands.guild_only()
    async def incTop(self, ctx: commands.Context, user: discord.Member) -> None:
        if user.id == ctx.bot.user.id:
            await ctx.send("Hell yes I am.")
            return

        if user.id == ctx.author.id:
            await ctx.send("Sure you are ;p")
            return

        user_id = str(user.id)

        cfg = self.config.guild(ctx.guild)

        await self.vote(cfg, topKey, user_id)

        # Send a message with the count
        await ctx.send(f"{user.mention} gained a topping point")


    @commands.command("bottom-energy")
    @commands.guild_only()
    async def incBottom(self, ctx: commands.Context, user: discord.Member) -> None:
        if user.id == ctx.bot.user.id:
            await ctx.send(":3 UwU")
            return

        if user.id == ctx.author.id:
            await ctx.send("You sure are!")
            return

        user_id = str(user.id)

        cfg = self.config.guild(ctx.guild)

        await self.vote(cfg, bottomKey, user_id)

        # Send a message with the count
        await ctx.send(f"{user.mention} has been asigned a bottom point")


    async def vote(self, cfg, key, user_id):
        try:
            count = await cfg.get_raw(key, user_id)
        except KeyError:
            count = 0

        count += 1

        table = cfg.__getattr__(key)
        await table.set_raw(user_id, value = count)

        return count

    async def most_votes(self, cfg, key):
        table = cfg.__getattr__(key)

        high = 0
        high_key = None

        tt  = await table.all()
        for k,v in tt.items():
            if v > high:
                high_key = set()
                high_key.add(k)
                high = v
            elif v == high:
                high_key.add(k)

        return high_key

    @commands.group("breeder")
    async def breeder(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send('Well you sure are horny aren\'t you ;p')

    @commands.guild_only()
    @breeder.command(name="board")
    async def single_breeder_board(self, ctx: commands.Context) -> None:
        cfg = self.config.guild(ctx.guild)
        guild_id = ctx.guild.id

        message = await self.breeder_board_message(ctx, guild_id)
        if len(message) == 0:
            await ctx.send("We need more votes!")
        else:
            await ctx.send(message)

    async def breeder_board_message(self, ctx: commands.Context, guild_id) -> None:
        cfg = self.config.guild_from_id(guild_id)
        tt = await self.most_votes(cfg, topKey)
        tb = await self.most_votes(cfg, bottomKey)

        message = ""
        if tt is not None:
            if len(tt) > 0:
                message += "Top report:\n"
            for member in tt:
                user = await ctx.guild.fetch_member(member)
                message += f"{user.mention} has been displaying serious top energy\n"
            if len(tt) > 0:
                message += "\n"

        if tb is not None:
            if len(tb) > 0:
                message += "Bottom report:\n"
            for member in tb:
                user = await ctx.guild.fetch_member(member)
                message += f"{user.mention} has been displaying serious bottom energy\n"
            if len(tb) > 0:
                message += "\n"

        return message

    @commands.is_owner()
    @commands.guild_only()
    @breeder.command(name="set-channel")
    async def set_breeder_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        cfg = self.config.guild(ctx.guild)
        await cfg.breeder_channel.set(channel.id)

        aaa = await cfg.breeder_channel()
        await ctx.send(f"Channel set {aaa}")

    async def all_breeder_board(self, ctx: commands.Context) -> None:
        guilds = await self.config.all_guilds()

        for guild_id, data in guilds.items():
            guild = self.bot.get_guild(guild_id)
            guild_id = ctx.guild.id
            #await ctx.send(f"Processing: {guild}")
            cfg = self.config.guild(guild)
            channel_id = await cfg.breeder_channel()

            channel = self.bot.get_channel(channel_id)
            #await ctx.send(f"Channel: {channel}")

            if channel_id is None:
                logger.info(f"Failed to find channel for guild {guild}")
                continue

            message = await self.breeder_board_message(ctx, guild_id)
            if len(message) > 0:
                await channel.send(message)

    @commands.is_owner()
    @commands.guild_only()
    @breeder.command(name="reset")
    async def breeder_reset(self, ctx: commands.Context) -> None:
        guilds = await self.config.all_guilds()
        for guild_id, data in guilds.items():
            guild_config = self.config.guild_from_id(guild_id)

            await guild_config.clear_raw(topKey)
            await guild_config.clear_raw(bottomKey)

    @commands.guild_only()
    @breeder.command(name="test")
    async def breeder_tick_test(self, ctx):
        await self.breeder_tick(ctx)

    @tasks.loop(time=breederTime)
    async def breeder_tick(self, ctx: commands.Context) -> None:

        if ctx.message is not None:
            await ctx.send("running breeder test in debug\n------")
        elif datetime.datetime.today().day != 1:
            return

        await self.all_breeder_board(ctx)

        if ctx.message is None:
            await self.breeder_reset(ctx)
        else:
            await ctx.send("--------\nSkipping reset due to testing")
