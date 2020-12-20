# coding=windows-1251
from os import environ

import aiohttp
import discord
from discord.ext import commands
from discord import utils

import emojis

if environ.get('ENV') == 'DEV':
    host = 'http://localhost:8000'
else:
    host = 'https://hacktues.pythonanywhere.com'

TOKEN = environ.get('token')

auth = aiohttp.BasicAuth('hacktues', 'Go Green')

bot = commands.Bot(command_prefix=('�� ', 'ht '))


async def fetch(client, path='', url=None):
    if url is None:
        url = f'{host}/{path}'

    async with client.get(url) as response:
        assert response.status == 200
        return await response.json()


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')


@bot.command(aliases=['�', 'h'])
async def ����(ctx):
    await ctx.send_help()


async def edit_status(message, status, �������):
    content = f"{emojis.TICKETS}: {�������} (������: {status})"
    await message.edit(content=content)


@bot.command(aliases=('�������', '�', 'p'))
async def problem(ctx, *, �������="�� � ������� ��������� �������"):
    assert 'team' in ctx.channel.name, 'problem outside team channel'
    roles = ['team' in str(role) for role in ctx.author.roles]
    assert any(roles), 'problem from non-participant'
    team_role = ctx.author.roles[roles.index(True)]

    reason = 'ticket system'
    status = f"{emojis.TICKETS} �������o"
    content = f"{emojis.TICKETS}: {�������} (������: {status})"
    message = await bot.get_channel(789806249704685578).send(content)

    def check_tickets(r, u):
        return (str(r) == emojis.TICKETS and
                u != bot.user and r.message.id == message.id)

    def check_yesno(mentor):
        def check(r, u):
            return (u == mentor and r.message.id == message.id and
                    (str(r) in emojis.WHITE_CHECK_MARK,
                     emojis.NEGATIVE_SQUARED_CROSS_MARK))
        return check

    while True:
        await message.add_reaction(emojis.TICKETS)
        _, mentor = await bot.wait_for('reaction_add', check=check_tickets)
        await mentor.add_roles(team_role, reason=reason)
        await message.clear_reaction(emojis.TICKETS)
        status = f"{emojis.X} � ������ �� �����������"
        await edit_status(message, status, �������)

        await message.add_reaction(emojis.WHITE_CHECK_MARK)
        await message.add_reaction(emojis.NEGATIVE_SQUARED_CROSS_MARK)
        reaction, _ = await bot.wait_for('reaction_add',
                                         check=check_yesno(mentor))
        await mentor.remove_roles(team_role, reason=reason)
        await message.clear_reaction(emojis.WHITE_CHECK_MARK)
        await message.clear_reaction(emojis.NEGATIVE_SQUARED_CROSS_MARK)

        if str(reaction) == emojis.WHITE_CHECK_MARK:
            status = f"{emojis.WHITE_CHECK_MARK} ����������"
            await edit_status(message, status, �������)
            break

        await edit_status(message, f"{emojis.TICKETS} �������o", �������)


@bot.command(aliases=['����'])
async def ping(ctx):
    await ctx.send(f"\U0001F3D3 ���� � {str(round(bot.latency, 2))} s")

'''
@bot.event
async def on_member_join(member):
    print(f'member {member.name} joined')
    print('searching for user...')
    async with aiohttp.ClientSession(auth=auth) as client:
        members_json = await fetch(client, path='users/')

        member_found = False
        username = f'{member.name}#{member.discriminator}'
        for member_json in members_json:
            if member_json['username'] == username:
                print('user was found')
                member_found = True
                break

        if not member_found:
            print('no user was found')
            return


        if team_set := member_json['team_set']:
            print('searching for team...')
            team_json = await fetch(client, url=team_set[-1])

            team_name = 'team ' + team_json['name']
            guild = member.guild
            reason = 'member join'

            role = utils.get(guild.roles, name=team_name)
            if role is None:
                print('creating role and channels...')
                role = await guild.create_role(reason=reason, name=team_name)

                perms = {
                    guild.default_role:
                        discord.PermissionOverwrite(view_channel=False),
                    role: discord.PermissionOverwrite(view_channel=True)
                }

                category = await guild.create_category(
                    team_name, overwrites=perms, reason=reason
                )
                await guild.create_text_channel(team_name, category=category)
                await guild.create_voice_channel(team_name, category=category)
            print('assigning role to member...')
            await member.add_roles(role, reason=reason)
        else:
            print('member has no team')
'''


bot.run(TOKEN)
