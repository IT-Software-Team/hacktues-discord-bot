# coding=utf-8
from distutils.log import debug
import random
from urllib import response
from aiohttp.helpers import TOKEN

import discord
from discord.ext import commands

import channels
from utils import get_team_role
from emojis import SUNGLASSES, SAD
import emojis
from utils import remessage, request, resend

import re
from datetime import date

import aiohttp
from dotenv import load_dotenv
import os


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()

    @commands.has_role('Организатор')
    @commands.command(aliases=['s', 'с'])
    async def send(self, ctx, channel: discord.TextChannel, *, message=''):
        await remessage(channel.send, message, ctx.message)

    @commands.has_role('Организатор')
    @commands.command(aliases=['m', 'съобщение', 'м'])
    async def message(self, ctx, user: discord.User, *, message=''):
        await remessage(user.send, message, ctx.message)
        await ctx.send(f"sent to {user.id}")

    @commands.check_any(commands.has_role('Организатор'),
                        commands.has_role('оценител'),
                        commands.has_role('ЕКО'))
    @commands.command(aliases=['j', 'виж', 'в', '+'])
    async def join(self, ctx, *, role: discord.Role):
        await ctx.author.add_roles(role, reason="join")

    @commands.check_any(commands.has_role('Организатор'),
                        commands.has_role('оценител'),
                        commands.has_role('ЕКО'))
    @commands.command(aliases=['l', 'напусни', 'н', '-'])
    async def leave(self, ctx, *, role: discord.Role):
        await ctx.author.remove_roles(role, reason="leave")

    async def edit_status(self, message, status, проблем, team):
        content = f"{emojis.TICKETS}проблем от {team}: {проблем} (статус: {status})"
        await message.edit(content=content)

    @commands.command(aliases=('проблем', 'п', 'p'))
    async def problem(self, ctx, *, проблем="не е посочен конкретен проблем"):
        assert 'team' in ctx.channel.name, 'problem outside team channel'
        roles = ['team' in str(role) for role in ctx.author.roles]
        assert any(roles), 'problem from non-participant'
        team_role = ctx.author.roles[roles.index(True)]

        reason = 'ticket system'
        status = f"{emojis.TICKETS} отворенo"
        content = f"{emojis.TICKETS}проблем от {team_role.name}: {проблем} (статус: {status})"
        problems = await self.bot.fetch_channel(channels.PROBLEMS)
        message = await problems.send(content)

        def check_tickets(r, u):
            return (str(r) == emojis.TICKETS and
                    u != self.bot.user and r.message.id == message.id)

        def check_yesno(mentor):
            def check(r, u):
                return (u == mentor and r.message.id == message.id and
                        (str(r) in (emojis.WHITE_CHECK_MARK,
                         emojis.NEGATIVE_SQUARED_CROSS_MARK)))
            return check

        content = (f"Вашият {emojis.TICKETS}проблем беше "
                   "изпратен до менторите успешно!")
        await ctx.channel.send(content)

        while True:
            await message.add_reaction(emojis.TICKETS)
            _, mentor = await self.bot.wait_for('reaction_add',
                                                check=check_tickets)
            if mentor.nick:
                mentor_name = mentor.nick
            else:
                mentor_name = mentor.name
            await mentor.add_roles(team_role, reason=reason)
            await message.clear_reaction(emojis.TICKETS)
            status = f"{emojis.X} в процес на разрешаване…"
            await self.edit_status(message, status, проблем, team_role.name)

            await message.add_reaction(emojis.WHITE_CHECK_MARK)
            await message.add_reaction(emojis.NEGATIVE_SQUARED_CROSS_MARK)
            content = f"<@{mentor.id}> се зае с вашия {emojis.TICKETS}проблем!"
            await ctx.channel.send(content)
            claimed = await self.bot.fetch_channel(channels.CLAIMED)
            await claimed.send(mentor_name)
            reaction, _ = await self.bot.wait_for('reaction_add',
                                                  check=check_yesno(mentor))
            await mentor.remove_roles(team_role, reason=reason)
            await message.clear_reaction(emojis.WHITE_CHECK_MARK)
            await message.clear_reaction(emojis.NEGATIVE_SQUARED_CROSS_MARK)

            if str(reaction) == emojis.WHITE_CHECK_MARK:
                status = f"{emojis.WHITE_CHECK_MARK} приключено"
                await self.edit_status(message, status, проблем, team_role.name)
                content = (f"{emojis.TICKETS}Проблемът ви "
                           "беше отбелязан като разрешен!")
                await ctx.channel.send(content)
                closed = await self.bot.fetch_channel(channels.CLOSED)
                await closed.send(mentor_name)
                break

            await self.edit_status(message, f"{emojis.TICKETS} отворенo",
                                   проблем, team_role.name)
            content = f"{emojis.TICKETS}Проблемът ви беше повторно отворен!"
            await ctx.channel.send(content)
            reopened = await self.bot.fetch_channel(channels.REOPENED)
            await reopened.send(mentor_name)

    @commands.command(aliases=['пинг'])
    async def ping(self, ctx):
        await ctx.send(f"{emojis.PONG} Понг с "
                       f"{str(round(self.bot.latency, 2))} s")

    @commands.command(aliases=['мотивирай', 'мот', 'mot'])
    async def motivate(self, ctx):
        channel = await self.bot.fetch_channel(channels.MOTIVATIONS)
        messages = [message async for message in channel.history()]
        message = random.choice(messages)
        await ctx.send(message.attachments[0].url)

    @commands.command(aliases=['email', 'имейл', 'емаил'])
    async def auth_email(self, ctx, email):
        assert 'верификация' in ctx.channel.name, 'Problem outside auth channel'
        
        if(len(ctx.message.content.split()) != 3):
            await remessage(ctx.author.send, f'Здравей, Гришо е!\n Радвам се да те видя {SUNGLASSES}. Пиша, за да ти кажа, че ползваш грешен формат.. Форматът е "ht email ivan.i.ivanov.2020@elsys-bg.org"', ctx.message)
            return

        auth_token = os.getenv('auth_token')
        headers = {"Authorization": f"Bearer {auth_token}"}
        async with aiohttp.ClientSession(headers=headers) as client:
            response = await request(self.bot, client, path='api/user/get-discord-token', email=email, feedback=True)
            if(response['success']):
                await remessage(ctx.author.send, f'Хей, Гришо е! Радвам се да те видя {SUNGLASSES}\nПиша, за да ти кажа, че ти пратих имейл с кода за верификация. Екипът на HackTUES Infinity ти пожелава приятно изкарване в сървъра', ctx.message)
            # elif (not response['success'] and ('' in response['errors'])):
            else:
                err_msg = list(response['errors'].values())[0]
                await remessage(ctx.author.send, f'Хей, Гришо е!\n{err_msg} \n{SAD}', ctx.message)

    # give_user_points
    # (user, points, reason)
    @commands.has_role('Организатор')
    @commands.command(aliases=['give', 'g'])
    async def give_points(self, ctx, user: discord.User, points, reason="No reason specified"):
        # get discord id
        user_id = str(user.id)
        print("discordId", user_id)

        # send request
        auth_token = os.getenv('auth_token')
        headers = {"Authorization": f"Bearer {auth_token}"}
        async with aiohttp.ClientSession(headers=headers) as client:
            response = await request(self.bot, client, path='api/team/add-points', discordId=user_id, points=int(points))
            if(response['success']):
                # send message of success
                await ctx.send(f"Бяха дадени {points} точки на отбор {response['response']['teamName']}. Общо {response['response']['grishoPoints']}")
            else:
                err_msg = response['response']
                await ctx.send(f'\n{err_msg} \n{SAD}')

    @commands.has_role('Организатор')
    @commands.command(aliases=["updatementors"])
    async def update_mentors(self, ctx):
        await ctx.send("Starting update_mentors...");
        reason = "updatementors"

        for member in ctx.guild.members:
            role = discord.utils.get(ctx.guild.roles, name="Ментор")
            # Get mentors
            if role in member.roles:
                if member.nick:
                    name = member.nick
                else:
                    name = member.name
                
                print("Current mentor:", name)

                if(name == "Манол Ружинов"):
                    continue

                # send request
                auth_token = os.getenv('auth_token')
                headers = {"Authorization": f"Bearer {auth_token}"}
                async with aiohttp.ClientSession(headers=headers) as client:
                    response = await request(self.bot, client, path='api/user/get-mentor-info', mentorName=name)
                    
                    # Add technologies
                    technologies = response['technologies']
                    for tech in technologies:
                        if not discord.utils.get(ctx.guild.roles, name=tech):
                            await ctx.guild.create_role(name=tech)

                        role = discord.utils.get(ctx.guild.roles, name=tech)
                        
                        if role not in member.roles:
                            try:
                                await member.add_roles(role, reason=reason)
                            except Exception as e:
                                print(e)

                    # Add team role. Note: Add 'team' in front of the team name
                    if response["teamName"]:
                        team_name = 'team ' + response["teamName"]
                        team_role = await get_team_role(team_name, ctx.guild, reason)

                        await member.add_roles(team_role, reason=reason)

                # for role in member.roles:
                #     print("ROLE     ", role)
                #     if 'team' not in role.name and role.name != 'Ментор':
                #         await role.edit(mentionable=True)
                
        await ctx.send("update_mentors done!");

    @commands.has_role('Организатор')
    @commands.command(aliases=["printmentors"])
    async def print_mentors(self, ctx):
        for member in ctx.guild.members:
            role = discord.utils.get(ctx.guild.roles, name="Ментор")
            # Get mentors
            if role in member.roles:
                if member.nick:
                    name = member.nick
                else:
                    name = member.name
                
                print(name)
        # get all teams
        
        # go though all teams

            # convert the team name

            # search for team name

            # if no result => print

    # @commands.command(aliases=["updatementorrole"])
    # async def update_channels(self, ctx):
    #     channels = ctx.guild.voice_channels
    #     count = 0
    #     for channel in channels:
    #         if channel.name.startswith('team'):
    #             print("Fetching",channel)
    #             role = discord.utils.get(ctx.guild.roles, name="Ментор Оценител")
    #             await channel.set_permissions(role, send_messages=True, view_channel=True)
    #             count += 1

    #     print(count)
    


