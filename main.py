import discord
from discord.ext import commands
import asyncio
import datetime
import config  # Импортируем файл конфигурации
from messages import Messages  # Импортируем класс с сообщениями
import os

# Настройка токена и префикса
TOKEN = config.BOT_TOKEN
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# Файлы для записи голосов
VOTE_FILE = "votes.txt"
READY_FILE = "ready.txt"

# Словари для хранения идентификаторов сообщений и голосов
POLL_MESSAGES = {}
USER_VOTES = {}

# Список разрешённых пользователей для всех команд
ALLOWED_USER_IDS = [453939184005283861]  # Замените на реальные ID пользователей

# Путь к локальной GIF-анимации
GIF_PATH = config.GIF_PATH

# Декоратор для проверки разрешений
def is_allowed_user():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id not in ALLOWED_USER_IDS:
            await interaction.response.send_message("⛔ У вас нет доступа к этой команде!", ephemeral=True)
            return False
        return True
    return discord.app_commands.check(predicate)

# Команда для создания голосований
@bot.tree.command(name="startpoll", description="Start Craft Awards polls")
@is_allowed_user()
async def start_polls(interaction: discord.Interaction):
    global POLL_MESSAGES
    POLL_MESSAGES = {}

    # Отправка вступительного сообщения с GIF-анимацией
    intro = Messages.INTRO_MESSAGE
    intro_embed = discord.Embed(title=intro["title"], description=intro["description"], color=discord.Color.gold())

    with open(GIF_PATH, "rb") as gif_file:
        gif = discord.File(gif_file, filename="animation.gif")
        intro_embed.set_image(url="attachment://animation.gif")
        await interaction.response.send_message(embed=intro_embed, file=gif)

    # Отправка сообщений для голосований
    for poll in Messages.POLL_DATA:
        await asyncio.sleep(1)

        description = poll["description"] + "\n" + "\n".join(
            [f"{emoji} **{candidate}**" for emoji, candidate in poll["candidates"].items()])
        embed = discord.Embed(title=poll["title"], description=description, color=discord.Color.blue())

        msg = await interaction.followup.send(embed=embed, wait=True)

        for emoji in poll["reactions"]:
            await msg.add_reaction(emoji)

        POLL_MESSAGES[msg.id] = {"title": poll["title"], "reactions": poll["reactions"]}

# Обработчик добавления реакции
@bot.event
async def on_raw_reaction_add(payload):
    # Игнорируем реакцию от самого бота
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = guild.get_member(payload.user_id)

    # Обработка реакции для команды /startpoll
    if payload.message_id in POLL_MESSAGES:
        allowed_reactions = POLL_MESSAGES[payload.message_id]["reactions"]

        # Проверка, если реакция не разрешена
        if payload.emoji.name not in allowed_reactions:
            await message.remove_reaction(payload.emoji, member)
            return

        # Проверка, если пользователь уже голосовал
        user_key = (payload.user_id, payload.message_id)
        if user_key in USER_VOTES:
            await message.remove_reaction(payload.emoji, member)
            return

        # Запись голоса в файл и словарь
        poll_title = POLL_MESSAGES[payload.message_id]["title"]
        emoji = payload.emoji.name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        USER_VOTES[user_key] = emoji

        with open(VOTE_FILE, "a", encoding="utf-8") as file:
            file.write(f"{poll_title} - {member.name} - {emoji} - {timestamp}\n")

        print(f"{member.name} проголосовал за {emoji} в {poll_title}")

        # Удаление реакции после записи
        await message.remove_reaction(payload.emoji, member)

# Команда для получения результатов голосования
@bot.tree.command(name="results", description="Get the voting results")
@is_allowed_user()
async def get_results(interaction: discord.Interaction):
    if not os.path.exists(VOTE_FILE):
        await interaction.response.send_message("📄 Файл с результатами голосования пуст или не существует.")
        return

    # Чтение результатов голосования
    votes = {}
    with open(VOTE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            poll_title, user_name, emoji, timestamp = line.strip().split(" - ")
            votes.setdefault(poll_title, {}).setdefault(emoji, []).append(user_name)

    # Формирование итогового сообщения
    result_message = "🏆 **Результаты голосования**\n\n"
    for poll in Messages.POLL_DATA:
        poll_title = poll["title"]
        poll_results = []

        for emoji, candidate in poll["candidates"].items():
            voter_list = votes.get(poll_title, {}).get(emoji, [])
            vote_count = len(voter_list)
            if vote_count > 0:
                voters = ", ".join(voter_list)
                poll_results.append(f"{candidate} — {vote_count} голосов ({voters})")

        if poll_results:
            result_message += f"**{poll_title}:**\n" + "\n".join(poll_results) + "\n\n"

    if result_message.strip() == "🏆 **Результаты голосования**":
        result_message += "Нет голосов, чтобы показать."

    await interaction.response.send_message(result_message[:2000])  # Убедимся, что сообщение не превышает лимит Discord


# Функция on_ready для синхронизации команд
@bot.event
async def on_ready():
    print(f"Bot {bot.user} is online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Запуск бота
bot.run(TOKEN)
