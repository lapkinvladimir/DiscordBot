# 🚀 Python Discord Bot  

A multifunctional Discord bot built with **Python** to enhance server interaction through automated tasks, API integrations, and role management.  

## 🔧 Features  

- **🌐 Google Image Search** – Quickly find images within the chat using Google API.  
- **⛅ Real-Time Weather Updates** – Fetch live weather data based on user requests.  
- **🎭 Reaction-Based Role Assignment** – Automate role management and improve user engagement.  
- **⚡ Automated Tasks** – Streamline various server operations with custom commands.  

## 🛠️ Tech Stack  

- **Language**: Python  
- **Libraries**: `discord.py`, `requests`, `google-api-python-client`  
- **APIs**: Google Search API, OpenWeather API  
- **Database (Optional)**: SQLite / PostgreSQL  

## 🚀 Installation  

1. Clone this repository:  
   sh
   git clone https://github.com/yourusername/python-discord-bot.git
   cd python-discord-bot
   
2. Install dependencies:
   pip install -r requirements.txt
   
3. Set up your .env file:
   DISCORD_TOKEN=your_discord_bot_token
   GOOGLE_API_KEY=your_google_api_key
   WEATHER_API_KEY=your_weather_api_key
   
4. Run the bot:
   python bot.py


## ⚙️ Commands

- **!image <query>**   # Searches for an image using Google API
- **!weather <city>**  # Fetches real-time weather updates
- **!role <emoji>**    # Assigns a role based on reaction
- **!help**            # Displays the available commands


📝 License
MIT License - Feel free to use and modify this project
