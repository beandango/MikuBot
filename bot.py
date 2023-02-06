from doctest import debug_script
from pydoc import describe
from ssl import CERT_NONE
import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import Button, View
import motor
import motor.motor_asyncio
import random
import asyncio


client = commands.Bot()

# -=-=-=-=-=-=-=- Database Connections

cluster = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://beandango:147896342sarah@maindata.oogqgqc.mongodb.net/discord?retryWrites=true&w=majority")
db = cluster.discord
collection = db.bank
inv = db.inv 

@client.event
async def on_ready():
    print(f'{client.user} is online!')

# -=-=-=-=-=- calculator/basic tests

@client.slash_command(name='add', description='Add numbers!', guild_ids=[851961510200606770])
async def add(ctx, num1, num2):
    await ctx.respond(f'{num1} + {num2} = {int(num1)+int(num2)}!')

@client.slash_command(name='subtract', description='Substract numbers!', guild_ids=[851961510200606770])
async def add(ctx, num1, num2):
    await ctx.respond(f'{num1} - {num2} = {int(num1)-int(num2)}!')

@client.slash_command(name='multiply', description='Multiply numbers!', guild_ids=[851961510200606770])
async def add(ctx, num1, num2):
    await ctx.respond(f'{num1} x {num2} = {int(num1)*int(num2)}!')

@client.slash_command(name='divide', description='Divide numbers!', guild_ids=[851961510200606770])
async def add(ctx, num1, num2):
    await ctx.respond(f'{num1} / {num2} = {int(num1)/int(num2)}!')

@client.message_command(name='repeat')
async def repeat(ctx, msg: discord.Message):
    await ctx.respond(msg.content)

@client.user_command(name='Joined Date')
async def joinedat(ctx, user: discord.Member):
    await ctx.respond(f'{user.mention} joined the server on <t:{user.joined_at.timestamp():.0f}:f>', ephemeral = True)

@client.slash_command(name='buttontest', description='Testing buttons', guild_ids=[851961510200606770])
async def button(ctx):
    button1 = Button(
        label = 'uwu',
        style = discord.ButtonStyle.blurple,
        emoji='😘'
    )
    buttonlink = Button(
        label='Go to link',
        url='https://www.youtube.com/watch?v=yPuI4l0jK7s'
    )

    view = View()
    view.add_item(button1)
    view.add_item(buttonlink)

    embed = discord.Embed(
        title='The Gospel',
        description = "Observe the holy scripture",
        color=discord.Color.random()
    )
    embed.set_author(name='Miku')
    embed.set_thumbnail(url='https://i.kym-cdn.com/entries/icons/original/000/013/638/Miku_Domino_Pizza_App.png')
    embed.set_image(url='https://www.cultofmac.com/wp-content/uploads/2013/03/post-219201-image-a8ff209e6bc5e045dedf9d8de1ec7391.jpg?ezimgfmt=ng:webp/ngcb24')

    async def button1callback(interaction: discord.Interaction):
        if interaction.user!=ctx.author:
            await interaction.response.send_message('This button is not for you!', ephemeral=True)
        if interaction.user==ctx.author:
            button1.disabled=True
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send('uwu???? W-whats that??? ***notices ur buldgey-wuldgey***~~~') 
        
    button1.callback = button1callback
    await ctx.respond(embed = embed, view = view)

