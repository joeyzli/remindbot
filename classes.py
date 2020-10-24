from time import localtime
import datetime


class Tree:
	def __init__(self, value, left=None, right=None):
		self.value = value
		self.left = left
		self.right = right

class TimeObject:
	def __init__(self, year=None, month=None, day=None, hour=None, minute=None):
		self.values = {'year': localtime().tm_year if year == None else year, 'month': localtime().tm_mon if month == None else month, 'day': localtime().tm_mday if day == None else day, 'hour': localtime().tm_hour if hour == None else hour, 'minute': localtime().tm_min if minute == None else minute}

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
		diff = datetime.datetime(self.year, self.month, self.day, self.hour, self.minute) - datetime.datetime(other.year, other.month, other.day, other.hour, other.minute)
		return int(diff.total_seconds() // 60)

	def __rsub__(self, other):
		diff = datetime.datetime(other.year, other.month, other.day, other.hour, other.minute) - datetime.datetime(self.year, self.month, self.day, self.hour, self.minute)
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
		self.notif_times = [60,30,5,1] #can be modified by the user so they are reminded more/less often.
		self.reminders = []
		self.parse_data(user_data)

	def parse_data(self, user_data):
		for k,v in user_data.items():
			time_args = [int(n) for n in v.split('-')]
			self.reminders.append(Reminder(k, TimeObject(time_args[0],time_args[1],time_args[2],time_args[3],time_args[4])))

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

	def get_dict(self):
		return {r.name: str(r.time) for r in self.reminders}

	def __str__(self):
		return str(self.id) + " -- " + str(self.get_dict())
