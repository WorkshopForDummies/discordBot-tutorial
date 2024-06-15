# discordBot-tutorial

used as part of [Tech Workshop for Dummies](https://wfd.modernneo.com)

# Setup Instructions
```bash
python -m pip install -r requirements.txt
cd discordBot/discordBot_django
python django_manage.py makemigrations
python django_manage.py migrate
cd ../
BOT_TOKEN='BOT_TOKEN' GUILD_ID='GUILD_ID' python main.py
```