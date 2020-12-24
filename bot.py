#!/usr/bin/env python3
print(
    """Email Santa Discord Bot v. 1.0.0
Copyright (c) 2020 Félix An
Licensed under the GNU AGPL 3.0"""
)

# Standard library imports
import gc
import time

# Third-party library imports
import discord
from discord.ext import tasks
from discord.utils import find
from emailsanta import *


# Place token here
TOKEN = ""

gc.enable()
client = discord.Client()
wipLetters = {}
finishedLetters = {}


# Task to clear old letters every 5 minutes
@tasks.loop(seconds=30, count=None)
async def clearOldLetters():
    global wipLetters
    for user, data in list(wipLetters.items()):
        if time.time() - data["lastmodified"] > 300:
            await (client.get_user(user)).send(
                "> **Since you have not worked on your letter to Santa for more than 5 minutes, it has been automatically cleared to free up resources on the server.** To start again, go to a server with the bot and type `es!emailsanta`, or type it here to get Santa's reply in your DMs."
            )
            del wipLetters[user]
    gc.collect()


# Task to send out finished emails to Santa (this ensures that two emails don't clash with each other)
@tasks.loop()
async def sendFinishedLetters():
    global finishedLetters

    for user, letter in list(finishedLetters.items()):
        await client.get_channel(letter[0]).send(letter[1])
        for line in letter[2]:
            if len(line.strip()) >= 4:
                await client.get_channel(letter[0]).send(line)
        await client.get_channel(letter[0]).send(letter[3])
        del finishedLetters[user]


@client.event
async def on_ready():
    print("Connected to Discord at " + time.ctime())
    perms = discord.Permissions(3072)
    print(f"Invite link: {discord.utils.oauth_url(client.user.id, perms)}")
    activity = discord.Activity(
        name="to see who's naughty or nice", type=discord.ActivityType.watching
    )
    await client.change_presence(activity=activity)
    clearOldLetters.start()
    sendFinishedLetters.start()


# Welcome message when the bot joins a server
@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == "general", guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(
            "> **Merry Christmas! Thanks for adding the Email Santa Discord bot to {}!** Please try `es!help` for a list of commands.\n> Disclaimer: Santa Claus is not real and this bot is provided for entertainment purposes only.\n> Data is processed in accordance with emailSanta.com's privacy policy: <https://www.emailsanta.com/privacy.asp>".format(
                guild.name
            )
        )