class DropDownPoopMenu(discord.ui.View):
    @discord.ui.select(placeholder='Will you poop?', min_values=1, max_values=1, options=[
        discord.SelectOption(label='Yes', description='I will poop', emoji='💩'),
        discord.SelectOption(label='No', description='I will not poop', emoji='😠')
    ])
    async def callback(self, select, interaction: discord.Interaction):
        await interaction.response.send_message(f'You have chosen "{select.values[0]}"', ephemeral=True) 
        if select.values[0] == 'No':
            noembed = discord.Embed(
                title='No',
                description="I will NOT poop",
                color=discord.Color.red()
            )
            noembed.set_author(name='Miku')
            noembed.set_image(url='https://c.tenor.com/DTpTIwK3ScgAAAAM/angry-mad.gif')
            noembed.set_thumbnail(url='https://us.123rf.com/450wm/momoforsale/momoforsale2009/momoforsale200900031/156161790-no-pooping-sign-isolated-on-white-background-vector-illustration-.jpg?ver=6')

            await interaction.followup.send(embed=noembed)

        if select.values[0] == 'Yes':            
            yesembed = discord.Embed(
            title='Yes',
            description='I WILL INDEED poop',
            color=discord.Color.green()
            )
            yesembed.set_author(name='Miku')
            yesembed.set_image(url='https://static8.depositphotos.com/1004529/988/i/450/depositphotos_9887128-stock-photo-sharpei-dog.jpg')
            yesembed.set_thumbnail(url='https://askthescientists.com/wp-content/uploads/2021/04/AdobeStock_240042551-835x835.jpeg')

            await interaction.followup.send(embed=yesembed)

@client.slash_command(name='dropdowntest', description='testing dropdowns', guild_ids=[851961510200606770])
async def dropdown(ctx):
    sample = discord.Embed(
        title='Will you poop?',
        color=discord.Color.nitro_pink()
    )
    dropdowns=DropDownPoopMenu()
    if ctx.user != ctx.author:
        await ctx.respond.followup('This is not for you, smelly',ephemeral=True)
    await ctx.respond(embed=sample, view=dropdowns)


# -=-=-=-=-=-=-= Economy

class BankView(View):

    # Withdraw Button

    @discord.ui.button(label="Withdraw", style=discord.ButtonStyle.red)
    async def button_callback(self, button1, interaction: discord.Interaction):
        button1.disabled = True
        member = interaction.user
        findbank = await collection.find_one({"_id": member.id})
        if not findbank:
            await interaction.response.send_message("You don't currently have an account!\nPlease use `/start` to open up an account.")
        
        wallet = findbank['wallet']
        bankamnt = findbank['bank']
        money = bankamnt

        updated_wallet = wallet + int(money)
        updated_bank = bankamnt - int(money)

        if int(money) > bankamnt:
            await interaction.response.send_message("You don't have enough Mikoins in the bank for that lmao", ephemeral=True)

        if int(money) <= 0:
            await interaction.response.send_message("You can't withdraw negative or non-existent money", ephemeral=True)
        
        if int(money)<=bankamnt and int(money)>0:
            await collection.update_one({"_id": member.id}, {"$set": {"wallet": updated_wallet}})
            await collection.update_one({"_id": member.id}, {"$set": {"bank": updated_bank}})
            
            wdembed = discord.Embed(
            title=f"**{member.display_name}'s balance**",
            color = discord.Color.random()
            )
            wdembed.add_field(name="Bank", value=f"{str(updated_bank)}", inline=True)
            wdembed.add_field(name="Wallet", value=f"{str(updated_wallet)}", inline=True)
            wdembed.set_author(name=f"Successfully withdrew {money} Mikoins from your bank!")

            await interaction.response.edit_message(embed = wdembed)

    # Deposit button 

    @discord.ui.button(label="Desposit Wallet", style=discord.ButtonStyle.blurple)
    async def button2_callback(self, button2, interaction: discord.Interaction):
        button2.disabled=True
        member = interaction.user
        findbank = await collection.find_one({'_id': member.id})
        if not findbank:
            await interaction.response.send_message("You don't currently have an account!\nPlease use `/start` to open up an account.")
        
        wallet = findbank['wallet']
        bankamnt = findbank['bank']
        money = wallet

        updated_wallet = wallet - int(money)
        updated_bank = bankamnt + int(money)

        if int(money) > wallet:
            await interaction.response.send_message("You don't have enough Mikoins for that lmao", ephemeral=True)

        if int(money) <= 0:
            await interaction.response.send_message("You can't deposit negative or non-existent money", ephemeral=True)
        
        if int(money)<=wallet and int(money)>0:
            await collection.update_one({"_id": member.id}, {"$set": {"wallet": updated_wallet}})
            await collection.update_one({"_id": member.id}, {"$set": {"bank": updated_bank}})
            
            depositembed = discord.Embed(
            title=f"**{member.display_name}'s balance**",
            color = discord.Color.random()
            )
            depositembed.add_field(name="Bank", value=f"{str(updated_bank)}", inline=True)
            depositembed.add_field(name="Wallet", value=f"{str(updated_wallet)}", inline=True)
            depositembed.set_author(name=f"Successfully deposited {money} Mikoins into your bank!")

            await interaction.response.edit_message(embed = depositembed)



