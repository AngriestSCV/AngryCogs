#!/usr/bin/env python3
import os, sys

from . import topie

async def setup(bot):
    await bot.add_cog(topie.Topie(bot))
