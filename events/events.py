#!/usr/bin/env python3

import os
import json
import re
from redbot.core import commands
from redbot.core import Config
from red_commons.logging import getLogger
import discord, discord.ext
import typing

import argparse

from contextlib import redirect_stdout, redirect_stderr
import io

from . import eventparse

log = getLogger("red.AngryCogs.events")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=hash("net.angrylabs.angrycogs.events"))

    @commands.command("events")
    async def event_call(self, ctx, *args):
        #await ctx.send(f"Recievied {args}")
        try:
            evt = eventparse.EventParse()
            await evt.parse(ctx, args)
        except eventparse.ParseException as e:
            await ctx.send(str(e))
            return

        vote_string = ''
        for k,v in evt.options.items():
            vote_string+=f"{v} - {k}\n"
        vote_string.strip()

        if len(vote_string) > 0:
            vote_string = "\n" + vote_string

        if evt.to_send:
            target_channel = evt.channel
            preview = ''
        else:
            target_channel = ctx.channel
            preview = f"This is a preview. The real message will be sent to {evt.channel.mention} when --send is passed\n{'-'*20}\n" 

        perms = target_channel.permissions_for(ctx.author)

        pings = ' - '.join([ x.mention for x in evt.pings] )

        eventMessage = ""
        if evt.event is not None:
            if not perms.manage_events:
                await ctx.send("You can not create events, aborting")
                return

            if not evt.to_send:  eventMessage = "Not creating event for unsent message"
            else:
                discord_event = await ctx.guild.create_scheduled_event(
                        name=evt.event.name,
                        start_time = evt.event.time,
                        channel=evt.event.channel,
                        location = evt.event.channel)
                eventMessage = f"Event link: {discord_event.url}"


        msg = f'''
{preview}
{pings}
{ctx.author.mention} has an announcement!

{evt.message}
{eventMessage}
{vote_string}
'''.strip()

        if evt.debug:
            msg += f"\n```{evt.message}```"

        discord_message = await target_channel.send(msg)

        for k,v in evt.options.items():
            await discord_message.add_reaction(v)