@client.slash_command(name='start', description='Open up a bank account with Miku')
async def start(ctx):
    member = ctx.author
    findbank = await collection.find_one({'_id': member.id})
    if findbank:
        await ctx.respond('You already have an account, silly', ephemeral=True)
    if not findbank:
        await collection.insert_one({'_id': member.id, 'bank':0, 'wallet':50})
        await ctx.respond("Welcome to the bank! Here's 50 Mikoins to get started.\nUse `/bank` to see your balance.")




# -=-=-=-=-=-=-= bank

@client.slash_command(name='bank', description='check your wallet', guild_ids=[851961510200606770])
async def bank(ctx):
    member = ctx.author

    findbank = await collection.find_one({'_id': member.id})
    if not findbank:
        await ctx.respond("You don't currently have an account!\nPlease use `/start` to open up an account.")

    amnt = findbank['bank']
    wallet = findbank['wallet']
    embed = discord.Embed(
        title=f"**{member.display_name}'s balance**",
        color = discord.Color.random()
    )
    depositbutton = Button(
        label="Deposit Wallet",
        style=discord.ButtonStyle.blurple
    )

    view = BankView()

    embed.add_field(name="Bank", value=f"{str(amnt)}", inline=True)
    embed.add_field(name="Wallet", value=f"{str(wallet)}", inline=True)
    await ctx.respond(embed=embed, view=view)

# -=-=-=-=-=-=-= beg

@client.slash_command(name='beg', description='beg for free money', guild_ids=[851961510200606770])
async def beg(ctx):
    member=ctx.author
    findbank = await collection.find_one({'_id': member.id})
    if not findbank:
        await ctx.respond("You don't currently have an account!\nPlease use `/start` to open up an account.")

    begagain = Button(
        label="Beg Again",
        style=discord.ButtonStyle.blurple
    )

    
    begview = View()
    begview.add_item(begagain)

    async def bacallback(interaction: discord.Interaction):
        if interaction.user!=ctx.author:
            await interaction.response.send_message('This button is not for you!', ephemeral=True)
        if interaction.user==ctx.author:
            begagain.disabled=True
            await beg(ctx)
            await interaction.response.edit_message(view=begview)
            
    begagain.callback=bacallback

    wallet = findbank["wallet"]

    luck=random.randint(1,100)
    random_luckymoney = random.randint(700, 1000)
    random_kindaluckymoney = random.randint(1, 400)
    random_unluckymoney = random.randint(1, 700)

    if luck >= 90:
        
        updated_money = wallet + random_luckymoney
        await collection.update_one({"_id": member.id}, {"$set": {"wallet": updated_money}})

        luckyembed = discord.Embed(
        title="Miku's in a good mood!",
        description=f"Your wallet has increased by {random_luckymoney}"
        )

        luckyembed.set_footer(text=f"Wallet: {updated_money}")
        luckyembed.set_thumbnail(url='https://c.tenor.com/CNNcfjuEpMQAAAAj/miku.gif')


        await ctx.respond(embed=luckyembed, view=begview)

    if 60 <= luck < 90:
        
        updated_money = wallet + random_kindaluckymoney
        await collection.update_one({"_id": member.id}, {"$set": {"wallet": updated_money}})

        luckyembed = discord.Embed(
        title="Miku has taken a liking to you...",
        description=f"Your wallet has increased by {random_kindaluckymoney}"
        )

        luckyembed.set_footer(text=f"Wallet: {updated_money}")
        luckyembed.set_thumbnail(url='https://cdn.discordapp.com/attachments/997334759170658434/998856851028463656/Stamp0234.webp')


        await ctx.respond(embed=luckyembed, view=begview)

    if 10< luck < 60:
        nochangeembed = discord.Embed(
        title="Beg all you want...",
        description=f"but your begging falls on deaf ears."
        )

        nochangeembed.set_footer(text=f"Wallet: {wallet}")
        nochangeembed.set_thumbnail(url='https://media.discordapp.net/attachments/997334759170658434/998856955797983332/Stamp0235.webp?width=266&height=230')


        await ctx.respond(embed=nochangeembed, view=begview)

    if luck <= 10:
        
        updated_money = wallet - random_unluckymoney
        await collection.update_one({"_id": member.id}, {"$set": {"wallet": updated_money}})

        unluckyembed = discord.Embed(
        title="Miku laughs at your misfortune...",
        description=f"Your wallet has decreased by {random_unluckymoney}"
        )

        unluckyembed.set_footer(text=f"Wallet: {updated_money}")
        unluckyembed.set_thumbnail(url='https://cdn.discordapp.com/attachments/997334759170658434/998856928258183178/Stamp0233.webp')


        await ctx.respond(embed=unluckyembed, view=begview)


