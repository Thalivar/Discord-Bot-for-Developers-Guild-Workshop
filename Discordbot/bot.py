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

@client.command() # Help message for the commands for the rpg game.
async def rpghelp(ctx):
    rpghelp_message = """
    Here are the commands to play the rpg game:
    ".start" - To create you character and register into the guild
    ".profile" - To check your profile
    ".fight" - To fight monsters for the guild"""
    await ctx.send(rpghelp_message)

def load_characters(): # A define to load the characters from the json
    if os.path.exists('characters.json'):
        with open ('characters.json', 'r') as f:
            return json.load(f)
    return {}

characters = load_characters()

def save_characters():
    """Save all characters to the JSON file."""
    with open('characters.json', 'w') as f:
        json.dump(characters, f, indent=4)
        print("Character data saved!")  # Debugging to confirm the file is being saved

def create_character(user_id, custom_name): # the name and stats that are saved in the json

    characters[user_id] = {
        
        'Name': custom_name, # The characters name
        'Level': 1, # The level of the character
        'Xp': 0, # How much xp the character has
        'Health': 100, # How much current health the character has
        'MaxHealth':100, # What the max health of the character is
        'Defense': 10, # What defense stat the character has
        'Attack': 5, # How much damage the character does
        'Inventory': [], # Shows what the character has in his inventory
        'XpToLevelUp': 100 # The amount it takes to levelup each level (The amount needed will increase each level)
    }
    save_characters()

def take_damage(user_id, damage): # A define to be called later on when the users sends his character to fight something
    
    if user_id in characters: # Checks if the user is in the json file
        character = characters[user_id]
        
        new_health = character['Health'] - damage # Sets the newHealth to the character current health - the damage it took
        
        if new_health < 0: # Incase health goes under 0 sets it back to 0
            new_health = 0
        
        character['Health'] = new_health # Attaches the new health back to the character
        
        save_characters() # Saves the file to the json

def Level_up(user_id): # If the user has enough xp (Checked with Check_Level_Up) Levels up the user and increases its stats

    if user_id in characters:
        
        character = characters[user_id]

        print(f"Leveling up {user_id}... Current level: {character['Level']}, XP: {character['Xp']}")  # Debugging

        character['Level'] += 1  # Increase level by 1
        character['Attack'] += 2  # Increase attack by 2
        character['MaxHealth'] += 20  # Increase max health by 20
        character['Defense'] += 1  # Increase defense by 1
        character["XpToLevelUp"] = int(character['XpToLevelUp'] * 1.2)  # Increase XP required for next level by 20%

        character['Health'] = character['MaxHealth']  # Set health to max

        print(f"New stats for {user_id}: Level {character['Level']}, Attack {character['Attack']}, Health {character['Health']}, XP to level up {character['XpToLevelUp']}")  # Debugging

        save_characters()  # Save updated character data

        return True  # Return True to indicate level-up successful

    return False  # Return False if user not found

def Check_Level_Up(user_id): # Checks if the user can levelup with its current xp
    
    if user_id in characters:
        character = characters[user_id]
        
        print(f"Checking level-up for {user_id}. Current XP: {character['Xp']} / XP required: {character['XpToLevelUp']}")  # Debugging

        # Check if the player has enough XP to level up
        if character['Xp'] >= character['XpToLevelUp']:
            print(f"{user_id} has enough XP to level up!")  # Debugging
            character['Xp'] -= character['XpToLevelUp']  # Deduct XP required for level-up
            return Level_up(user_id)  # Level up and return True if successful
        else:
            print(f"{user_id} does not have enough XP to level up.")  # Debugging
    return False  # Return False if no level-up condition is met