@client.event
async def on_message(message):
    global wipLetters
    if message.author == client.user:
        return

    if message.content.startswith("es!"):
        argv = (message.content).split("!")[1].split()
        currentCommand = argv[0].lower() if len(argv) >= 1 else ""

        # TODO: do something based on the command
        if currentCommand == "emailsanta":
            if not message.author.id in wipLetters:
                try:
                    receivingLocation = 'the "' + message.guild.name + '" server'
                except:
                    receivingLocation = "your DMs"
                wipLetters[message.author.id] = {
                    "lastmodified": time.time(),
                    "replylocation": message.channel.id,
                    "receivinglocation": receivingLocation,
                    "letter_argv": [],
                }

                if message.guild:
                    await message.channel.send(
                        "> "
                        + message.author.mention
                        + ", go to your DMs and follow the prompts to write your letter to Santa. Once you have finished, come back here to see the reply."
                    )

                await message.author.send(
                    """> **TIME TO START writing your letter to Santa Claus!**
> Your original letter and Santa's reply will be sent in {}. If you are not comfortable with sharing real information with the members of that chat, you may make it up if you wish.
> If you make a mistake, type `es!cancel` and start again. Editing your previous messages will not edit the saved answers.
> Remember to use proper capitalization.
> First question: What is your FIRST name ONLY? (Do not enter your last name.)""".format(
                        receivingLocation
                    )
                )
            else:
                await message.channel.send(
                    "> {}, you are currently writing a letter to Santa. Finish it up first or cancel it by typing `es!cancel` before making a new one.".format(
                        message.author.mention
                    )
                )

        elif currentCommand == "cancel":
            try:
                del wipLetters[message.author.id]
                await message.channel.send(
                    "> {}, your responses have been cleared.".format(
                        message.author.mention
                    )
                )

            except:
                await message.channel.send(
                    "> {}, you are not currently sending a letter to Santa.".format(
                        message.author.mention
                    )
                )

        elif currentCommand == "help":
            await message.channel.send(
                """> **Email Santa Bot**
> 
> COMMANDS:
> >> `es!emailsanta` - Start an interactive prompt to write an email to Santa. Upon completion, the automated reply from Santa will be shown here.
> >> `es!cancel` - Clear your responses so you can start over again.
> >> `es!help` - Display this help message.
> >> `es!about` - Display information about the bot's software.
"""
            )

        elif currentCommand == "about":
            await message.channel.send(
                """> **Email Santa Bot**
> Version 1.0.0
> Discord Bot by Félix An - <https://www.felixan.tk/> - Copyright © 2020 Félix An. Licensed under the GNU AGPL 3.0. Source code: <https://github.com/fffelix-jan/emailSanta-discordbot>
> Uses the open source Python library "emailsanta", licensed under the GNU AGPL 3.0, also by Félix An: <https://github.com/fffelix-jan/emailsanta-py>
> Replies provided by Alan Kerr's "emailSanta.com" - <https://www.emailsanta.com/> - Copyright © 1997-2020 emailSanta.com Inc.
> 
> If you are having technical difficulties with this bot, contact Félix at fffelix.jan.yt (AT) gmail (POINT) com, or join this Discord server: <https://discord.gg/gag7S886Vp>
> DO NOT CONTACT EMAILSANTA.COM FOR SUPPORT WITH THIS BOT! THEY ARE NOT RESPONSIBLE FOR THE USAGE OR DEVELOPMENT OF THIS BOT. They are only responsible for the replies provided and the emailSanta.com website.
> 
> Disclaimer: Santa Claus is not real. Therefore, this bot is for entertainment purposes ONLY. I am not responsible for the content of the replies. They come from emailSanta.com.
> 
> Privacy: Your data will be sent to a third party for processing. The data will be sent to and stored at emailSanta.com for processing under their privacy policy: <https://www.emailsanta.com/privacy.asp>
> This bot itself only temporarily stores your personal information in RAM on my server. It is not saved to disk. Once you have finished your letter, or you have been inactive for more than 5 minutes, your information will immediately be cleared from my server."""
            )

        else:
            await message.channel.send(
                "> **Email Santa Bot** - Invalid command! To see a list of commands, type `es!help`"
            )

    else:
        if not message.guild:
            try:
                wipLetters[message.author.id]["lastmodified"] = time.time()
                if len(wipLetters[message.author.id]["letter_argv"]) == 1:
                    if message.content.isdigit():
                        if 1 <= int(message.content) <= 2:
                            wipLetters[message.author.id]["letter_argv"].append(
                                int(message.content)
                            )
                        else:
                            await message.channel.send(
                                "> The gender must be either 1 for boy or 2 for girl."
                            )
                    else:
                        await message.channel.send(
                            "> The gender must be an integer, and it must be either 1 for boy or 2 for girl."
                        )

                elif len(wipLetters[message.author.id]["letter_argv"]) == 2:
                    if message.content.isdigit():
                        wipLetters[message.author.id]["letter_argv"].append(
                            int(message.content)
                        )
                    else:
                        await message.channel.send("> The age must be an integer.")

                elif len(wipLetters[message.author.id]["letter_argv"]) == 5:
                    if message.content.isdigit():
                        if 0 <= int(message.content) <= 3:
                            wipLetters[message.author.id]["letter_argv"].append(
                                int(message.content)
                            )
                        else:
                            await message.channel.send(
                                "> Choose how good you are on a scale of either `0`, `1`, `2` or `3`, with `0` being naughtiest and `3` being nicest."
                            )
                    else:
                        await message.channel.send(
                            "> You must type an integer to rank how good you are. You can choose either `0`, `1`, `2` or `3`, with `0` being naughtiest and `3` being nicest."
                        )
                elif len(wipLetters[message.author.id]["letter_argv"]) == 9:
                    if message.content == "SKIP!":
                        wipLetters[message.author.id]["letter_argv"].append("")
                    else:
                        wipLetters[message.author.id]["letter_argv"].append(
                            message.content
                        )
                else:
                    wipLetters[message.author.id]["letter_argv"].append(message.content)

                if len(wipLetters[message.author.id]["letter_argv"]) > 9:
                    global finishedLetters
                    replySplit = None
                    attemptCount = 0

                    while replySplit is None and attemptCount < 3:
                        try:
                            replySplit = SantaReply(
                                SantaEmail(
                                    *wipLetters[message.author.id]["letter_argv"]
                                )
                            ).replyText.replace("\n", "\n> ")
                        except:
                            await message.channel.send(
                                "> There was an issue sending your letter. Trying again..."
                            )
                            attemptCount += 1
                    if replySplit is None:
                        await message.channel.send(
                            "> There was an issue sending your letter. Please report this issue to the developers of this bot (type `es!about`). Sorry!"
                        )
                        del wipLetters[message.author.id]
                        return

                    replySplit = replySplit.splitlines()

                    readyToAddFinishedLetter = (
                        wipLetters[message.author.id]["replylocation"],
                        "> **A letter from Santa for {}**".format(
                            message.author.mention
                        ),
                        replySplit,
                        "> **End of letter from Santa for {}**".format(
                            message.author.name
                        ),
                    )
                    finishedLetters[message.author.id] = readyToAddFinishedLetter
                    await message.channel.send(
                        "> Thank you. Your letter is now complete. Please wait in "
                        + wipLetters[message.author.id]["receivinglocation"]
                        + " for your letter to appear. It takes a bit for Santa to send many letters, so you might have to wait up to 5 minutes before you see your letter. Please be patient."
                    )
                    del wipLetters[message.author.id]

                elif len(wipLetters[message.author.id]["letter_argv"]) == 9:
                    await message.channel.send(
                        "> Do you have any additional comments for Santa? If you do not, type `SKIP!` (all caps with exclamation mark) to skip this step."
                    )
                elif len(wipLetters[message.author.id]["letter_argv"]) == 8:
                    await message.channel.send(
                        "> What is your third choice for Christmas gift this year?"
                    )
                elif len(wipLetters[message.author.id]["letter_argv"]) == 7:
                    await message.channel.send(
                        "> What is your second choice for Christmas gift this year?"
                    )
                elif len(wipLetters[message.author.id]["letter_argv"]) == 6:
                    await message.channel.send(
                        "> What is your top choice for Christmas gift this year?"
                    )
                elif len(wipLetters[message.author.id]["letter_argv"]) == 5:
                    await message.channel.send(
                        """> How good have you been this year? Select one of the three following choices:
    > `0` denotes "my halo has been to the repair shop a few times".  
    > `1` denotes "I should still be on the 'Nice' list!"  
    > `2` denotes "my halo is just a little bit crooked!!"  
    > `3` denotes "I should be the angel at the top of the tree!"""
                    )
                elif len(wipLetters[message.author.id]["letter_argv"]) == 4:
                    await message.channel.send("> What country do you live in?")
                elif len(wipLetters[message.author.id]["letter_argv"]) == 3:
                    await message.channel.send("> What city do you live in?")
                elif len(wipLetters[message.author.id]["letter_argv"]) == 2:
                    await message.channel.send(
                        "> How old are you? Type an integer only. (If less than one year old, type `0`.)"
                    )
                elif len(wipLetters[message.author.id]["letter_argv"]) == 1:
                    await message.channel.send(
                        "> Are you a boy or a girl? Type `1` for boy or `2` for girl."
                    )
            except:
                await message.channel.send(
                    "> You haven't started an email to Santa yet! Go to a server with this bot and type `es!emailsanta`, or type it here to see Santa's reply here."
                )


if __name__ == "__main__":
    client.run(TOKEN)