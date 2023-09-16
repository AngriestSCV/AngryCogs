#!/usr/bin/env python3

import os
import json
import re
from redbot.core import commands
import discord

# Path to the JSON file
COUNTS_FILE = "callcute_counts.json"

class CallCute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counts = self.load_counts()

    def load_counts(self):
        # Load the counts from the JSON file
        if os.path.exists(COUNTS_FILE):
            with open(COUNTS_FILE, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_counts(self):
        # Save the counts to the JSON file
        with open(COUNTS_FILE, "w") as f:
            json.dump(self.counts, f)

    @commands.command("cutie")
    async def call(self, ctx: commands.Context, user: discord.Member) -> None:
        # Check if the command is called in a server (not DMs)
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return

        if user.id == ctx.bot.user.id:
            await ctx.send("No U!")
            return

        user_id = user.id

        # Check if the username has been called before
        if user_id in self.counts:
            self.counts[user_id] += 1
        else:
            self.counts[user_id] = 1

        # Save the updated counts
        self.save_counts()

        # Send a message with the count
        await ctx.send(f"{user.mention} has been called cute {self.counts[user_id]} times.")


class Compliment: #(commands.Cog):
    """Compliment users because there's too many insults"""

    __author__ = ["Airen", "JennJenn", "TrustyJAID"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def compliment(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """
        Compliment the user

        `user` the user you would like to compliment
        """
        msg = " "
        if user:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                bot_msg: List[str] = [
                    _("Hey, I appreciate the compliment! :smile:"),
                    _("No ***YOU'RE*** awesome! :smile:"),
                ]
                await ctx.send(f"{ctx.author.mention} {choice(bot_msg)}")

            else:
                await ctx.send(user.mention + msg + choice(compliments))
        else:
            await ctx.send(ctx.message.author.mention + msg + choice(compliments))

