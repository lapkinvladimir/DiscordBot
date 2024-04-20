import discord
from interactions.api.http import interaction

import config
from discord.ext import commands
import random
import wikipedia

intents = discord.Intents.all()
intents.members = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)


# Просто начало, тут ошибок нет
@bot.event
async def on_ready():
    print(f"Бот {bot.user} в сети!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced tree: {len(synced)} commands")
    except Exception as e:
        print(e)


# TODO: Доделать исключения что бы 2 число было больше первого и мб еще что то
@bot.tree.command(name="random", description="Дает рандомное число в вашем диапозоне", )
async def random_num(interaction: discord.Interaction, first_num: int, second_num: int):
    if second_num <= first_num:
        await interaction.response.send_message("Ошибка: Второе число должно быть больше первого.")
        return
    random_number = random.randint(first_num, second_num)
    await interaction.response.send_message(f"Твое число это {random_number}")


# Тут думаю уже никак не пофиксить, разве что фул переписать код из какого то видео
# А так нормик, некоторые норм запросы(Microsoft, Ukraine, America)
@bot.tree.command(name="wiki", description="Поиск информации в Википедии")
async def wiki_search(interaction: discord.Interaction, query: str):
    page = wikipedia.page(query)
    sentences = page.content.split(". ")  # Разделение текста на предложения
    selected_sentences = ". ".join(sentences[:3])  # Выбор первых трех предложений
    search = discord.Embed(title=query, description=selected_sentences, color=discord.Color.purple())
    await interaction.response.send_message(embed=search)


# Роли работает, все убирается и ставится (только ты хотел сделать что бы он сам писал сообщение, а получается по айди, ну ладно)
@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    if message_id == config.MESSAGE_ROLE_REACTION:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)

        for emoji, role_id in config.ROLES_LIST.items():
            if payload.emoji.name == emoji:
                role = discord.utils.get(guild.roles, id=role_id)
                break
        else:
            role = None

    if role is not None:
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        if member is not None:
            await member.add_roles(role)
        else:
            print("Member not found")
    else:
        print("Role not found")


@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    if message_id == config.MESSAGE_ROLE_REACTION:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)

        for emoji, role_id in config.ROLES_LIST.items():
            if payload.emoji.name == emoji:
                role = discord.utils.get(guild.roles, id=role_id)
                break
        else:
            role = None

    if role is not None:
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        if member is not None:
            await member.remove_roles(role)
        else:
            print("Member not found")
    else:
        print("Role not found")



# Готово, получает аватарку пользователя
@bot.tree.command(name="avatar", description="Получить аватарку пользователя")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=member)
    embed.set_image(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)





bot.run(config.BOT_TOKEN)
