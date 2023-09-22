#!/usr/bin/env python3

import discord
import re

class ParseException(Exception):
    pass

unsafe_re = re.compile(r'.*@.*[0-9]+.*')
def unsafe_mention(msg):
    return unsafe_re.match(msg) is not None

mention_id_re = re.compile(r'([0-9]+)')
def get_embeded_id(msg):
    match = mention_id_re.search(msg)
    if match is not None:
        return int(match.group())

    return None


class EventEvent():
    def __init__(self):
        self.time = None
        self.channel = None
        self.name = None
        self.location = None

    async def set_channel(self, ctx, args):
        if self.channel is not None:
            raise ParseError("Can only set the event channel once")
        self.channel, args = await  get_channel(ctx, args)
        return args

class EventParse:
    def __init__(self):
        self.options = {}
        self.channel = None
        self.message = None
        self.ping = None
        self.to_send = False
        self.debug = False
        self.pings = []
        self.event = None

    async def parse(self, ctx, args):
        while len(args) > 0:
            arg = args[0]
            args = args[1:]

            if arg == '--option':
                args = await self.get_option(ctx, args)
            elif arg == '--channel':
                args = await self.get_channel(ctx, args)
            elif arg == '--message':
                args = await self.get_message(ctx, args)
            elif arg == '--ping':
                args = await self.get_ping(ctx, args)
            elif arg == '--send':
                self.to_send = True
            elif arg == '--debug':
                self.debug = True
            elif arg == '--event':
                args = await self.get_event(ctx, args)
            else:
                raise ParseException(f"Unknown argument [{arg}]")


    async def get_event(self, ctx, args):
        if self.event is not None:
            raise ParseException(f'Can only set one event')

        self.event = EventEvent()

        while len(args) > 0:
            arg = args[0]
            args = args[1:]

            if arg == '--event-name':
                self.event.name = args[0]
                args = args[1:]
            elif arg == '--event-time':
                self.event.time = args[0]
                args = args[1:]
            elif arg == '--event-channel':
                args = await self.event.set_channel(ctx, args)
            elif arg == '--event-location':
                self.event.location = args[0]
                args == args[1:]

        if self.event.channel and self.event.location:
            raise ParseError("Can only have one of channel or location for an event")

        return args

    async def get_ping(self, ctx, args):
        id =  get_embeded_id(args[0])

        for member in ctx.guild.members:
            if member.id == id:
                self.pings.append(member)
                return args[1:]

        for role in ctx.guild.roles:
            if role.id == id:
                self.pings.append(role)
                return args[1:]

        if args[0] == '@everyone':
            raise ParseException(f"Everyone mentions are not supported")

        if args[0] == '@here':
            raise ParseException(f"Here mentions are not supported")



        raise ParseException(f"Could not find a user or role for [`{args[0]}`]")

    async def get_message(self, ctx, args):
        if self.message != None:
            raise ParseException("Message may only be set once")

        self.message = ""
        while len(args) > 0 and not args[0].startswith('--'):
            self.message += " " + args[0]
            args = args[1:]

        if unsafe_mention(self.message):
            raise ParseException("The message has mentions that I can't verify are safe. Use the --ping argument")

        self.message = self.message.strip()
        return args

    async def get_channel(self, ctx, args):
        if self.channel is not None:
            raise ParseException(f"Channel can not be set twice")

        self.channel, args = await get_channel(ctx, args)
        return args

    async def get_option(self, ctx, args):
        if len(args) < 2:
            raise ParseException("not enout arguments for option")

        opt = args[0]
        emoji = args[1]
        if opt in self.options:
            raise ParseException(f"Duplicate option for {opt}")

        self.options[opt] = emoji

        return args[2:]


async def get_channel(ctx, args):
    token = args[0].strip('<').strip('>').strip('#').strip()
    try:
        as_int = int(token)
    except ValueError:
        as_int = None

    chan = discord.utils.get(ctx.guild.channels, name=token)
    if chan is None and as_int is not None:
        chan = discord.utils.get(ctx.guild.channels, id=as_int)

    if not chan:
        raise ParseException(f"Cound not find channel for `{args[0]}`")

    return chan, args[1:]