def get_monsters_for_area(area): # List of monsters and the areas they are in

    areas = {
        'Forest': [
            {'Name': 'Bunny', 'Health': 1, 'Attack': 11, 'Defense': 1, 'XpReward': 10, 'Rarity': 'common'},
            {'Name': 'Wolf', 'Health': 1, 'Attack': 11, 'Defense': 2, 'XpReward': 20, 'Rarity': 'common'},
            {'Name': 'Boar', 'Health': 2, 'Attack': 15, 'Defense': 2, 'XpReward': 30, 'Rarity': 'uncommon'},
            {'Name': 'Treant', 'Health': 2, 'Attack': 11, 'Defense': 1, 'XpReward': 35, 'Rarity': 'rare'},
            {'Name': 'Wolf King', 'Health': 2, 'Attack': 20, 'Defense': 3, 'XpReward': 100, 'Rarity': 'legendary'}
        ],
        'Cave': [
            {'Name': 'Bat', 'Health': 80, 'Attack': 12, 'Defense': 5, 'XpReward': 50, 'Rarity': 'common'},
            {'Name': 'Giant Spider', 'Health': 100, 'Attack': 15, 'Defense': 7, 'XpReward': 60, 'Rarity': 'uncommon'},
            {'Name': 'Troll', 'Health': 200, 'Attack': 25, 'Defense': 12, 'XpReward': 75, 'Rarity': 'rare'},
            {'Name': 'Basilisk', 'Health': 100, 'Attack': 20, 'Defense': 20, 'XpReward': 175, 'Rarity': 'epic'},
            {'Name': 'Mimic', 'Health': 150, 'Attack': 60, 'Defense': 34, 'XpReward': 300, 'Rarity': 'legendary'},
            {'Name': 'Orc', 'Health': 300, 'Attack': 30, 'Defense': 50, 'XpReward': 500, 'Rarity': 'legendary'}
        ],
        'Dessert': [
            {'Name': 'Giant Scorpions', 'Health': 150, 'Attack': 40, 'Defense': 10, 'XpReward': 250, 'Rarity': 'common'},
            {'Name': 'Mummy', 'Health': 250, 'Attack': 30, 'Defense': 15, 'XpReward': 400, 'Rarity': 'uncommon'},
            {'Name': 'Giant Lizards', 'Health': 200, 'Attack': 50, 'Defense': 15, 'XpReward': 420, 'Rarity': 'uncommon'},
            {'Name': 'Group of Bandits', 'Health': 250, 'Attack': 60, 'Defense': 25, 'XpReward': 500, 'Rarity': 'rare'},
            {'Name': 'Air Elemental', 'Health': 300, 'Attack': 100, 'Defense': 50, 'XpReward': 600, 'Rarity': 'epic'},
            {'Name': 'Jinn', 'Health': 250, 'Attack': 150, 'Defense': 75, 'XpReward': 750, 'Rarity': 'legendary'},
            {'Name': 'Brass Dragon', 'Health': 750, 'Attack': 110, 'Defense': 100, 'XpReward': 1500, 'Rarity': 'legendary'}
        ]
    }
    return areas.get(area, None)

def Spawn_Monster(area):  # Function to spawn a monster
    monsters = get_monsters_for_area(area)
    
    # Debugging: Check what monsters are returned
    if not monsters:
        print(f"Error: No monsters found for area: {area}")
        return None
    
    # Define the rarity weights
    rarity_weights = {
        'common': 1,
        'uncommon': 2,
        'rare': 5,
        'epic': 8,
        'legendary': 10
    }

    # Calculate the total weight of all the monsters in the area
    total_weight = sum(rarity_weights[monster['Rarity']] for monster in monsters)
    print(f"Total weight for area {area}: {total_weight}")  # Debugging

    # Generate a random number between 1 and total_weight
    random_choice = random.randint(1, total_weight)
    print(f"Random choice: {random_choice}")  # Debugging

    # Determine which monster is selected based on the random number and weights
    weight_sum = 0
    for monster in monsters:
        weight_sum += rarity_weights[monster['Rarity']]  # Accumulate the weight sum
        print(f"Checking monster {monster['Name']} with cumulative weight sum: {weight_sum}")  # Debugging
        
        if random_choice <= weight_sum:
            print(f"Selected monster: {monster['Name']}")  # Debugging
            return monster  # Return the monster that has been selected

    return None  # In case no monster is selected, but this shouldn't happen.

async def battle(character, monster):
    
    print(f"Battle started between {character['Name']} and {monster['Name']}")  # Debugging

    while character['Health'] > 0 and monster['Health'] > 0:
        # Character attacks first
        damage_to_monster = max(character['Attack'] - monster['Defense'], 1)  # Ensure no zero damage
        monster['Health'] -= damage_to_monster
        print(f"{monster['Name']} takes {damage_to_monster} damage, remaining health: {monster['Health']}")

        # Check if monster is dead
        if monster['Health'] <= 0:
            monster['Health'] = 0  # Prevent monster health from going negative
            # Award XP to the player after defeating the monster
            character['Xp'] += monster['XpReward']
            print(f"{character['Name']} gained {monster['XpReward']} XP! Total XP: {character['Xp']}")

            # Save the character data with updated XP
            save_characters()  # Ensure XP is saved to the file

            # Return the victory message, but don't check level up here
            return f"{character['Name']} defeated {monster['Name']}! You receive {monster['XpReward']} XP."

        # Monster attacks back
        damage_to_player = max(monster['Attack'] - character['Defense'], 1)  # Ensure no zero damage
        print(f"Damage to {character['Name']} from {monster['Name']}: {damage_to_player}")
        take_damage(character['Name'], damage_to_player)  # Apply damage to the player
        print(f"{character['Name']} has {character['Health']} health remaining after taking damage")

        # Check if player is dead
        if character['Health'] <= 0:
            character['Health'] = 0  # Prevent character health from going negative
            return f"{character['Name']} was defeated by {monster['Name']}... You lose the battle."

        # Optionally, you can add a small delay between rounds for visual effect
        await asyncio.sleep(1)

    return "Battle ended unexpectedly."
            

