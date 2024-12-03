import discord # type: ignore
from discord import Interaction # type: ignore
from discord.ext import commands # type: ignore
import asyncio
import os
from dotenv import load_dotenv # type: ignore
import random
import time
import sys
import json
import sqlite3
from discord.ext.commands import BucketType, cooldown # type: ignore

#Main ideas
#Connect it to git/github
#Try to make daily changes on it

load_dotenv()
TOKEN: str = os.getenv("TOKEN") # Loads the token from the .enc file

bot_intents = discord.Intents.default()
bot_intents.message_content = True

client = commands.Bot(command_prefix = '.', intents = bot_intents, help_command = None) # Command prefix for the commands, Also disables the original help command

start_time = time.time() # Records the time when the bots starts (For the uptime command)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Over the guild")) # Sets the bot's status
    print(f'{client.user} is now running!') # Lets me know the bot is running correctly.

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("""Sorry that's a unknown command. Try .help to look at the known commands""")

@client.command() # Command to get the bot's ping
async def ping(ctx):
    print("Ping called")
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command() # command to get all the current bot's commands
async def help(ctx):
    help_message = """
    Here are some commands you can use:
    ".ping" - To check the bot's latency.
    ".hello" - To greet the bot.
    ".joke" - To get a joke from the bot.
    ".status" - To check how long the bot has been up.
    ".cf" - To do a coinflip!
    ".rps" - Rock, Paper, Scissors
    """
    await ctx.send(help_message)

@client.command() # command to make the bot say hello
async def hello(ctx):
    await ctx.send(f'Hello! {ctx.author.name}. My name is Jimbo :)')

@client.command() # command to make the bot tell a joke
async def joke(ctx):
    jokes = [
        "What did the cat say when he lost all his money? I’m paw!",
        "What did the alien say to the cat? “Take me to your litter.”",
        "Did you hear about the cat who swallowed a ball of wool? She had mittens.",
        "What does the lion say to his friends before they go out hunting for food? “Let us prey.”"
    ]
    jokes = random.choice(jokes)
    await ctx.send(jokes)

@client.command() # Command to tell some basic info
async def info(ctx):
    info_message = """
    Hello my name is Guildmaster Jimbo!
I'm a developers guild project bot.
and im made by: Nuriho"""
    await ctx.send(info_message)

