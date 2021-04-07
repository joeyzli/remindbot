'''
TODO:
- Setup discord.py
- Write TimeTree class that sorts on time
- Write a Timenode class to be used as each tree's value
- Write a User class to allow easy manipulation of data. Identified by ID
- Write a main function that updates all users every minute
- Write a Reminder class to store reminders
- Consider looking into databases. For now, use user ids as names for json files to read off of
- Consider other functionalities like timezone converter, automatic timezone selection, etc.
- Consider implementing periodic reminders
'''
import discord
import json
import os
import asyncio
from classes import *

class MyClient(discord.Client):
	
	data_path = "Users/" #path file for getting user data
	prefix = '--'
	command_formats = {'add': "--add [reminder name] || [month]-[day]-[year]-[hour]-[minute]", 'remove': "--remove [reminder name]", 'add_nt': '--addnt [time(in minutes)]', 'remove_nt': '--removent [time(in minutes)]', 'view_nt': '--viewnt'}

	def __init__(self):
		self.parse_user_data() #store user objecs that are accessed to allow quick reaccessing, parse the data file here.
		discord.Client.__init__(self)

	def parse_user_data(self):
		if self.data_path.strip('/') not in os.listdir():
			os.mkdir(self.data_path.strip("/"))
		os.chdir(self.data_path)
		self.bot_users = {}
		for file in os.listdir():
			user_id = int(file[:-5]) #len of the file extension, .json
			with open(file, 'r') as f:
				self.bot_users[user_id] = User(user_id, json.loads(f.read()))
		print('Parsed user data.')

	async def on_ready(self):
		print("Successfully booted.")
		await asyncio.sleep(3)
		print("Updating...")
		while True:
			await self.update()
			await asyncio.sleep(60)

	async def on_message(self, message):
		if message.author == self.user:
			return

		if message.content.startswith(self.prefix):
			message.content = message.content[2:]
			command = message.content.split(' ')[0]
			#Command selection
			if command == 'add':
				try:
					await self.add_reminder(message.author.id, message.content[3:])
					await message.channel.send('Added reminder successfully.')
				except:
					await message.channel.send(f"{message.author.mention},\n```Failed to add your assignment. Use the following format:\n{self.command_formats['add']}\nAlternatively, you can replace each time with d to default it to the current time.```")

			elif command == 'show':
				if message.author.id not in self.bot_users:
					await message.channel.send('```You do not have any active reminders.```')
					return
				user = self.bot_users[message.author.id]
				msg = ''
				for reminder in user.reminders:
					msg += f"- {reminder.name}, due at {reminder.time.hour}:{str(reminder.time.minute).zfill(2)} on {reminder.time.month}/{reminder.time.day}/{reminder.time.year}\n"
				if msg:
					msg = "```Your currently active reminders are:\n" + msg + "```"
				else:
					msg = "```You have no active reminders.```"
				await message.channel.send(msg)

			elif command == 'remove':
				passed, reminder_name = await self.remove_reminder(message.author.id, message.content[6:])
				if passed:
					await message.channel.send(f"```Removed reminder '{reminder_name}' successfully.```")
				else:
					await message.channel.send(f"{message.author.mention},\n```'{reminder_name}' was not found in your reminders. Failed to remove it.```")

			elif command == 'addperiodic':
				pass

			elif command == 'addnt':
				pass

			elif command == 'removent':
				pass

			elif command == 'viewnt':
				pass

			elif command == 'help':
				await message.channel.send("```remind is a bot for helping you keep track of due dates. Commands available for use are:\n --help: For viewing this.\n --add [reminder name] || [month]-[day]-[year]-[hour]-[minute]: set a reminder.\n --show: show your active reminders.```")



	async def get_user_data(self, user_id):
		pass #retrieve the user's data and do something with it

	async def update(self):
		current_time = TimeObject()
		print(f"Updating at {current_time}.")
		for user_id, user in self.bot_users.items():
			disc_user = await self.fetch_user(f"{user_id}")
			msg1 = ''
			expired = []
			for reminder in user.reminders[:]:
				if current_time - reminder.time >= 0:
					expired.append(reminder)
					user.remove_reminder(reminder)
					self.update_user_file(user_id)
					msg1 += f"- {reminder.name}, due at {reminder.time.hour}:{str(reminder.time.minute).zfill(2)} on {reminder.time.month}/{reminder.time.day}/{reminder.time.year}\n"
			if msg1:
				msg1 = '```The following reminders are expired/occurring now:\n' + msg1 + '```'
				await disc_user.send(msg1)

			to_check = user.reminders[:]
			for time in user.config['notif_times']:
				msg2 = ''
				for reminder in to_check[:]:
					if reminder.time - current_time == time:
						msg2 += f"- {reminder.name}, due at {reminder.time.hour}:{str(reminder.time.minute).zfill(2)} on {reminder.time.month}/{reminder.time.day}/{reminder.time.year}\n"
						to_check.remove(reminder)
				if msg2:
					msg2 = f'```The following reminders are due in {time} minutes:\n' + msg2 + '```'
					await disc_user.send(msg2)
		print('Updated.')
		

	async def add_user(self, user_id):
		self.bot_users[user_id] = User(user_id)
		with open(f"{user_id}.json", 'w') as f:
			f.write(json.dumps({}))

	async def add_reminder(self, user_id, msg_content):
		if user_id not in self.bot_users:
			await self.add_user(user_id)
		reminder_name, args = msg_content.split("||")[:2]
		reminder_name, args = reminder_name.strip(), args.strip()
		current_time = datetime.now(TimeObject.deftz)
		defaults = [current_time.month, current_time.day, current_time.year, current_time.hour, current_time.minute]
		args = args.split('-')
		args = [(defaults[i] if args[i] == 'd' else int(args[i])) for i in range(len(args))]
		reminder = Reminder(reminder_name,TimeObject(args[2], args[0], args[1], args[3], args[4]))
		self.bot_users[user_id].add_reminder(reminder)
		self.update_user_file(user_id)

	async def remove_reminder(self, user_id, msg_content):
		reminder_name = msg_content.strip()
		passed = self.bot_users[user_id].remove_reminder_by_name(reminder_name)
		self.update_user_file(user_id)
		return passed, reminder_name
		
	def update_user_file(self, user_id):
		with open(f"{user_id}.json", 'w') as f:
			f.write(json.dumps(self.bot_users[user_id].get_dict()))





token = open('token.txt', 'r').read()
bot = MyClient()
bot.run(token)