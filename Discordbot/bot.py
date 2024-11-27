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
    ".fight" - To fight monsters for the guild"""
    await ctx.send(rpghelp_message)

def is_user_in_database(user_id):

    conn = sqlite3.connect('rpg_game.db')
    cursor = conn.cursor()

    # Query the database for the user ID
    cursor.execute('SELECT 1 FROM characters WHERE user_id = ? LIMIT 1', (user_id,))
    user_exists = cursor.fetchone() is not None  # Returns True if a row exists

    conn.close()
    return user_exists

def load_character(user_id):

    conn = sqlite3.connect('rpg_game.db')
    cursor = conn.cursor()

    # Fetch character data
    cursor.execute('SELECT * FROM characters WHERE user_id = ?', (user_id,))
    character_row = cursor.fetchone()

    if not character_row:

        conn.close()
        return None

    # Convert row into a dictionary
    character = {
        'Name': character_row[1],
        'Level': character_row[2],
        'Xp': character_row[3],
        'Health': character_row[4],
        'MaxHealth': character_row[5],
        'Defense': character_row[6],
        'Attack': character_row[7],
        'XpToLevelUp': character_row[8],
        'Inventory': []
    }

    # Fetch inventory items
    cursor.execute('SELECT item FROM inventory WHERE user_id = ?', (user_id,))
    items = cursor.fetchall()
    character['Inventory'] = [item[0] for item in items]

    conn.close()
    return character

def reset_character(user_id):

    with sqlite3.connect("rpg_game.db") as conn:

        cursor = conn.cursor()
        cursor.execute("DELETE FROM characters WHERE user_id = ?", (user_id,))
        conn.commit()

def save_characters(user_id, character):

    conn = sqlite3.connect('rpg_game.db')
    cursor = conn.cursor()

    # Update character data
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

    for item in character['Inventory']:

        cursor.execute('INSERT INTO inventory (user_id, item) VALUES (?, ?)', (user_id, item))

    conn.commit()
    conn.close()

def create_character(user_id, custom_name):

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
    
    character = load_character(user_id)
        
    new_health = character['Health'] - damage # Sets the newHealth to the character current health - the damage it took  

    if new_health < 0: # Incase health goes under 0 sets it back to 0          new_health = 0
        
        character['Health'] = new_health # Attaches the new health back to the character
        
    save_characters() # Saves the file to the json

def get_monsters_for_area(area): # List of monsters and the areas they are in

    areas = {
        'Forest': [
            {'Name': 'Bunny', 'Health': 20, 'Attack': 11, 'Defense': 1, 'XpReward': 10, 'Rarity': 'common', 'LootTable': {'Carrot': {'chance': 90, 'quantity': (1, 5), 'guaranteed': True}, 'Rabbit Fur': {'chance': 10, 'quantity': 1, 'guaranteed': False}}},
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
            {'Name': 'Mimic', 'Health': 150, 'Attack': 60, 'Defense': 34, 'XpReward': 300, 'Rarity': 'legendary', 'LootTable': {'Gold Coins': {'chance': 79, 'quantity': (1, 15), 'guaranteed': True}, 'Mixed Gems': {'chance': 20, 'quantity': (1, 4), 'guaranteed': False}, 'Diamond': {'chance': 1, 'quantity': (1, 3), 'guaranteed': False}}},
            {'Name': 'Gostir The Three Headed Dragon', 'Health': 300, 'Attack': 30, 'Defense': 50, 'XpReward': 500, 'Rarity': 'legendary', 'LootTable': {'Gold Coins': {'chance': 69, 'quantity': (1, 25), 'guaranteed': True}, 'Dragon Scale': {'chance': 30, 'quantity': (1, 8), 'guaranteed': False}, 'The Dragon Slayer': {'chance': 1, 'quantity': 1, 'guaranteed': False}}}
        ],
        'Desert': [
            {'Name': 'Giant Scorpions', 'Health': 150, 'Attack': 40, 'Defense': 10, 'XpReward': 250, 'Rarity': 'common', 'LootTable': {'Stinger': {'chance': 79, 'quantity': (1, 3), 'guaranteed': True}, 'Scorpion Claw': {'chance': 20, 'quantity': (1, 2), 'guaranteed': False}, 'Venow Gland': {'chance': 1, 'quantity': (1, 2), 'guaranteed': False}}},
            {'Name': 'Mummy', 'Health': 250, 'Attack': 30, 'Defense': 15, 'XpReward': 400, 'Rarity': 'uncommon', 'LootTable': {'Bandage': {'chance': 90, 'quantity': (1, 7), 'guaranteed': True}, 'Mummy Bone': {'chance': 10, 'quantity': (1, 10), 'guaranteed': False}}},
            {'Name': 'Giant Lizards', 'Health': 200, 'Attack': 50, 'Defense': 15, 'XpReward': 420, 'Rarity': 'uncommon', 'LootTable': {'Giant Lizard Meat': {'chance': 70, 'quantity': (1, 7), 'guaranteed': True}, 'Giant Lizard Eye': {'chance': 20, 'quantity': (1, 2), 'guaranteed': False}, 'Giant Lizard Scale': {'chance': 10, 'quantity': (1, 5), 'guaranteed': False}}},
            {'Name': 'Group of Bandits', 'Health': 250, 'Attack': 60, 'Defense': 25, 'XpReward': 500, 'Rarity': 'rare', 'LootTable': {'Ripped Cloth': {'chance': 89, 'quantity': (1, 5), 'guaranteed': True}, 'Bandit Helmet': {'chance': 10, 'quantity': 1, 'guaranteed': False}, 'Bandit Scimitar': {'chance': 1, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Air Elemental', 'Health': 300, 'Attack': 100, 'Defense': 50, 'XpReward': 600, 'Rarity': 'epic', 'LootTable': {'Air Element': {'chance': 74, 'quantity': (1, 8), 'guaranteed': True}, 'Air Elemental Core': {'chance': 15, 'quantity': 1, 'guaranteed': False}, 'Air Elemental Essence': {'chance': 1, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Djinn', 'Health': 250, 'Attack': 150, 'Defense': 75, 'XpReward': 750, 'Rarity': 'epic', 'LootTable': {'Broken Djinn Lamp': {'chance': 89.5, 'quantity': 1, 'guaranteed': True}, 'Djinn Essence': {'chance': 10, 'quantity': 1, 'guaranteed': False}, 'Djinns Flaming Scimitar': {'chance': 0.5, 'quantity': 1, 'guaranteed': False}}},
            {'Name': 'Brass Dragon', 'Health': 750, 'Attack': 110, 'Defense': 100, 'XpReward': 1500, 'Rarity': 'legendary', 'LootTable': {'Gold Coins': {'chance': 88.5, 'quantity': (1, 3), 'guaranteed': True}, 'Dragon Scale': {'chance': 10, 'quantity': 1, 'guaranteed': False}, 'Dragon Scale Mail': {'chance': 1, 'quantity': 1, 'guaranteed': False}, 'Brass Dragon Heart': {'chance': 0.5, 'quantity': 1, 'guaranteed': False}}}
        ]
    }
    return areas.get(area, None)

def Level_up(user_id):

    character = load_character(user_id)

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

        return False

    leveled_up = False
    while character['Xp'] >= character['XpToLevelUp']:
        # Deduct XP required for level-up
        character['Xp'] -= character['XpToLevelUp']
        Level_up(user_id)  # Perform the level-up
        leveled_up = True

        # Reload character after level-up to ensure accurate state
        character = load_character(user_id)

    save_characters(user_id, character)
    return leveled_up

def Generate_Loot(loot_table):

    loot_dropped = []

    for item, details in loot_table.items():

        if details.get('guaranteed', False):

            quantity = details['quantity']

            if isinstance(quantity, tuple):

                quantity = random.randint(quantity[0], quantity[1])

            loot_dropped.append((item, quantity))

        else:

            drop_chance = details['chance'] * 100  # Adjust if chance is a fraction (e.g., 0.5 = 50%)

            if random.randint(1, 10000) <= drop_chance:  # 1-10000 for 0.01% precision

                loot_quantity = details['quantity']

                quantity = random.randint(loot_quantity[0], loot_quantity[1]) if isinstance(loot_quantity, tuple) else loot_quantity

                loot_dropped.append((item, quantity))

    return loot_dropped


def add_to_inventory(inventory, item_name, quantity):

    if not inventory:  # Initialize inventory if empty
        
        inventory = {}

    if item_name in inventory:

        inventory[item_name] += quantity

    else:

        inventory[item_name] = quantity

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

    await ctx.send(f"A wild **{monster['Name']}** appears! Prepare for battle!")

    while character['Health'] > 0 and monster['Health'] > 0:
        # Player attacks monster
        damage_to_monster = max(character['Attack'] - monster['Defense'], 1)
        monster['Health'] -= damage_to_monster

        if monster['Health'] <= 0:
            # Monster defeated
            await ctx.send(f"**{character['Name']}** has defeated the **{monster['Name']}**!")
            character['Xp'] += monster['XpReward']

            # Check for level-up
            leveled_up = Check_Level_Up(user_id)
            if leveled_up:
                await ctx.send(f" {character['Name']} leveled up to **Level {character['Level']}**!")

            # Generate loot
            if 'LootTable' in monster and monster['LootTable']:
                loot = Generate_Loot(monster['LootTable'])
                if loot:
                    loot_message = f"Loot obtained from {monster['Name']}:\n"
                    for item, quantity in loot:
                        add_to_inventory(character['Inventory'], item, quantity)
                        loot_message += f"- **{item}** x{quantity}\n"
                    await ctx.send(loot_message)
                else:
                    await ctx.send("No loot obtained from this battle.")
            else:
                await ctx.send(f"{monster['Name']} had no loot.")
            
            # Save updated character to the database
            save_characters(user_id, character)
            return

        # Monster attacks player
        damage_to_player = max(monster['Attack'] - character['Defense'], 1)
        character['Health'] = max(0, character['Health'] - damage_to_player)
        await ctx.send(
            f"**{monster['Name']}** attacks **{character['Name']}** for {damage_to_player} damage! "
            f"Remaining Health: {character['Health']}/{character['MaxHealth']}"
        )

        if character['Health'] == 0:
            await ctx.send(f"**{character['Name']}** was defeated by the **{monster['Name']}**. Rest at the guild to recover.")
            save_characters(user_id, character)
            return

    # Fallback message (should not reach here)
    return "Battle ended unexpectedly."


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
async def start(ctx):
    user_id = str(ctx.author.id)

    # Check if the user already exists in the database
    if is_user_in_database(user_id):

        await ctx.send(f"You are already in the guild, adventurer.")
        return

    await ctx.send(f"Welcome adventurer! Please write down your preferred name in the guild list:")

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

        await ctx.send(f"Adventurer {custom_name} has joined the guild! You can now go out and slay monsters for the guild.")

    except asyncio.TimeoutError:

        await ctx.send("You took too long to choose a name. Please try again.")


@client.command()
async def profile(ctx):

    await asyncio.sleep(0.5)  # Optional delay to ensure database updates are complete
    user_id = str(ctx.author.id)
    
    if not is_user_in_database(user_id):

        await ctx.send("You are not enlisted in the guild traveler. Join the guild with `.start`.")
        return

    character = load_character(user_id)

    xp_bar_length = 15
    xp_progress = character['Xp'] / character['XpToLevelUp']
    xp_filled = int(xp_progress * xp_bar_length)
    xp_empty = xp_bar_length - xp_filled

    xp_bar = f"[{'#' * xp_filled}{' ' * xp_empty}] {character['Xp']} / {character['XpToLevelUp']}"

    if character.get('inventory'):
        
        inventory_items = ', ' .join(character['inventory']) if character['inventory'] else "Empty"
    
    else:
        inventory_items = "Empty"

    profile_message = (
        f"**Profile of {character['Name']}**\n"
        f"**Level:** {character['Level']}\n"
        f"**Xp:** {xp_bar}\n"
        f"**Health:** {character['Health']}/{character['MaxHealth']}\n"
        f"**Defense:** {character['Defense']}\n"
        f"**Attack:** {character['Attack']}\n"
        f"**Inventory:** {inventory_items}"
    )

    await ctx.send(profile_message)

@client.command()
async def fight(ctx, area: str):
    user_id = str(ctx.author.id)

    if not is_user_in_database(user_id):

        await ctx.send("You are not enlisted in the guild traveler. Join the guild with `.start`.")
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
async def resetdata(ctx):
    user_id = str(ctx.author.id)

    if not is_user_in_database:
        await ctx.send(f"You are not registed in the guild you cant reset your data. Register with '.start'.")
        return

    await ctx.send(f"Are you sure you want to leave te guild? Write down 'yes' to confirm.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "yes"
    
    try:

        await client.wait_for("message", check=check, timeout=30)

        reset_character(user_id)
        await ctx.send(f"You're officially out of the guild. If you ever want to return rype '.start'.")

    except asyncio.TimeoutError:

        await ctx.send(f"You took to long to decide if you really want to leave the guild.")

# Fight system:
# Make about 3 areas each different in difficulty
# Area 1: Forest
# Area 2: Mountain/Cave
# Area 3: Cave or wasteland
# Extra area idea: Dessert

# Make monsters drop loot each different in value
# Make loot drops like items that the user can use
# Maybe something like a dungeon later on with a endgame boss
# 

client.run(TOKEN)