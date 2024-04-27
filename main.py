import discord
from disnake.ext.commands import params

import config
from discord.ext import commands
import random
import wikipedia
import aiohttp

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



#работает погода (максимум добавить исключение нормальное если город не найден)
@bot.tree.command(name="weather", description="Узнать погоду по городу")
async def weather(interaction: discord.Interaction, city: str):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": config.WEATHER_API,
        "q": city
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as res:
            data = await res.json()

    location = data["location"]["name"]
    temp_c = data["current"]["temp_c"]
    temp_f = data["current"]["temp_f"]
    humidity = data["current"]["humidity"]
    wind_kph = data["current"]["wind_kph"]
    wind_mph = data["current"]["wind_mph"]
    condition = data["current"]["condition"]["text"]
    image_url = "http:" + data["current"]["condition"]["icon"]

    embed = discord.Embed(title=f"Weather for {location}", description=f"The condition in `{location}` is `{condition}`")
    embed.add_field(name="Temperature", value=f"C: {temp_c} | F: {temp_f}")
    embed.add_field(name="Humidity", value=f"{humidity}")
    embed.add_field(name="Wind Speeds", value=f"KPH: {wind_kph} | MPH: {wind_mph}")
    embed.set_thumbnail(url=image_url)

    await interaction.response.send_message(embed=embed)



bot.run(config.BOT_TOKEN)
