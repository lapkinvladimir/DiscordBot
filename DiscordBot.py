import datetime

import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
intents.guilds = True
intents.reactions = True


bot = commands.Bot(command_prefix='!', intents=intents)


# @bot.event
# async def on_member_join(member):
#     print(f"{member} has joined the server")
#     channel = bot.get_channel(1227981399974477926)
#     embed = disnake.Embed(
#         description=f"Welcome **{member.name}** to the server!",
#         color=0xff55ff,
#         timestamp=datetime.datetime.now()
#     )
#     await channel.send(embed=embed)

# @bot.slash_command()
# async def hello(ctx):
#     await ctx.send("Hello, World!")
#
#
# @bot.event
# async def on_member_join(member):
#     try:
#         print(f"{member} has joined the server")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
#
# @bot.event
# async def on_member_remove(member):
#     try:
#         print(f"{member} has left the server")
#     except Exception as e:
#         print(f"An error occurred: {e}")


# не работает ну хоть убейте


@bot.event
async def on_ready():
    print("Im ready")




@bot.slash_command()
async def welcome(ctx):
    guild = ctx.guild
    guild_name = guild.name
    channel_id = 1227956682219454485
    channel = bot.get_channel(channel_id)
    message = await channel.send(f"\n"
                                 f"**Welcome to the server, {guild_name}!**\n\n"
                                 f"You can click on the emojis below to get the corresponding roles:\n\n"
                                 f"> :blue_heart: <@&1227959634342580385>\n\n"
                                 f"> :green_heart: <@&1227959710905532530>\n\n"
                                 f"> :yellow_heart: <@&1227959730043883652>\n\n"
                                 f"> :purple_heart: <@&1227959756031918122>\n\n"
                                 f"> :heart: <@&1227959773962436678>\n")

    emojis = ["💙", "💚", "💛", "💜", "❤️"]
    for emoji in emojis:
        await message.add_reaction(emoji)




bot.run("MTE2MjgzNDcwMzYzNjc2Njg5MQ.G8CNDX.7WEftXfFyJluaEBqAzkRSjrp6A7L92WU_vwlmA")