# -=-=-=-=-=-=- Deposit 

@client.slash_command(name='deposit', description='deposit money to your bank', guild_ids=[851961510200606770])
async def deposit(ctx, money):
    member = ctx.author
    findbank = await collection.find_one({'_id': member.id})
    if not findbank:
        await ctx.respond("You don't currently have an account!\nPlease use `/start` to open up an account.")
    
    wallet = findbank['wallet']
    bankamnt = findbank['bank']

    updated_wallet = wallet - int(money)
    updated_bank = bankamnt + int(money)

    if int(money) > wallet:
        await ctx.respond("You don't have enough Mikoins for that lmao", ephemeral=True)

    if int(money) <= 0:
        await ctx.respond("You can't deposit negative or non-existent money", ephemeral=True)
    
    if int(money)<=wallet and int(money)>0:
        await collection.update_one({"_id": member.id}, {"$set": {"wallet": updated_wallet}})
        await collection.update_one({"_id": member.id}, {"$set": {"bank": updated_bank}})
        
        depositembed = discord.Embed(
        title=f"**{member.display_name}'s balance**",
        color = discord.Color.random()
        )
        depositembed.add_field(name="Bank", value=f"{str(updated_bank)}", inline=True)
        depositembed.add_field(name="Wallet", value=f"{str(updated_wallet)}", inline=True)
        depositembed.set_author(name=f"Successfully deposited {money} Mikoins into your bank!")

        await ctx.respond(embed = depositembed, ephemeral=True)

# -=-=-=-=-=- Withdraw


            





@client.slash_command(name='withdraw', description='Withdraw Mikoins from your bank', guild_ids=[851961510200606770])
async def withdraw(ctx, money):
    member = ctx.author
    findbank = await collection.find_one({"_id": member.id})
    if not findbank:
        await ctx.respond("You don't currently have an account!\nPlease use `/start` to open up an account.")
    
    wallet = findbank["wallet"]
    bankamnt = findbank["bank"]

    updated_wallet = wallet + int(money)
    updated_bank = bankamnt - int(money)

    if int(money) > bankamnt:
        await ctx.respond("You don't have enough Mikoins in the bank for that lmao", ephemeral=True)

    if int(money) <= 0:
        await ctx.respond("You can't withdraw negative or non-existent money", ephemeral=True)
    
    if int(money)<=bankamnt and int(money)>0:
        await collection.update_one({"_id": member.id}, {"$set": {"wallet": updated_wallet}})
        await collection.update_one({"_id": member.id}, {"$set": {"bank": updated_bank}})
        
        wdembed = discord.Embed(
        title=f"**{member.display_name}'s balance**",
        color = discord.Color.random()
        )
        wdembed.add_field(name="Bank", value=f"{str(updated_bank)}", inline=True)
        wdembed.add_field(name="Wallet", value=f"{str(updated_wallet)}", inline=True)
        wdembed.set_author(name=f"Successfully withdrew {money} Mikoins from your bank!")

        await ctx.respond(embed = wdembed, ephemeral=True)

