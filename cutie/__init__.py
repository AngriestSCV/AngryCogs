#!/usr/bin/env python3
import os, sys

from . import cutie

async def setup(bot):
    await bot.add_cog(cutie.CallCute(bot))
