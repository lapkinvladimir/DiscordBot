import discord
import config
from discord.ext import commands
import random
import wikipedia

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix='/', intents=intents)

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







@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == config.ID_POST:
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = message.guild.get_member(payload.user_id)
        emoji = str(payload.emoji)

        try:
            role = message.guild.get_role(config.ROLES_LIST[emoji])

            if len([i for i in user.roles if i.id not in config.USER_ROLES_LIST]) <= config.MAX_ROLES:
                await user.add_roles(role)
                print(f"{user.name} получил роль {role.name}")
            else:
                await message.remove_reaction(payload.emoji, user)
                print(f"Ошибка! пользователь {user.name} пытался получить слишком много ролей")

        except Exception as _ex:
            print(repr(_ex))

@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = message.guild.get_member(payload.user_id)

    try:
        emoji = str(payload.emoji)
        role = message.guild.get_role(config.ROLES_LIST[emoji])
        await user.remove_roles(role)
    except Exception as _ex:
        print(repr(_ex))




bot.run(config.BOT_TOKEN)