@client.command() # Status command with uptime, name and if of bot, and the count of how man servers the bot is in a d how many members in total the servers have
async def status(ctx):

    # Getting the basic bot info
    bot_name = client.user.name
    bot_id = client.user.id

    # Calculates the bots uptime since i tarted it.
    uptime_second = time.time() - start_time
    days = int(uptime_second // (24 * 3600)) # Uptime divided by 24*3600 or 86400 seconds
    hours = int(uptime_second % (24 * 3600) // 3600) # The rest is divided by 3600 seconds
    minutes = int((uptime_second % 3600) // 60) # What ever is left over gets divided by 60 seconds
    seconds = int(uptime_second % 60) # Than displays how many seconds were left.

    # Getting the amount of servers its in and the member counts of them
    server_count = len(client.guilds)
    member_count = sum(guild.member_count for guild in client.guilds)

    # String to display uptime
    uptime_string = f'{days} Days, {hours} Hours, {minutes} Minutes, and {seconds} Seconds!'

    status_message = f"**Name:** {bot_name} (ID: {bot_id})\n" \
                     f"**Uptime:** {uptime_string}\n" \
                     f"**Servers:** {server_count}\n" \
                     f"**Members:** {member_count}"

    await ctx.send(status_message)

@client.command() # Coinflip command
async def cf(ctx, guess: str):

    guess = guess.lower() # Makes all inputs lowercase

    if guess not in ['heads', 'tails']: # Incase the user does not input heads or tails tells them to do so
        await ctx.send(f"Please enter Heads or Tails")
        return
    
    result = random.choice(['heads','tails']) # Sets the RNG to the cf

    if guess == result: # If guess equals results outputs:
        await ctx.send(f"You guessed {guess}, and it was {result}! You win!")

    else: # If the guess does not equal results outputs:
        await ctx.send(f"You guessed {guess}, and it was {result}. You lose :(")

@client.command() # Rock, paper, scissors command
async def rps(ctx, choice: str):

    choice = choice.lower() # Makes all inputs lowercase
    
    options = ['rock', 'paper', 'scissors'] # Sets the options for the rng for the bot

    bot_choice = random.choice(options) # Make the bot have the rng

    if choice not in options: # If the user didn't put in rock, paper, or scissors asks them to put pick one of them.
        await ctx.send("Please choose Rocks, Paper, or Scissors.")
        return
    
    if choice == bot_choice: # If choice equals bot_choice outputs that its a tie
        await ctx.send(f"You both chose {choice}, it's a tie!")

    # Sets the winning conditions. Rock beats scissors, paper beats rock ect
    elif (choice == 'rock' and bot_choice == 'scissors') or \
         (choice == 'paper' and bot_choice == 'rock') or \
         (choice == 'scissors' and bot_choice == 'paper'):
        
        # If one of those conditions are true outputs this:
        await ctx.send (f" You chose {choice}, I chose {bot_choice}. You win!") 

    else: # Else outputs this:
        await ctx.send(f"You chose {choice}, I chose {bot_choice}. You lose!")

# =============================================================
# IDEA: Dungeon crawler/ RPG System mini game
# =============================================================
#For the rpg system after everything is ready.
# Rework how the messages looks. 
# Use avatars emojis or pictures for the users monsters and maybe areas aswell.
# Get images for the loot drops and items
# Get things like healing potions/ "Buff" potions to increase attack/ defense and health above the normal limit
# Maybe try to add something like magic
# Try to add a pet system/ classes for hunter pets

# Initialize the database
def initialize_database():

    conn = sqlite3.connect('rpg_game.db')
    cursor = conn.cursor()

    # Creates the characters table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS characters (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        level INTEGER,
        xp INTEGER,
        health INTEGER,
        max_health INTEGER,
        defense INTEGER,
        attack INTEGER,
        xp_to_level_up INTEGER
    )
    ''')

    # Creates the inventory table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        item TEXT,
        FOREIGN KEY (user_id) REFERENCES characters (user_id)
    )
    ''')

    conn.commit()
    conn.close()

# Call this to initialize the database
initialize_database()

@client.command() # Help message for the commands for the rpg game.
async def rpghelp(ctx):

    rpghelp_message = """
    Here are the commands to play the rpg game:
    ".start" - To create you character and register into the guild
    ".profile" - To check your profile
    ".fight" - To fight monsters for the guild
    ".rest" - To rest and recover your health at the guild inn
    """

    await ctx.send(rpghelp_message)

def is_user_in_database(user_id):

    # Connects with the database (rpg_game.db)
    conn = sqlite3.connect('rpg_game.db')
    cursor = conn.cursor()

    # Query the database for the user ID
    cursor.execute('SELECT 1 FROM characters WHERE user_id = ? LIMIT 1', (user_id,))
    user_exists = cursor.fetchone() is not None  # Returns True if a row exists

    conn.close()
    return user_exists

def load_character(user_id):

    try:

        with sqlite3.connect('rpg_game.db') as conn:

            cursor = conn.cursor()

            # Fetch character data
            cursor.execute('SELECT * FROM characters WHERE user_id = ?', (user_id,))
            character_row = cursor.fetchone()

            if not character_row:

                return None

            # Convert character to dictionary
            character = {
                'Name': character_row[1],
                'Level': character_row[2],
                'Xp': character_row[3],
                'Health': character_row[4],
                'MaxHealth': character_row[5],
                'Defense': character_row[6],
                'Attack': character_row[7],
                'XpToLevelUp': character_row[8],
                'Inventory': {}
            }

            # Fetch inventory items
            cursor.execute('SELECT item, COUNT(item) FROM inventory WHERE user_id = ? GROUP BY item', (user_id,))
            items = cursor.fetchall()

            character['Inventory'] = {item: count for item, count in items}

            return character
        
    except sqlite3.Error as e:

        print(f"Database error in load_character: {e}")
        return None
    
    except Exception as e:

        print(f"Unexpected error in load_character: {e}")
        return None

def reset_character(user_id):

    try:

        with sqlite3.connect("rpg_game.db") as conn:

            cursor = conn.cursor()

            # Delete character data
            cursor.execute("DELETE FROM characters WHERE user_id = ?", (user_id,))
            # Delete inventory data
            cursor.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))

            conn.commit()

    except sqlite3.Error as e:

        print(f"Database error in reset_character: {e}")

    except Exception as e:

        print(f"Unexpected error in reset_character: {e}")

