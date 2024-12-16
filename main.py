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

# Файлы для записи голосов и подтверждений участия
VOTE_FILE = "votes.txt"
READY_FILE = "ready.txt"

# Название реакции для команды /msg
REACTION_NAME = "<:84734leolookatthat:1282124163255111763>"

# Словарь для хранения идентификаторов сообщений с реакциями и их разрешёнными реакциями
POLL_MESSAGES = {}
MSG_REACTIONS = {}

# Словарь для хранения информации о голосах пользователей
USER_VOTES = {}

# Список разрешённых пользователей для всех команд
ALLOWED_USER_IDS = [453939184005283861, 530700163090612235]  # Замените на реальные ID пользователей

# ID канала, куда будет отправляться сообщение с командой /msg
ALLOWED_CHANNEL_ID = 1317917924006301696

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

        # Создание Embed с оформлением
        description = poll["description"] + "\n" + "\n".join(
            [f"{emoji} **{candidate}**" for emoji, candidate in poll["candidates"].items()])
        embed = discord.Embed(title=poll["title"], description=description, color=discord.Color.blue())

        msg = await interaction.followup.send(embed=embed, wait=True)

        for emoji in poll["reactions"]:
            await msg.add_reaction(emoji)

        POLL_MESSAGES[msg.id] = {"title": poll["title"], "reactions": poll["reactions"]}


# Команда для отправки ознакомительного сообщения
@bot.tree.command(name="msg", description="Send an announcement message for Craft Awards participation")
@is_allowed_user()
async def send_announcement(interaction: discord.Interaction):
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message("⛔ Команду можно использовать только в разрешённом канале!", ephemeral=True)
        return

    # Текст сообщения
    announcement = (
        "🎉 **Craft Awards приближаются!** 🎉\n\n"
        "🔥 **Готовы стать частью самого яркого события года?** 🔥\n\n"
        "🏆 Примите участие в нашем ежегодном мероприятии и поборитесь за звание **лучших из лучших** в сообществе! 🌟\n\n"
        "🗳️ **Как участвовать?**\n"
        "Поставьте реакцию под этим сообщением, чтобы подтвердить своё участие! 🤩\n\n"
        "⚠️ **Важно!**\n"
        "Нажав на реакцию **один раз**, вы подтверждаете своё участие. Изменить решение уже **нельзя**! 🚫\n\n"
        "✨ Не упустите шанс войти в историю Craft Awards! ЙОУ✨"
    )

    # Отправка сообщения
    await interaction.response.send_message(announcement)
    msg = await interaction.original_response()

    # Добавление реакции
    await msg.add_reaction(REACTION_NAME)

    # Сохранение сообщения для отслеживания реакций
    MSG_REACTIONS[msg.id] = True


# Команда для получения списка участников из файла ready.txt
@bot.tree.command(name="msgres", description="Get the list of participants")
@is_allowed_user()
async def get_participants(interaction: discord.Interaction):
    if not os.path.exists(READY_FILE):
        await interaction.response.send_message("📄 Файл с участниками пуст или не существует.")
        return

    with open(READY_FILE, "r", encoding="utf-8") as file:
        participants = file.read().strip()

    if not participants:
        await interaction.response.send_message("📄 В списке участников пока никого нет.")
        return

    embed = discord.Embed(title="✅ Список участников Craft Awards", description=participants, color=discord.Color.green())
    await interaction.response.send_message(embed=embed)


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

    # Формирование и отправка сообщения с результатами
    embed = discord.Embed(title="🏆 Результаты голосования", color=discord.Color.green())

    for poll in Messages.POLL_DATA:
        poll_title = poll["title"]
        embed.add_field(name=f"**{poll_title}**", value="", inline=False)

        for emoji, candidate in poll["candidates"].items():
            voter_list = votes.get(poll_title, {}).get(emoji, [])
            vote_count = len(voter_list)
            voters = ", ".join(voter_list) if voter_list else "()"
            embed.add_field(name=f"{candidate} — {vote_count} голосов", value=f"{voters}", inline=False)

    await interaction.response.send_message(embed=embed)

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

    # Обработка реакции для команды /msg
    if payload.message_id in MSG_REACTIONS:
        # Проверка, что пользователь ещё не записан в файл
        if not os.path.exists(READY_FILE):
            open(READY_FILE, "w").close()

        with open(READY_FILE, "r", encoding="utf-8") as file:
            participants = file.read().splitlines()

        if member.name not in participants:
            # Записываем ник пользователя в файл
            with open(READY_FILE, "a", encoding="utf-8") as file:
                file.write(f"{member.name}\n")
            print(f"{member.name} подтвердил участие")

        # Удаление реакции после записи
        await message.remove_reaction(payload.emoji, member)


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
