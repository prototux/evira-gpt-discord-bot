import discord
import requests
import yaml
import random
from discord.ext import commands

# Load config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Define Intents
intents = discord.Intents.default()
intents.messages = True  # Enables receiving messages
intents.message_content = True  # Enables content of messages

# Initialize the Discord client with intents
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

# Function to construct the conversation context
def construct_context():
    context_parts = ['Personality: '+config['context']]
    if 'languages' in config and config['languages']:
        context_parts.append(f"Languages often discussed: {', '.join(config['languages'])}.")
    if 'topics' in config and config['topics']:
        context_parts.append(f"Common topics include: {', '.join(config['topics'])}.")
    return ' '.join(context_parts)

def get_openai_response(messages):
    headers = {
        'Authorization': f'Bearer {config["openai_api_key"]}',
        'Content-Type': 'application/json'
    }

    chat_messages = [] if config.get('context_add', False) else [{'role': config.get('context_type', 'system'), 'content': construct_context()}]
    chat_messages += [{"role": "assistant" if msg.author == bot.user else "user", "content": msg.clean_content} for msg in messages]

    data = {
        'messages': chat_messages,
        'model': config['openai_model'],
        'max_tokens': 1000
    }

    response = requests.post(f'{config["openai_api_url"]}/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content'].strip()
    else:
        return config.get('error_msg', 'Sorry, there was an error generating the response')

# Helper function to gather messages in the reply chain
async def gather_reply_chain(message):
    chain = []
    while message is not None:
        chain.append(message)
        message = await message.channel.fetch_message(message.reference.message_id) if message.reference else None
    return list(reversed(chain))

# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Command to interact with OpenAI
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    reply_chain = []
    if bot.user.mentioned_in(message):
        if message.reference:
            reply_chain = await gather_reply_chain(message.reference.resolved)

        # Generate the AI response
        async with message.channel.typing():
            ai_response = get_openai_response(reply_chain + [message])

        try:
            await message.reply(ai_response)
        except:
            print('cannot send message!')

bot.run(config['discord_token'])
