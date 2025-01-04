import discord #type: ignore
from discord.ext import commands #type: ignore
from discord.ext.commands import cooldown, BucketType #type: ignore
import asyncio
import json
from pathlib import Path
from database import Database
import random
from dotenv import load_dotenv #type: ignore
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("Error: No Discord token found in .env file")
    exit(1)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='.', intents=intents)
db = Database()

# Get the directory where the bot.py script is located
BOT_DIR = Path(__file__).parent
DATA_DIR = BOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Load game data
try:
    with open(DATA_DIR / 'areas.json', 'r') as f:
        areas = json.load(f)
    with open(DATA_DIR / 'items.json', 'r') as f:
        items = json.load(f)
    print("Game data loaded successfully")
except FileNotFoundError as e:
    print(f"Error: Required JSON file not found - {e}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON format - {e}")
    exit(1)

@client.event
async def on_ready():
    await client.chance_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Over the guild"))
    print(f'Logged in as {client.user}')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in (error.retry_after:.2f)s")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `.help` to see available commands.")


@client.command()
@cooldown(1, 5, BucketType.user)
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="list of the available commands",
        color=discord.Color.Purple()
    )

    embed.add_field(name=".start", value="Enlist in the guild to start your adventure in Azefarnia", inline=False)
    embed.add_field(name=".profile", value="View your character's profile", inline=False)
    embed.add_field(name=".shop", value="View the items that are aviable in the local shop", inline=False)
    embed.add_field(name=".buy <item>", value="Buy an item from the shop", inline=False)
    embed.add_field(name=".sell <item>", value="Sell an item to the shop", inline=False)
    embed.add_field(name=".equip <item>", value="Equip an item from your inventory", inline=False)
    embed.add_field(name=".unequip <slot>", value="Unequip an item from a slot", inline=False)
    embed.add_field(name=".fight", value="Fight a monster in the current area", inline=False)



