#!/usr/bin/env python3

import os
import json
import re
from redbot.core import commands
from redbot.core import Config
from red_commons.logging import getLogger
import sqlite3

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

    def build_query_db(self):
        db = sqlite3.connect(":memory:")
        #db = sqlite3.connect("/tmp/aaa.db")
        with db:
            db.execute('create table if not exists points (user, top, bot);')
            db.execute('delete from points;')
            db.commit()
        return db

    async def add_to_query_db(self, cfg, db: sqlite3.Connection, key):
        table = cfg.__getattr__(key)

        tt = await table.all()
        with db:
            for k,v in tt.items():
                if key == topKey:
                    kt = "top"
                elif key == bottomKey:
                    kt = 'bot'
                else:
                    raise Exception("Can not turn {key} into a table key")
                db.execute(f'insert into points (user, {kt}) values (?, ?);', (k, v))

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

    def get_message_report(self, db: sqlite3.Connection):
        res = db.execute('select sum(top) + sum(bot) from points;').fetchone()[0]

        votes_str = db.execute('select coalesce(sum(top), 0) + coalesce(sum(bot), 0) from points;').fetchone()[0]
        votes = int(votes_str)

        if votes == 0:
            return ""

        return f"With a total of {votes} votes we have some results!"

    async def get_top_message(self, ctx: commands.Context, db: sqlite3.Connection):
        res = db.execute('''
                        with topCounts as (
                            select distinct top high from points where top > 0 order by top desc limit 3
                        )
                        select user, top 
                        from points
                        join topCounts on high = top 
                        order by top desc;
                        ''').fetchall()

        if len(res) == 0:
            return "Odd. We can't seem to find a top here."

        lines = ["Our topmost tops are on fire"]
        for uid, top in res:
            uid = int(uid)
            top = int(top)
            user = await ctx.guild.fetch_member(uid)
            if user is None: 
                continue
            lines.append(f'{user.mention}: Score {top}')
        return "\n".join(lines).strip()

    async def get_bottom_message(self, ctx: commands.Context, db: sqlite3.Connection):
        res = db.execute('''
                        with botCounts as (
                            select distinct bot low from points where bot > 0 order by bot desc limit 3
                        )
                        select user, bot 
                        from points
                        join botCounts on low = bot 
                        order by bot desc;
                        ''').fetchall()

        if len(res) == 0:
            return ""

        lines = ["Our biggest bottoms have really been working 'it'"]
        for uid, bot in res:
            uid = int(uid)
            bot = int(bot)
            user = await ctx.guild.fetch_member(uid)
            if user is None: 
                continue
            lines.append(f'{user.mention}: Score {bot}')
        return "\n".join(lines).strip()

    async def breeder_board_message(self, ctx: commands.Context, guild_id) -> None:
        cfg = self.config.guild_from_id(guild_id)
        db = self.build_query_db()
        await self.add_to_query_db(cfg, db, topKey)
        await self.add_to_query_db(cfg, db, bottomKey)

        vote_message = self.get_message_report(db)

        if len(vote_message) == 0:
            return ""

        top_message = await self.get_top_message(ctx, db)
        bottom_message = await self.get_bottom_message(ctx, db)

        message = "\n\n".join([
            vote_message,
            top_message,
            bottom_message
            ]).strip()

        return message

    @commands.is_owner()
    @commands.guild_only()
    @breeder.command(name="set-channel")
    async def set_breeder_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        cfg = self.config.guild(ctx.guild)
        await cfg.breeder_channel.set(channel.id)
        self.get_breeder_channel(ctx)

    @commands.is_owner()
    @commands.guild_only()
    @breeder.command(name='get-channel')
    async def get_breeder_channel(self, ctx: commands.Context):
        cfg = self.config.guild(ctx.guild)
        channel_id = await cfg.breeder_channel()
        await ctx.send(f"Channel id: {channel_id}")
        if channel_id is None:
            return

        channel = self.bot.get_channel(channel_id)
        await ctx.send(f"Channel mention: {channel.mention}")

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
    @commands.is_owner()
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

