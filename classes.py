'''
- implement config part, so alter the user data a bit
'''

from datetime import datetime
from pytz import timezone


class Tree:
	def __init__(self, value, left=None, right=None):
		self.value = value
		self.left = left
		self.right = right

class TimeObject:
	deftz = timezone("America/Los_Angeles")

	def __init__(self, year=None, month=None, day=None, hour=None, minute=None):
		curtime = datetime.now(self.deftz)
		self.values = {'year': curtime.year if year == None else year, 'month': curtime.month if month == None else month, 'day': curtime.day if day == None else day, 'hour': curtime.hour if hour == None else hour, 'minute': curtime.minute if minute == None else minute}

	def __getattr__(self, attribute):
		return self.values[attribute]

	def compare_to(self, other):
		for key, value in self.values.items():
			if other.__getattr__(key) > value:
				return -1
			elif other.__getattr__(key) < value:
				return 1
		return 0

	def __sub__(self, other):
		diff = datetime(self.year, self.month, self.day, self.hour, self.minute) - datetime(other.year, other.month, other.day, other.hour, other.minute)
		return int(diff.total_seconds() // 60)

	def __rsub__(self, other):
		diff = datetime(other.year, other.month, other.day, other.hour, other.minute) - datetime(self.year, self.month, self.day, self.hour, self.minute)
		return int(diff.total_seconds() // 60)

	def __eq__(self, other):
		return self.compare_to(other) == 0

	def __ne__(self, other):
		return self.compare_to(other)

	def __lt__(self, other):
		return self.compare_to(other) < 0

	def __le__(self, other):
		return self.compare_to(other) <= 0

	def __gt__(self, other):
		return self.compare_to(other) > 0

	def __ge__(self, other):
		return self.compare_to(other) >= 0

	def __str__(self):
		return f'{self.year}-{self.month}-{self.day}-{self.hour}-{self.minute}'

	def __repr__(self):
		return f'{self.month}-{self.day}-{self.year}, {self.hour}:{str(self.minute).zfill(2)}'



class Reminder:
	def __init__(self, name, time):
		self.name = name
		self.time = time

	def __str__(self):
		return f"{self.name}: {str(self.time)}"

class TimeTree(Tree):
	def __init__(self):
		Tree.__init__(self)

	def __str__(self):
		return None #represent as a dictionary/json object.

class User:
	def __init__(self, user_id, user_data={}):
		self.id = user_id
		self.time_tree = self.make_tree(user_data)
		self.config = {}
		self.reminders = []
		self.parse_data(user_data)
		self.set_default_config()

	def parse_data(self, user_data):
		if 'config' in user_data:
			for k,v in user_data['config'].items():
				self.config[k] = v
		if 'reminders' in user_data:
			for k,v in user_data['reminders'].items():
				time_args = [int(n) for n in v.split('-')]
				self.reminders.append(Reminder(k, TimeObject(time_args[0],time_args[1],time_args[2],time_args[3],time_args[4])))

	def set_default_config(self):
		if 'notif_times' not in self.config:
			self.config['notif_times'] = [60,30,5,1]
		if 'timemode_24hr' not in self.config:
			self.config['timemode_24hr'] = True
		if 'timezone' not in self.config:
			self.config['timezone'] = 'PST'

	def make_tree(self, user_data):
		return None

	def add_reminder(self, reminder):
		v = 1
		def_name = reminder.name
		while reminder.name in [r.name for r in self.reminders]:
			reminder.name = def_name + f"({v})"
			v += 1
		self.reminders.append(reminder)
		self.reminders.sort(key=lambda x: x.time)

	def remove_reminder(self, reminder):
		self.reminders.remove(reminder)

	def remove_reminder_by_name(self, reminder_name):
		for reminder in self.reminders:
			if reminder.name == reminder_name:
				self.remove_reminder(reminder)
				return True
		return False

	def add_notif_time(self, minutes):
		if minutes not in self.config['notif_times']:
			self.config['notif_times'].append(minutes)
			self.config['notif_times'].sort(key=lambda x: -x)
			return True
		return False

	def remove_notif_time(self, minutes):
		if minutes in self.config['notif_times']:
			self.config['notif_times'].remove(minutes)
			return True
		return False

	def swap_timemode(self):
		self.config['timemode_24hr'] = not self.config['timemode_24hr']

	def get_dict(self):
		return {'config': self.config, 'reminders': {r.name: str(r.time) for r in self.reminders}}

	def __str__(self):
		return str(self.id) + " -- " + str(self.get_dict())