@client.command() # Command to start the game and create your character.
async def start(ctx):
    user_id = str(ctx.author.id)

    # Checks if the user already has a character
    if user_id in characters:
        await ctx.send(f"You already have a character, {ctx.author.name}.")
        return
    
    # Asks the user to input their name
    await ctx.send(f"Welcome adventurer! Please write down your preferred name in the guild list:") 

    def check(msg):
        return msg.author == ctx.author and len(msg.content) > 0  # Checks if the message is from the user and not empty
    
    try:
        # Wait for the user's response for the custom name
        name_msg = await client.wait_for('message', check=check, timeout=30.0)  # Timeout after 30 seconds
        custom_name = name_msg.content # Sets the custom name to what the user has said

        # Create the character with the custom name
        create_character(user_id, custom_name)
        await ctx.send(f"Adventurer {custom_name} has joined the guild! You can now go out and slay monsters for the guild.")

    except asyncio.TimeoutError: # Output for when the user takes longer than 30 seconds to say a name
        await ctx.send("You took too long to choose a name. Please try again.")

@client.command() # Command to show the users profile
async def profile(ctx):
    user_id = str(ctx.author.id)

    if user_id not in characters: # Checks if the user is in the json file
        await ctx.send(f"Sorry adventurer, you are not enlisted in the guild. Please register with `.start`.") # If not tells them to create a character
        return
    
    character = characters[user_id]

    xp_bar_length= 15 # Sets the size of the xpbar
    xp_progress = character['Xp'] / character['XpToLevelUp'] # Sets how far the user is into leveling
    xp_filled = int(xp_progress * xp_bar_length) # Sets how far the bar will be filled
    xp_empty = xp_bar_length - xp_filled # Sets the amount of empty spaces in the bar

    xp_bar = f"[{'#' * xp_filled}{' ' * xp_empty}] {character['Xp']} / {character['XpToLevelUp']}" # String to show how far the user is into leveling

    # String to display the users profile
    profile_message = (
        f"**Profile of {character['Name']}**\n" # Says who's profile it is
        f"**Level:** {character['Level']}\n" # Says the level of the user
        f"**Xp:** {xp_bar}\n" # Shows the xp bar of the user
        f"**Health:** {character['Health']}/{character['MaxHealth']}\n" # Says the health and maxhealth of the user
        f"**Defense:** {character['Defense']}\n" # How much defense the user has
        f"**Attack:** {character['Attack']}\n" # How much attack the user has
        f"**Inventory:** {', '.join(character['Inventory']) if character['Inventory'] else 'Is empty'}" # The items the user has in his inventory
    )

    await ctx.send(profile_message)

@client.command()
async def fight(ctx, area: str):
    user_id = str(ctx.author.id)

    if user_id not in characters:
        await ctx.send(f"Sorry adventurer, you have to join the guild to hunt monsters (.start)")
        return

    character = characters[user_id]
    monster = Spawn_Monster(area)

    if not monster:
        await ctx.send(f"Somebody already took all the bounty's for this area. Please try another one")
        return

    print(f"Character: {character['Name']} - Monster: {monster['Name']}")  # Debugging

    # Debug: Ensure the battle function is being called
    await ctx.send(f"A wild {monster['Name']} has appeared! Prepare for battle.")

    result = await battle(character, monster)
    await ctx.send(result)

    if Check_Level_Up(character['Name']):
        await ctx.send(f"Congratulations {character['Name']}! You have leveled up!")
        save_characters()

@client.command()
async def testlevelup(ctx):
    
    user_id = str(ctx.author.id)

    print(f"Test level-up command triggered for user {user_id}")  # Debugging: Confirm command is triggered

    if user_id not in characters:
        await ctx.send("You need to join the guild first. Use `.start` to create your character.")
        return

    character = characters[user_id]

    # Manually increase XP to trigger level-up
    character['Xp'] = character['XpToLevelUp'] + 1  # Ensure XP exceeds XPToLevelUp

    print(f"Manual XP set for {user_id}: {character['Xp']}")  # Debugging

    if Check_Level_Up(character['Name']):
        await ctx.send(f"Level-up successful! New stats: Level {character['Level']}, Attack {character['Attack']}, Health {character['Health']}")
    else:
        await ctx.send("Level-up failed.")

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