# -=-=-=-=-=-=-=- fishing

fishpool = ['Squid :squid:', 'Shark :shark:', 'Whale :whale:', 'Lobster :lobster:', 'Octopus :octopus:',
 'Dolphin :dolphin:', 'Seal :seal:', 'Fish :fish:']


@client.slash_command(name="fish", description="Go fishing!", guild_ids=[851961510200606770])
async def fish(ctx):
    member = ctx.author
    findinv = await inv.find_one({"_id": member.id})
    if not findinv:
        await inv.insert_one({'_id': member.id, 'fish':[]})

    fishagain = Button(label="Fish again", style=discord.ButtonStyle.blurple, emoji = '🐟')

    fishview = View()
    fishview.add_item(fishagain)

    async def fishcallback(interaction: discord.Interaction):
            if interaction.user!=ctx.author:
                await interaction.response.send_message('This button is not for you!', ephemeral=True)
            if interaction.user==ctx.author:
                await fish(ctx)
            fishagain.disabled=True
            
    fishagain.callback=fishcallback

    fishroll = random.randint(0, 21)
    if fishroll <=7:
        fishinv = findinv['fish']
        updated_fishinv = fishinv.append(fishpool[fishroll])
        
        await inv.update_one({"_id": member.id}, {"$set": {"fish": fishinv}})
        countedfish={}
        for i in fishinv:
            countedfish[i] = fishinv.count(i)

        columnedfish = str(countedfish).replace(", '", "\n").replace("{'", "").replace("}", "").replace("'", "")
        
        ResultEmbed = discord.Embed(
            title=f"{member.name} caught {fishpool[fishroll]}!",
            description=f"You now have:\n\n{columnedfish}"
        )
        ResultEmbed.set_thumbnail(url='https://c.tenor.com/CNNcfjuEpMQAAAAj/miku.gif')
        FishEmbed = discord.Embed()
        FishEmbed.set_image(url='https://c.tenor.com/ZJkVnDWN-VwAAAAC/inazuma-eleven-go-inago.gif')

        await ctx.respond(embed = FishEmbed, delete_after=5)
        await asyncio.sleep(5)
        await ctx.followup.send(f'{member.mention}', embed=ResultEmbed, view = fishview)

    elif fishroll > 7:
        FishEmbed = discord.Embed()
        FishEmbed.set_image(url='https://c.tenor.com/ZJkVnDWN-VwAAAAC/inazuma-eleven-go-inago.gif')

        nobite = discord.Embed(
            title='No biters... :('
        )
        nobite.set_image(url='https://i.gifer.com/embedded/download/Mpbv.gif')
        await ctx.respond(embed = FishEmbed, delete_after=5)
        await asyncio.sleep(5)
        await ctx.followup.send(f'{member.mention}', embed = nobite, view = fishview)

    
"""
@client.slash_command(name="inventory", description="check your inventory", guild_ids=[851961510200606770])
async def inventory(ctx):
    member = ctx.author
    findinv = await inv.find_one({"_id": member.id})
    if not findinv:
        await inv.insert_one({'_id': member.id, 'fish':[]})

    fishinv = findinv['fish']

    invembed = discord.Embed(
        title=f"{member.display_name}'s Inventory",
    )
    invembed.add_field(name="Fish", value = fishinv, inline = True)

    await ctx.respond(embed=invembed, ephemeral=True)
"""






    
    




client.run('TOKEN')
