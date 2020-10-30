import asyncio
import datetime
import discord
import time

client = discord.Client()
monitored_channels = []

# TODO:
# - Add error message if bot does not have sufficient permissions
# - Remove channels where bot does not have sufficient permissions
# - Add list command
# - Add the option to specify a time interval
# - Add a timeout to deletion (to avoid hanging too long on a single channel)
# - Check all the functions called to catch any potential exceptions
# - Write a command list
# - Implement proper logging lmfao

# Why did I decide to make this bot official, again?

stop = False
@client.event
async def on_ready():

    print('Setting activity...')
    act = discord.Game(name="Purge")
    await client.change_presence(activity=act)
    print('Logged on as {0}!'.format(client.user))

    with open("channels.txt", 'r') as fh:
        for line in fh.readlines():
            monitored_channels.append(int(line))

    print("read from file:", monitored_channels)
    client.loop.create_task(run())

@client.event
async def on_message(message):
    # It's incredible how little I can be assed to do this the smart way.
    is_enable = message.content.startswith("purge!enable")
    is_disable = message.content.startswith("purge!disable")
    is_list = message.content.startswith("purge!list")
    is_command =  message.content.startswith("purge!")
    if is_command:
        channel = message.channel
        if type(channel) == discord.TextChannel:
            user = message.author
            perms = user.permissions_in(channel)
            if perms.administrator or perms.manage_messages: # Check Permissions
                if is_enable and message.channel.id not in monitored_channels:
                    monitored_channels.append(message.channel.id)
                    return
                if is_disable and message.channel.id in monitored_channels:
                    monitored_channels.remove(message.channel.id)
                    return
                # Maybe I'll implement this one day
                if is_list:
                    return


async def run():

    # Not sure if the coroutine is automatically killed when the
    # task that spawned it dies. I should read up on that.
    # Until then, we'll have this jankass solution
    while not stop:

        # get all messages in monitored channels, delete them
        with open("channels.txt", "w") as fh:
            strings = [str(i) + "\n" for i in monitored_channels]
            print("writing to file:", strings)
            fh.writelines(strings)

        coroutines = []
        for monitored_channel in monitored_channels:
            channel = None
            for guild in client.guilds:
                for c in guild.text_channels:
                    if c.id == monitored_channel:
                        channel = c
            if channel is not None:
                cor = del_messages(channel)
                coroutines.append((monitored_channel,cor))
            else:
                monitored_channels.remove(monitored_channel)
                print("Could not find channel with id", monitored_channel)

        for channel, cor in coroutines:
            result = await cor

            if not result:
                monitored_channels.remove(channel)
                print("Insufficient permissions; removing channel")

        await asyncio.sleep(5)

async def del_messages(channel):
    # Fuuuuuck do I not wanna implement proper logging
    print("checking channel", channel)

    permission = True
    yesterday = datetime.datetime.now() - datetime.timedelta(hours = 24)
    try:
        await channel.purge(before = yesterday, limit = 20)
    except discord.HTTPException as e:
        print(f"Error occurred: {e}")
        if e.code == 50013: # 'Missing Permission'
            permission = False

    except discord.Forbidden as e:
        print(f"Error occurredaoeu: {e}")
        permission = False

    print("done")
    return permission

with open("token.txt", "r") as f:
    token = f.read()

client.run(token)
stop = True
