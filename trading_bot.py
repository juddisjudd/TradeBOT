import discord
from discord.ext import commands
import asyncio
import json
import os
import time

intents = discord.Intents.all()
intents.reactions = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

RATE_COOLDOWN = 1800  # 30 minutes in seconds
reputation_data = {}

if os.path.exists("reputation_data.json"):
    with open("reputation_data.json", "r") as f:
        reputation_data = json.load(f)


def save_reputation_data():
    with open("reputation_data.json", "w") as f:
        json.dump(reputation_data, f)


@bot.command()
async def starttrade(ctx, member: discord.Member):
    def check(reaction, user):
        return user == member and str(reaction.emoji) in ['👍', '👎']

    message = await ctx.send(f"{member.mention}, would you like to trade with {ctx.author.mention}? React with 👍 to accept or 👎 to decline.")
    await message.add_reaction('👍')
    await message.add_reaction('👎')

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Trade request timed out.")
    else:
        if str(reaction.emoji) == '👍':
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
                member: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await ctx.guild.create_text_channel(f'trade-{ctx.author.name}-{member.name}', overwrites=overwrites)
            await channel.send(f"Both parties have agreed to trade. {ctx.author.mention} and {member.mention}, please respond with !complete to complete the trade when finished.")
        else:
            await ctx.send("Trade request declined.")

@bot.command()
async def complete(ctx):
    if ctx.channel.id not in trading_channels:
        await ctx.send("This is not a trading channel.")
        return

    trading_channels[ctx.channel.id]["completed"].add(ctx.author.id)

    if trading_channels[ctx.channel.id]["user1"].id in trading_channels[ctx.channel.id]["completed"] and trading_channels[ctx.channel.id]["user2"].id in trading_channels[ctx.channel.id]["completed"]:
        rated_user = trading_channels[ctx.channel.id]["user1"] if trading_channels[ctx.channel.id]["user1"].id != ctx.author.id else trading_channels[ctx.channel.id]["user2"]
        msg = await ctx.send(f"{ctx.author.mention}, please rate {rated_user.mention} using !rate command. Example: !rate @ExampleUser")

        del trading_channels[ctx.channel.id]
        await ctx.channel.delete()
    else:
        await ctx.send(f"{ctx.author.mention}, waiting for the other user to complete the trade.")

@bot.command()
async def rate(ctx, user: discord.Member):
    await ctx.message.delete()  # Delete the command message

    author_id = str(ctx.author.id)
    user_id = str(user.id)

    if author_id == user_id:
        await ctx.send("You can't rate yourself.")
        return

    now = time.time()

    if author_id not in reputation_data:
        reputation_data[author_id] = {
            "ratings": {}
        }
    else:
        if user_id in reputation_data[author_id]["ratings"]:
            last_rated = reputation_data[author_id]["ratings"][user_id]["last_rated"]
            if now - last_rated < RATE_COOLDOWN:
                remaining_time = int((RATE_COOLDOWN - (now - last_rated)) / 60)
                await ctx.send(f'{ctx.author.mention}, you can rate {user.mention} again in {remaining_time} minutes.')
                return

    if user_id not in reputation_data[author_id]["ratings"]:
        reputation_data[author_id]["ratings"][user_id] = {
            "thumbsup": 0,
            "thumbsdown": 0,
            "last_rated": now
        }
    else:
        reputation_data[author_id]["ratings"][user_id]["last_rated"] = now

    rating_message = await ctx.send(f"Please rate {user.mention} with either a 👍 or 👎")
    await rating_message.add_reaction("👍")
    await rating_message.add_reaction("👎")

    def check(reaction, member):
        return member == ctx.author and reaction.message.id == rating_message.id and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, rating timed out.")  # Mention the user
        return

    if str(reaction.emoji) == "👍":
        reputation_data[author_id]["ratings"][user_id]["thumbsup"] += 1
    elif str(reaction.emoji) == "👎":
        reputation_data[author_id]["ratings"][user_id]["thumbsdown"] += 1

    save_reputation_data()
    await ctx.send(f"{ctx.author.mention}, thanks for rating {user.mention}!")  # Mention the user


@bot.command()
async def check(ctx, user: discord.Member):
    await ctx.message.delete()  # Delete the command message

    user_id = str(user.id)
    thumbs_up = 0
    thumbs_down = 0

    for author_id in reputation_data:
        if user_id in reputation_data[author_id]["ratings"]:
            thumbs_up += reputation_data[author_id]["ratings"][user_id]["thumbsup"]
            thumbs_down += reputation_data[author_id]["ratings"][user_id]["thumbsdown"]

    await ctx.send(f"{ctx.author.mention}, {user.mention} has received {thumbs_up} 👍 and {thumbs_down} 👎")  # Mention the user

bot.run("your-bot-token")
