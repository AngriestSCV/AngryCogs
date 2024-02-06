#!/usr/bin/env python3
import os, sys

from . import breeder

async def setup(bot):
    await bot.add_cog(breeder.Breeder(bot))