@client.command()
@cooldown(1, 5, BucketType.user)
async def start(ctx):
    user_id = str(ctx.author.id)
    if db.get_character(user_id):
        await ctx.send("You already have a character!")
        return

    await ctx.send("Welcome to the guild! What's your character's name?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        if db.create_character(user_id, msg.content):
            embed = discord.Embed(
                title="Welcome to the guild!",
                description=f"Welcome, {msg.content}! Your adventure begins now.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("There was an error creating your character.")
    except asyncio.TimeoutError:
        await ctx.send("Character creation canceled - you took too long to respond.")

@client.command()
@cooldown(1, 5, BucketType.user)
async def profile(ctx):
    character = db.get_character(str(ctx.author.id))
    if not character:
        await ctx.send("You don't have a character! Use `.start` to create one.")
        return

    embed = discord.Embed(title=f"{character['name']}'s Profile", color=discord.Color.blue())
    embed.add_field(name="Level", value=character['level'], inline=True)
    embed.add_field(name="XP", value=f"{character['xp']}/{character['xp_to_level']}", inline=True)
    embed.add_field(name="Health", value=f"{character['health']}/{character['max_health']}", inline=True)
    embed.add_field(name="Attack", value=character['attack'], inline=True)
    embed.add_field(name="Defense", value=character['defense'], inline=True)
    embed.add_field(name="Coins", value=character['coins'], inline=True)
    

    inventory = character['inventory']
    if inventory:
        inv_text = "\n".join([f"{item}: {qty}" for item, qty in inventory.items()])
    else:
        inv_text = "Empty"
    embed.add_field(name="Inventory", value=inv_text, inline=False)

    equipment = character['equipment']
    equip_text = "\n".join([f"{slot.title()}: {item or 'Empty'}" for slot, item in equipment.items()])
    embed.add_field(name="Equipment", value=equip_text, inline=False)

    embed.set_footer(text=f"Current Area: {character['current_area']}")
    await ctx.send(embed=embed)

@client.command()
@cooldown(1, 30, BucketType.user)
async def resetdata(ctx):
    user_id = str(ctx.author.id)
    if not db.get_character(user_id):
        await ctx.send("You don't have a character to reset!")
        return

    embed = discord.Embed(
        title="Character Reset",
        description="Are you sure you want to reset your character? This action cannot be undone.\nType 'yes' to confirm.",
        color=discord.Color.red()
    )
    msg = await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'yes'

    try:
        await client.wait_for('message', timeout=30.0, check=check)
        if db.delete_character(user_id):
            await ctx.send("Your character has been reset. Use `.start` to create a new one!")
        else:
            await ctx.send("There was an error resetting your character.")
    except asyncio.TimeoutError:
        await ctx.send("Reset canceled - you took too long to respond.")

@client.command()
@cooldown(1, 10, BucketType.user)
async def fight(ctx):
    character = db.get_character(str(ctx.author.id))
    if not character:
        await ctx.send("You need a character to fight! Use `.start` to create one.")
        return

    current_area = character['current_area']
    area_monsters = areas['areas'].get(current_area, {}).get('monsters', [])
    if not area_monsters:
        await ctx.send(f"No monsters to fight in {current_area}!")
        return

    monster = random.choice(area_monsters)
    monster_hp = monster['health']
    char_hp = character['health']

    embed = discord.Embed(
        title=f"Combat: {character['name']} vs {monster['name']}",
        color=discord.Color.red()
    )
    embed.add_field(name="Your HP", value=char_hp)
    embed.add_field(name=f"{monster['name']}'s HP", value=monster_hp)
    battle_msg = await ctx.send(embed=embed)

    while monster_hp > 0 and char_hp > 0:
   
        damage = max(1, character['attack'] - monster['defense'])
        monster_hp -= damage
        
        if monster_hp > 0:
            monster_damage = max(1, monster['attack'] - character['defense'])
            char_hp -= monster_damage

        embed = discord.Embed(
            title=f"Combat: {character['name']} vs {monster['name']}",
            color=discord.Color.red()
        )
        embed.add_field(name="Your HP", value=char_hp)
        embed.add_field(name=f"{monster['name']}'s HP", value=max(0, monster_hp))
        await battle_msg.edit(embed=embed)
        await asyncio.sleep(1)

    if char_hp > 0:
        xp_gain = monster['xp_reward']
        coins_gain = monster['coin_reward']
        
        updates = {
            'health': char_hp,
            'xp': character['xp'] + xp_gain,
            'coins': character['coins'] + coins_gain
        }

        if updates['xp'] >= character['xp_to_level']:
            updates['level'] = character['level'] + 1
            updates['xp'] = 0
            updates['xp_to_level'] = character['xp_to_level'] * 1.5
            updates['max_health'] = character['max_health'] + 20
            updates['attack'] = character['attack'] + 5
            updates['defense'] = character['defense'] + 3
            level_up = True
        else:
            level_up = False

        db.update_character(str(ctx.author.id), updates)

        # Handle loot
        if 'loot_table' in monster:
            for item, chance in monster['loot_table'].items():
                if random.random() < chance:
                    inventory = character['inventory']
                    inventory[item] = inventory.get(item, 0) + 1
                    db.update_character(str(ctx.author.id), {'inventory': inventory})

        result = f"Victory! Gained {xp_gain} XP and {coins_gain} coins."
        if level_up:
            result += f"\nLevel Up! You are now level {updates['level']}!"
            
        await ctx.send(result)
    else:
        db.update_character(str(ctx.author.id), {'health': character['max_health']})
        await ctx.send("You were defeated! Your health has been restored.")

@client.command()
@cooldown(1, 5, BucketType.user)
async def shop(ctx):
    shop_items = items['shop']
    pages = []
    items_per_page = 5
    
    for i in range(0, len(shop_items), items_per_page):
        embed = discord.Embed(title="Shop", color=discord.Color.gold())
        page_items = shop_items[i:i + items_per_page]
        
        for item in page_items:
            embed.add_field(
                name=f"{item['name']} - {item['buy_price']} coins",
                value=f"Type: {item['type']}\nEffect: {item['effect']}\n{item['description']}",
                inline=False
            )
        pages.append(embed)
    
    current_page = 0
    message = await ctx.send(embed=pages[current_page])
    
    if len(pages) > 1:
        await message.add_reaction('⬅️')
        await message.add_reaction('➡️')
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']
            
        while True:
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
                
                if str(reaction.emoji) == '➡️':
                    current_page = (current_page + 1) % len(pages)
                elif str(reaction.emoji) == '⬅️':
                    current_page = (current_page - 1) % len(pages)
                    
                await message.edit(embed=pages[current_page])
                await message.remove_reaction(reaction, user)
                
            except asyncio.TimeoutError:
                break

@client.command()
@cooldown(1, 5, BucketType.user)
async def buy(ctx, *, item_name: str):
    character = db.get_character(str(ctx.author.id))
    if not character:
        await ctx.send("You need a character first! Use `.start` to create one.")
        return
        
    shop_items = items['shop']
    item = next((item for item in shop_items if item['name'].lower() == item_name.lower()), None)
    
    if not item:
        await ctx.send("That item doesn't exist in the shop!")
        return
        
    if character['coins'] < item['buy_price']:
        await ctx.send("You don't have enough coins!")
        return
        
    inventory = character['inventory']
    inventory[item['name']] = inventory.get(item['name'], 0) + 1
    
    updates = {
        'inventory': inventory,
        'coins': character['coins'] - item['buy_price']
    }
    
    db.update_character(str(ctx.author.id), updates)
    await ctx.send(f"You bought {item['name']} for {item['buy_price']} coins!")

@client.command()
@cooldown(1, 5, BucketType.user)
async def sell(ctx, *, item_name: str):
    character = db.get_character(str(ctx.author.id))
    if not character:
        await ctx.send("You need a character first! Use `.start` to create one.")
        return
        
    inventory = character['inventory']
    if item_name not in inventory or inventory[item_name] <= 0:
        await ctx.send("You don't have that item!")
        return
        
    shop_items = items['shop']
    item = next((item for item in shop_items if item['name'].lower() == item_name.lower()), None)
    
    if not item:
        await ctx.send("That item cannot be sold!")
        return
        
    sell_price = item['buy_price'] // 2
    inventory[item_name] -= 1
    
    if inventory[item_name] <= 0:
        del inventory[item_name]
        
    updates = {
        'inventory': inventory,
        'coins': character['coins'] + sell_price
    }
    
    db.update_character(str(ctx.author.id), updates)
    await ctx.send(f"You sold {item_name} for {sell_price} coins!")

@client.command()
@cooldown(1, 5, BucketType.user)
async def equip(ctx, *, item_name: str):
    character = db.get_character(str(ctx.author.id))
    if not character:
        await ctx.send("You need a character first! Use `.start` to create one.")
        return

    inventory = character['inventory']
    if item_name not in inventory:
        await ctx.send("You don't have that item!")
        return

    shop_items = items['shop']
    item = next((item for item in shop_items if item['name'].lower() == item_name.lower()), None)
    
    if not item or 'slot' not in item:
        await ctx.send("That item cannot be equipped!")
        return

    equipment = character['equipment']
    slot = item['slot']

    if equipment[slot]:
        old_item = equipment[slot]
        inventory[old_item] = inventory.get(old_item, 0) + 1

    equipment[slot] = item_name
    inventory[item_name] -= 1
    if inventory[item_name] <= 0:
        del inventory[item_name]

    base_stats = {
        'attack': 10,
        'defense': 5,
        'max_health': 100
    }

    for equipped_item in equipment.values():
        if equipped_item:
            item_data = next((i for i in shop_items if i['name'] == equipped_item), None)
            if item_data and 'effect' in item_data:
                for stat, value in item_data['effect'].items():
                    base_stats[stat.lower()] += value

    updates = {
        'equipment': equipment,
        'inventory': inventory,
        'attack': base_stats['attack'],
        'defense': base_stats['defense'],
        'max_health': base_stats['max_health']
    }

    db.update_character(str(ctx.author.id), updates)
    await ctx.send(f"Equipped {item_name} in {slot} slot!")

@client.command()
@cooldown(1, 5, BucketType.user)
async def unequip(ctx, slot: str):
    character = db.get_character(str(ctx.author.id))
    if not character:
        await ctx.send("You need a character first! Use `.start` to create one.")
        return

    equipment = character['equipment']
    slot = slot.lower()
    
    if slot not in equipment:
        await ctx.send("Invalid equipment slot!")
        return

    if not equipment[slot]:
        await ctx.send("Nothing equipped in that slot!")
        return

    inventory = character['inventory']
    item_name = equipment[slot]
    inventory[item_name] = inventory.get(item_name, 0) + 1
    equipment[slot] = None

    # Recalculate stats
    base_stats = {
        'attack': 10,
        'defense': 5,
        'max_health': 100
    }

    shop_items = items['shop']
    for equipped_item in equipment.values():
        if equipped_item:
            item_data = next((i for i in shop_items if i['name'] == equipped_item), None)
            if item_data and 'effect' in item_data:
                for stat, value in item_data['effect'].items():
                    base_stats[stat.lower()] += value

    updates = {
        'equipment': equipment,
        'inventory': inventory,
        'attack': base_stats['attack'],
        'defense': base_stats['defense'],
        'max_health': base_stats['max_health']
    }

    db.update_character(str(ctx.author.id), updates)
    await ctx.send(f"Unequipped {item_name} from {slot} slot!")

# Error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f}s")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `.help` to see available commands.")
    else:
        print(f"Error: {error}")
        await ctx.send("An error occurred while processing your command.")


client.run(TOKEN)