def save_characters(user_id, character):

    try:

        with sqlite3.connect('rpg_game.db') as conn:

            cursor = conn.cursor()

            # Save character stats
            cursor.execute('''
            INSERT OR REPLACE INTO characters (user_id, name, level, xp, health, max_health, defense, attack, xp_to_level_up)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                character['Name'],
                character['Level'],
                character['Xp'],
                character['Health'],
                character['MaxHealth'],
                character['Defense'],
                character['Attack'],
                character['XpToLevelUp']
            ))

            # Update inventory
            cursor.execute('DELETE FROM inventory WHERE user_id = ?', (user_id,))

            if isinstance(character['Inventory'], dict):

                for item, quantity in character['Inventory'].items():

                    for _ in range(quantity):

                        cursor.execute('INSERT INTO inventory (user_id, item) VALUES (?, ?)', (user_id, item))

            elif isinstance(character['Inventory'], list):

                for item in character['Inventory']:

                    cursor.execute('INSERT INTO inventory (user_id, item) VALUES (?, ?)', (user_id, item))

            conn.commit()

    except sqlite3.Error as e:

        print(f"Database error in save_characters: {e}")

    except Exception as e:

        print(f"Unexpected error in save_characters: {e}")

def create_character(user_id, custom_name):

    # The base character preset data
    character = {
        'Name': custom_name,
        'Level': 1,
        'Xp': 0,
        'Health': 100,
        'MaxHealth': 100,
        'Defense': 10,
        'Attack': 5,
        'Inventory': [],
        'XpToLevelUp': 100
    }

    # Save the character to the database
    save_characters(user_id, character)

    # Debugging
    print(f"Character created for user_id={user_id}: {character}")

def take_damage(user_id, damage): # A define to be called later on when the users sends his character to fight something
    
    # Sets character to load_character(user_id)
    character = load_character(user_id)
        
    new_health = character['Health'] - damage # Sets the newHealth to the character current health - the damage it took  

    if new_health < 0: # Incase health goes under 0 sets it back to 0          new_health = 0
        
        character['Health'] = new_health # Attaches the new health back to the character
        
    save_characters(user_id, character) # Saves the file to the json

def get_monsters_for_area(area): # List of monsters and the areas they are in

    areas = {
        'Forest': [
            {'Name': 'Bunny', 'Health': 20, 'Attack': 11, 'Defense': 1, 'XpReward': 10, 'Rarity': 'common', 'LootTable': {'Carrot': {'chance': 90, 'quantity': (1, 5), 'guaranteed': True}, 'Bunny Fur': {'chance': 10, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Wolf', 'Health': 20, 'Attack': 11, 'Defense': 2, 'XpReward': 20, 'Rarity': 'common', 'LootTable': {'Wolf Pelt': {'chance': 80, 'quantity': (1, 2), 'guaranteed': True}, 'Wolf Bone': {'chance': 20, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Boar', 'Health': 20, 'Attack': 15, 'Defense': 2, 'XpReward': 30, 'Rarity': 'uncommon', 'LootTable': {'Boar Pelt': {'chance': 70, 'quantity': (1, 3), 'guaranteed': True}, 'Tusk': {'chance': 30, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Treant', 'Health': 20, 'Attack': 11, 'Defense': 1, 'XpReward': 35, 'Rarity': 'rare', 'LootTable': {'Treant bark': {'chance': 70, 'quantity': (1, 5), 'guaranteed': True}, 'Treant Sap': {'chance': 29, 'quantity': (1, 3), 'guaranteed': False}, 'Treant Heart': {'chance': 1, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Wolf King', 'Health': 20, 'Attack': 20, 'Defense': 3, 'XpReward': 100, 'Rarity': 'legendary', 'LootTable': {'Wolf King Pelt': {'chance': 80, 'quantity': (1, 4), 'guaranteed': True}, 'Wolf King bone': {'chance': 19, 'quantity': 1, 'guaranteed': False}, 'Wolf Kings Essence': {'chance': 1, 'quantity': 1, 'guaranteed': False}}}
        ],
        'Cave': [
            {'Name': 'Bat', 'Health': 80, 'Attack': 12, 'Defense': 5, 'XpReward': 50, 'Rarity': 'common', 'LootTable': {'Bat Wing': {'chance': 70, 'quantity': (1, 2), 'guaranteed': True}, 'Bat ear': {'chance': 30, 'quantity': (1, 2), 'guaranteed': False}}},
            {'Name': 'Giant Spider', 'Health': 100, 'Attack': 15, 'Defense': 7, 'XpReward': 60, 'Rarity': 'uncommon', 'LootTable': {'Spider Legs': {'chance': 80, 'quantity': (1, 8), 'guaranteed': True}, 'Spider Eyes': {'chance': 20, 'quantity': (1, 10), 'guaranteed': False}}},
            {'Name': 'Goblin', 'Health': 200, 'Attack': 25, 'Defense': 12, 'XpReward': 75, 'Rarity': 'rare', 'LootTable': {'Goblin Teeth': {'chance': 69, 'quantity': (1, 8), 'guaranteed': True}, 'Goblin Hide': {'chance': 30, 'quantity': (1, 3), 'guaranteed': False}, 'Goblin Hammer': {'chance': 1, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Basilisk', 'Health': 100, 'Attack': 20, 'Defense': 20, 'XpReward': 175, 'Rarity': 'epic', 'LootTable': {'Basilisk Skin': {'chance': 79, 'quantity': (1, 4), 'guaranteed': True}, 'Basalisk Teeth': {'chance': 20, 'quantity': (1, 10), 'guaranteed': False}, 'Basalisk Scale': {'chance': 1, 'quantity': (1, 5), 'guaranteed': False}}},
            {'Name': 'Mimic', 'Health': 150, 'Attack': 60, 'Defense': 34, 'XpReward': 300, 'Rarity': 'legendary', 'LootTable': {'Mimic Gold Coins': {'chance': 79, 'quantity': (1, 15), 'guaranteed': True}, 'Mixed Gems': {'chance': 20, 'quantity': (1, 4), 'guaranteed': False}, 'Diamond': {'chance': 1, 'quantity': (1, 3), 'guaranteed': False}}},
            {'Name': 'Gostir The Three Headed Dragon', 'Health': 300, 'Attack': 30, 'Defense': 50, 'XpReward': 500, 'Rarity': 'legendary', 'LootTable': {'Dragon Gold Coins': {'chance': 69, 'quantity': (1, 25), 'guaranteed': True}, 'Dragon Scale': {'chance': 30, 'quantity': (1, 8), 'guaranteed': False}, 'The Dragon Slayer': {'chance': 1, 'quantity': 1, 'guaranteed': False}}}
        ],
        'Desert': [
            {'Name': 'Giant Scorpions', 'Health': 150, 'Attack': 40, 'Defense': 10, 'XpReward': 250, 'Rarity': 'common', 'LootTable': {'Stinger': {'chance': 79, 'quantity': (1, 3), 'guaranteed': True}, 'Scorpion Claw': {'chance': 20, 'quantity': (1, 2), 'guaranteed': False}, 'Venow Gland': {'chance': 1, 'quantity': (1, 2), 'guaranteed': False}}},
            {'Name': 'Mummy', 'Health': 250, 'Attack': 30, 'Defense': 15, 'XpReward': 400, 'Rarity': 'uncommon', 'LootTable': {'Mummy Bandage': {'chance': 90, 'quantity': (1, 7), 'guaranteed': True}, 'Mummy Bone': {'chance': 10, 'quantity': (1, 10), 'guaranteed': False}}},
            {'Name': 'Giant Lizards', 'Health': 200, 'Attack': 50, 'Defense': 15, 'XpReward': 420, 'Rarity': 'uncommon', 'LootTable': {'Giant Lizard Meat': {'chance': 70, 'quantity': (1, 7), 'guaranteed': True}, 'Giant Lizard Eye': {'chance': 20, 'quantity': (1, 2), 'guaranteed': False}, 'Giant Lizard Scale': {'chance': 10, 'quantity': (1, 5), 'guaranteed': False}}},
            {'Name': 'Group of Bandits', 'Health': 250, 'Attack': 60, 'Defense': 25, 'XpReward': 500, 'Rarity': 'rare', 'LootTable': {'Ripped Cloth': {'chance': 89, 'quantity': (1, 5), 'guaranteed': True}, 'Bandit Helmet': {'chance': 10, 'quantity': 1, 'guaranteed': False}, 'Bandit Scimitar': {'chance': 1, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Air Elemental', 'Health': 300, 'Attack': 100, 'Defense': 50, 'XpReward': 600, 'Rarity': 'epic', 'LootTable': {'Air Element': {'chance': 74, 'quantity': (1, 8), 'guaranteed': True}, 'Air Elemental Core': {'chance': 15, 'quantity': 1, 'guaranteed': False}, 'Air Elemental Essence': {'chance': 1, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Djinn', 'Health': 250, 'Attack': 150, 'Defense': 75, 'XpReward': 750, 'Rarity': 'epic', 'LootTable': {'Broken Djinn Lamp': {'chance': 89.5, 'quantity': 1, 'guaranteed': True}, 'Djinn Essence': {'chance': 10, 'quantity': 1, 'guaranteed': False}, 'Djinns Flaming Scimitar': {'chance': 0.5, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Brass Dragon', 'Health': 750, 'Attack': 110, 'Defense': 100, 'XpReward': 1500, 'Rarity': 'legendary', 'LootTable': {'Dragon Gold Coins': {'chance': 88.5, 'quantity': (1, 3), 'guaranteed': True}, 'Dragon Scale': {'chance': 10, 'quantity': 1, 'guaranteed': False}, 'Dragon Scale Mail': {'chance': 1, 'quantity': 1, 'guaranteed': False}, 'Brass Dragon Heart': {'chance': 0.5, 'quantity': 1, 'guaranteed': False}}}
        ]
    }
    return areas.get(area, None)

def get_shop_items():

    return [
        {"item_name": "Health Potion", "buy_price": 50, "sell_price": 10, "type": "consumable", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Wooden Sword", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Iron Sword", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Wooden Shield", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Metal Shield", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Leather Helmet", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Leather Vest", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Leather Pants", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Leather Boots", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Chainmail Helmet", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Chainmail Vest", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Chainmail Pants", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Chainmail Boots", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Iron Helmet", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Iron Vest", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Iron Pants", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Iron Boots", "buy_price": 50, "sell_price": 10, "type": "equipment", "effect": {"heal": 50}, "description": "Restores 50 health when the potion is consumed."},
    ]

def get_craftable_items():
    return [
        {"item_name": "Prowler's Stride", "materials": {"Carrot": 1, "Bunny Fur": 1}, "type": "equipment", "effect": {"health": 100,}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Fenrin's Edge", "materials": {"Carrot": 1, "Bunny Fur": 1}, "type": "equipment", "effect": {"attack": 25}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Gostir's Plate", "materials": {"Carrot": 1, "Bunny Fur": 1}, "type": "equipment", "effect": {"health": 150}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Fenrin's Inferno", "materials": {"Carrot": 1, "Bunny Fur": 1}, "type": "equipment", "effect": {"attack": 50}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Eternal Shroud", "materials": {"Carrot": 1, "Bunny Fur": 1}, "type": "equipment", "effect": {"health":2050}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Dragonwoven Shroud", "materials": {"Carrot": 1, "Bunny Fur": 1}, "type": "equipment", "effect": {"health": 250}, "description": "Restores 50 health when the potion is consumed."},
        {"item_name": "Venomcrest Helm", "materials": {"Carrot": 1, "Bunny Fur": 1}, "type": "equipment", "effect": {"health": 300}, "description": "Restores 50 health when the potion is consumed."}
    ]

def Level_up(user_id):

    # Sets character to load_character(user_id)
    character = load_character(user_id)

    # Incase user is not in the database doesnt return anything
    if not character:

        return False

    # Apply level-up changes
    character['Level'] += 1
    character['Attack'] += 2
    character['MaxHealth'] += 20
    character['Defense'] += 1
    character['XpToLevelUp'] = int(character['XpToLevelUp'] * 1.2)  # Increase XP for next level
    character['Health'] = character['MaxHealth']  # Restore health

    # Save changes
    save_characters(user_id, character)

    print(f"New stats: Level {character['Level']}, Attack {character['Attack']}, MaxHealth {character['MaxHealth']}, Defense {character['Defense']}, Next XPToLevelUp: {character['XpToLevelUp']}")

    return True

def Check_Level_Up(user_id):

    character = load_character(user_id)

    if not character:

        return None

    leveled_up = False

    while character['Xp'] >= character['XpToLevelUp']:
        # Deduct XP required for level-up
        character['Xp'] -= character['XpToLevelUp']

        # Apply level-up changes
        character['Level'] += 1
        character['Attack'] += 2
        character['MaxHealth'] += 20
        character['Defense'] += 1
        character['XpToLevelUp'] = int(character['XpToLevelUp'] * 1.2)  # Increase XP for next level
        character['Health'] = character['MaxHealth']  # Restore health
        leveled_up = True

    # Save the updated character
    save_characters(user_id, character)

    print(f"Level-up complete. New stats: {character}")
    return character if leveled_up else None

def Generate_Loot(loot_table):

    loot_dropped = []

    # Sets it so all the ietms with guaranteed set to true to always drop
    for item, details in loot_table.items():

        if details.get('guaranteed', False):

            quantity = details.get('quantity', 1)

            if isinstance(quantity, tuple):

                quantity = random.randint(quantity[0], quantity[1])

            loot_dropped.append((item, quantity))

        # Everything that is not set to true goes through this
        else:

            drop_chance = details['chance'] * 100  # Adjust if chance is a fraction (e.g., 0.5 = 50%)

            if random.randint(1, 10000) <= drop_chance:  # 1-10000 for 0.01% precision

                quantity = details.get('quantity', 1)

                if isinstance(quantity, tuple):

                    quantity = random.randint(quantity[0], quantity[1])
                
                loot_dropped.append((item, quantity))

    return loot_dropped

def add_to_inventory(inventory, item_name, quantity):

    if inventory is None:

        inventory = {}  # Initialize inventory if it's None

    if item_name in inventory:

        inventory[item_name] += quantity  # Increment quantity if the item exists

    else:

        inventory[item_name] = quantity  # Add the new item with the given quantity

    return inventory  # Always return the updated inventory

async def battle(ctx, user_id, area):

    user_id = str(ctx.author.id)
    character = load_character(user_id)

    if not character:

        await ctx.send("You need to join the guild first! Use `.start` to create your character.")
        return

    # Spawn a monster for the area
    monster = Spawn_Monster(area)

    if not monster:

        await ctx.send(f"No monsters found in the {area}. Try exploring somewhere else!")
        return

    # Send initial embed for battle
    battle_embed = discord.Embed(title=f"Battle: {character['Name']} vs {monster['Name']}", color=discord.Color.red())
    battle_embed.add_field(name="Monster Stats", value=f"Health: {monster['Health']}, Attack: {monster['Attack']}, Defense: {monster['Defense']}")
    message = await ctx.send(embed=battle_embed)

    # Battle loop
    while character['Health'] > 0 and monster['Health'] > 0:
        # Player attacks monster
        damage_to_monster = max(character['Attack'] - monster['Defense'], 1)
        monster['Health'] -= damage_to_monster

        # Monster attacks player
        damage_to_player = max(monster['Attack'] - character['Defense'], 1)
        character['Health'] = max(0, character['Health'] - damage_to_player)

        # Update embed with new stats
        battle_embed.clear_fields()
        battle_embed.add_field(name=f"{character['Name']} attacks!", value=f"Dealt {damage_to_monster} damage. Monster HP: {max(monster['Health'], 0)}")
        battle_embed.add_field(name=f"{monster['Name']} attacks!", value=f"Dealt {damage_to_player} damage. Your HP: {character['Health']}/{character['MaxHealth']}")
        await message.edit(embed=battle_embed)
        await asyncio.sleep(1)  # Dramatic pause

        if monster['Health'] <= 0:
            break

        if character['Health'] <= 0:
            break

    # Post-battle rewards or defeat screen
    if character['Health'] > 0:
        # Monster defeated
        character['Xp'] += monster['XpReward']

        # Check for level-up and update character
        updated_character = Check_Level_Up(user_id)
        if updated_character:

            character = updated_character  # Use the updated character stats

        # Rewards embed
        rewards_embed = discord.Embed(title=f"Victory! {character['Name']} defeated {monster['Name']}", color=discord.Color.green())
        rewards_embed.add_field(name="XP Gained", value=f"{monster['XpReward']}", inline=False)

        if updated_character:

            rewards_embed.add_field(name="Level Up!", value=f"Level {character['Level']} achieved!", inline=False)

        # Loot generation
        if 'LootTable' in monster and monster['LootTable']:

            loot = Generate_Loot(monster['LootTable'])

            if loot:

                loot_message = "\n".join([f"- {item}: x{quantity}" for item, quantity in loot])
                rewards_embed.add_field(name="Loot Collected", value=loot_message, inline=False)

                for item, quantity in loot:

                    character['Inventory'] = add_to_inventory(character['Inventory'], item, quantity)
        else:

            rewards_embed.add_field(name="Loot Collected", value="No loot dropped.", inline=False)

        # Replace the battle embed with the rewards embed
        await message.edit(embed=rewards_embed)

    else:
        # Player defeated
        defeat_embed = discord.Embed(title=f"Defeat... {character['Name']} was defeated by {monster['Name']}", color=discord.Color.dark_red())
        defeat_embed.add_field(name="Tip", value="Rest at the guild to recover and try again.")
        await message.edit(embed=defeat_embed)

    # Save character updates
    save_characters(user_id, character)

def Spawn_Monster(area): 
    # Balanced monster generation with corrected weighting
    monsters = get_monsters_for_area(area)

    if not monsters:

        return None
    
    rarity_weights = {'common': 10, 'uncommon': 6, 'rare': 3, 'epic': 1, 'legendary': 0.5}
    total_weight = sum(rarity_weights[m['Rarity']] for m in monsters)
    random_choice = random.uniform(0, total_weight)
    cumulative_weight = 0

    for monster in monsters:

        cumulative_weight += rarity_weights[monster['Rarity']]

        if random_choice <= cumulative_weight:

            return monster
        
    return None           

@client.command()
@cooldown(1, 5, BucketType.user)
async def start(ctx):
    user_id = str(ctx.author.id)

    # Check if the user already exists in the database
    if is_user_in_database(user_id):
        embed = discord.Embed(
            title = "Already a member",
            description = "You are already part of the guild, adventurer.",
            color = discord.Color.orange()
        )
        await ctx.send(embed = embed)
        return

    embed = discord.Embed(
        title = "Welcome adventurer!",
        description = "Please write down your preffered name in the guild list",
        color = discord.Color.blue()
    )
    embed.set_footer(text = "You have 30 seconds to respond.")
    message = await ctx.send(embed = embed)

    def check(msg):
        return msg.author == ctx.author and len(msg.content) > 0

    try:
        # Wait for the user's response for the custom name
        name_msg = await client.wait_for('message', check=check, timeout=30.0)
        custom_name = name_msg.content

        # Create the character with the custom name
        create_character(user_id, custom_name)

        # Debugging: Ensure the user is now in the database
        if is_user_in_database(user_id):
            print(f"User successfully added to the database: user_id={user_id}")
        else:
            print(f"Failed to add user to the database: user_id={user_id}")

        embed = discord.Embed(
            title = "Adventurer Registered!",
            description = f"Adventurer **{custom_name}** has joined the guild! You can now go out and slay monsters for the guild.",
            color = discord.Color.green()
        )
        await message.edit(embed = embed)

    except asyncio.TimeoutError:
        embed = discord.Embed(
            title = "Timedout.",
            description = "You took to long to write down your name adventurer.",
            color = discord.Color.red()
        )
        await message.edit(embed = embed)

@client.command()
async def profile(ctx):
    user_id = str(ctx.author.id)

    # Load the character from the database
    character = load_character(user_id)

    if not character:
        # User is not in the database
        embed = discord.Embed(
            title = "Not a member.",
            description = "You aren't a member of the guild yet adventurer. Join with '.start'.",
            color = discord.Color.orange()
        )
        await ctx.send(embed = embed)
        return

    # XP progress bar
    xp_bar_length = 15
    xp_progress = character['Xp'] / character['XpToLevelUp']
    xp_filled = int(xp_progress * xp_bar_length)
    xp_empty = xp_bar_length - xp_filled
    xp_bar = f"[{'#' * xp_filled}{' ' * xp_empty}] {character['Xp']} / {character['XpToLevelUp']}"

    # Makes the inventory 3 items per row
    inventory_items = [f"{item}: x{quantity}" for item, quantity in character['Inventory'].items()]
    items_per_row = 3
    rows = [inventory_items[i:i + items_per_row] for i in range(0, len(inventory_items), items_per_row)]
    formatted_inventory = "\n".join([",   ".join(row) for row in rows])

    # Create embed for the profile
    profile_embed = discord.Embed(
        title=f"Profile of {character['Name']}",
        color=discord.Color.blue(),
        description="Here are your current stats and inventory."
    )
    profile_embed.add_field(name="🏅 Level", value=character['Level'], inline=True)
    profile_embed.add_field(name="🌟 XP", value=xp_bar, inline=True)
    profile_embed.add_field(name="❤️ Health", value=f"{character['Health']} / {character['MaxHealth']}", inline=True)
    profile_embed.add_field(name="🛡️ Defense", value=character['Defense'], inline=True)
    profile_embed.add_field(name="⚔️ Attack", value=character['Attack'], inline=True)

    # Add inventory fields
    if inventory_items:
        profile_embed.add_field(name = "🎒 Inventory (1/2)", value = formatted_inventory, inline = False)

    else:
        profile_embed.add_field(name = "🎒 Inventory", value="Empty", inline = False)

    profile_embed.set_footer(text = f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    # Send the profile embed
    await ctx.send(embed=profile_embed)

@client.command()
@cooldown(1, 5, BucketType.user)  # 1 use per 5 seconds
async def rest(ctx):
    user_id = str(ctx.author.id)

    # Load the character
    character = load_character(user_id)

    if not character:
        embed = discord.Embed(
            title = "Not a member.",
            description = "You aren't a member of the guild yet adventurer. Join with '.start'.",
            color = discord.Color.orange()
        )
        await ctx.send(embed = embed)
        return

    if character['Health'] >= character['MaxHealth']:
        # Use an embed to notify the user
        full_health_embed = discord.Embed(
            title="Resting Not Needed",
            description=f"{character['Name']} is already at full health!",
            color=discord.Color.gold()
        )
        await ctx.send(embed=full_health_embed)
        return

    heal_amount = character['MaxHealth'] // 5  # Heal 20% of max health per second
    total_time = 5  # Total rest duration in seconds

    # Create initial embed
    rest_embed = discord.Embed(
        title=f"{character['Name']} is resting...",
        description="Healing in progress...",
        color=discord.Color.blue()
    )
    rest_embed.add_field(name="Health", value=f"{character['Health']} / {character['MaxHealth']}")
    message = await ctx.send(embed=rest_embed)

    try:
        for second in range(1, total_time + 1):
            # Increment health
            character['Health'] = min(character['MaxHealth'], character['Health'] + heal_amount)

            # Update embed with progress
            rest_embed.clear_fields()
            rest_embed.add_field(name="Health", value=f"{character['Health']} / {character['MaxHealth']}")
            rest_embed.set_footer(text=f"Resting... {second}/{total_time} seconds elapsed")
            await message.edit(embed=rest_embed)

            await asyncio.sleep(1)  # Wait 1 second between updates

            if character['Health'] >= character['MaxHealth']:
                break

        # Final embed to show completion
        rest_embed.title = f"{character['Name']} is fully rested!"
        rest_embed.description = "Resting complete. You are ready for your next adventure!"
        rest_embed.color = discord.Color.green()
        rest_embed.clear_fields()
        rest_embed.add_field(name="Health", value=f"{character['Health']} / {character['MaxHealth']}")
        await message.edit(embed=rest_embed)

        # Save updated health to the database
        save_characters(user_id, character)

    except Exception as e:
        await ctx.send(f"An error occurred during rest: {str(e)}")

@client.command()
@cooldown(1, 5, BucketType.user)
async def fight(ctx, area: str):
    user_id = str(ctx.author.id)

    if not is_user_in_database(user_id):
        embed = discord.Embed(
            title = "Not a member.",
            description = "You aren't a member of the guild yet adventurer. Join with '.start'.",
            color = discord.Color.orange()
        )
        await ctx.send(embed = embed)
        return

    character = load_character(user_id)
    monster = Spawn_Monster(area)

    if not monster:

        await ctx.send("Somebody already took all the bounty's for this area. Please try another one.")
        return

    print(f"Character: {character['Name']} - Monster: {monster['Name']}")  # Debugging

    result = await battle(ctx, user_id, area)  # Pass the `ctx` to allow messaging
    await ctx.send(result)

    if Check_Level_Up(user_id):

        await ctx.send(f"Congratulations {character['Name']}! You have leveled up!")

@client.command()
@cooldown(1, 5, BucketType.user)
async def shop(ctx):
    user_id = str(ctx.author.id)

    if not is_user_in_database(user_id):
        embed = discord.Embed(
            title = "Not a member.",
            description = "You aren't a member of the guild yet adventurer. Join with '.start'.",
            color = discord.Color.orange()
        )
        await ctx.send(embed = embed)
        return
    
    character = load_character(user_id)
    shop_items = get_shop_items



@client.command()
@cooldown(1, 5, BucketType.user)
async def testlevelup(ctx):
    user_id = str(ctx.author.id)

    character = load_character(user_id)
    if not character:
        await ctx.send("You don't have a character. Use `.start` to create one.")
        return

    # Give XP to trigger a level-up
    character['Xp'] = character['XpToLevelUp'] + 1
    save_characters(user_id, character)

    if Check_Level_Up(user_id):
        character = load_character(user_id)  # Reload to get updated state
        await ctx.send(f"Level-up successful! {character['Name']} is now Level {character['Level']}. XP: {character['Xp']}, Next Level XP: {character['XpToLevelUp']}")
    else:
        await ctx.send("Level-up failed.")

@client.command()
@cooldown(1, 5, BucketType.user)
async def resetdata(ctx):
    user_id = str(ctx.author.id)

    # Check if the user is in the database
    if not is_user_in_database(user_id):
        await ctx.send("You are not registered in the guild. Register with `.start`.")
        return

    await ctx.send("Are you sure you want to leave the guild? Type 'yes' to confirm.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "yes"

    try:
        # Wait for confirmation
        await client.wait_for("message", check=check, timeout=30)

        # Reset character data
        reset_character(user_id)
        await ctx.send("You have officially left the guild. If you ever want to return, type `.start`.")

    except asyncio.TimeoutError:
        await ctx.send("You took too long to decide. Reset canceled.")


######################################
# Make monsters drop loot each different in value
# Make loot drops like items that the user can use
# Maybe something like a dungeon later on with a endgame boss
# Make a shop and a crafting system
# Change up the Ui with how everything is getting output
# 

client.run(TOKEN)