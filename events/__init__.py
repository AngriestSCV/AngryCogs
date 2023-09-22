#!/usr/bin/env python3
import os, sys

from . import events

async def setup(bot):
    await bot.add_cog(events.Events(bot))
