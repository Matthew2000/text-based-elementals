import curses
from enum import Enum
from random import randint


class AutoNumber(Enum):
	def __new__(cls):
		value = len(cls.__members__) + 1
		obj = object.__new__(cls)
		obj._value_ = value
		return obj


class Races(AutoNumber):
	Human = ()     # 1
	Avaker = ()    # 2
	Elf = ()       # 3
	Dragon = ()    # 4
	Valkyrie = ()  # 5


class Character:
	def __init__(self, name: str, character: chr, race: Races):
		self.location = [1, 1]
		self.prevlocation = [1, 1]
		self.health = 100
		self.max_health = 100
		self.inventory = {"Coins": 100}
		self.name = name
		self.character = character
		self.race = race

	def move_up(self):
		if self.location[0] > 1:
			self.location[0] -= 1

	def move_down(self, area):
		if self.location[0] < area[0] - 2:
			self.location[0] += 1

	def move_left(self):
		if self.location[1] > 1:
			self.location[1] -= 1

	def move_right(self, area):
		if self.location[1] < area[1] - 2:
			self.location[1] += 1

	def attack(self, opponent):  # what you attack must inherit from Character
		opponent.health -= 10

	def death(self):  # kills the Character
		if self.health <= 0:
			self.prevlocation = self.location[:]
			self.location = [0, 0]

	def is_dead(self):  # returns True if the characters health is at or below 0
		if self.health <= 0:
			return True

	def add_coin(self, amount):
		self.inventory["Coins"] += amount

	def add_inventory_item(self, item, amount=0):
		var = False
		for x in self.inventory:
			if item.lower() == x.lower:
				var = True
		if not var:
			self.inventory[item] = amount

	def respawn(self, y, x):
		self.health = self.max_health
		self.location = [y, x]


class Player(Character):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.quests = {}
		self.quest_completed = False

	def move(self, input_key, area):
		self.prevlocation = self.location[:]
		if input_key == curses.KEY_UP:
			self.move_up()
		elif input_key == curses.KEY_DOWN:
			self.move_down(area)
		elif input_key == curses.KEY_LEFT:
			self.move_left()
		elif input_key == curses.KEY_RIGHT:
			self.move_right(area)

	def attack(self, enemy):
		if enemy.location[0] == self.location[0] + 1 or enemy.location[0] == self.location[0] - 1 or enemy.location[0] == self.location[0]:
			if enemy.location[1] == self.location[1] + 1 or enemy.location[1] == self.location[1] - 1 or enemy.location[1] == self.location[1]:
				super().attack(enemy)

	def add_quest(self, quest):
		self.quests[quest["quest name"]] = quest

	def update_quests(self, enemies, npcs, journal):
		for quest in self.quests:
			requirement = self.quests[quest]["objective"]["requirement"]
			if requirement == "kill":
				for enemy in enemies:
					if enemy.name == self.quests[quest]["objective"]["object"]:
						if enemy.is_dead():
							if not self.quests[quest]["quest completed"]:
								journal.insertln()
								journal.addstr(1, 1, "You have completed the quest go to %s to claim your reward" % self.quests[quest]["quest giver"])
							self.quests[quest]["quest completed"] = True
							self.quest_completed = True
						else:
							self.quests[quest]["quest completed"] = False
							self.quest_completed = False


class NPC(Character):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.allow_movement = True
		self.talking = False
		self.dialogue = {"intro": "Hi my name is %s." % self.name, "quest": {"quest 1": {"quest name": "name", "description": "quest description.", "objective": {"requirement": "quest requirement", "object": "object"}, "reward": {"object": "reward object", "amount": "reward amount"}, "quest completed": False, "quest giver": self.name}}, "trade": "I have nothing to trade.", "talk": "I am an NPC."}
		self.has_quest = False

	def move(self, area):
		if self.allow_movement:
			self.prevlocation = self.location[:]
			direction = randint(0, 4)
			if direction is 0:
				pass
			elif direction is 1:
				self.move_up()
			elif direction is 2:
				self.move_down(area)
			elif direction is 3:
				self.move_right(area)
			else:
				self.move_left()

	def conversation_start(self, conversation):
		conversation.clear()
		conversation.border()
		conversation.addstr(0, 1, "Conversation")
		conversation.addstr(2, 1, "1 - Talk")
		conversation.addstr(3, 1, "2 - Quest")
		conversation.addstr(4, 1, "3 - Trade")
		conversation.addstr(5, 1, "4 - Leave")
		conversation.refresh()

	def show_options(self, conversation, *options):
		x = 2
		conversation.clear()
		conversation.border()
		conversation.addstr(0, 1, "Conversation")
		for option in options:
			conversation.addstr(x, 1, option)
			x += 1
		conversation.refresh()

	def interact(self, journal, conversation, input_key, player, log):
		if self.talking is False:
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["intro"])
			self.conversation_start(conversation)
		self.talking = True
		if input_key is ord("1"):
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["talk"])
			self.conversation_start(conversation)
		elif input_key is ord("2"):
			if self.has_quest is True:
				while 1:
					if player.quest_completed:
						for quest in self.dialogue["quest"]:
							if player.quests[self.dialogue["quest"][quest]["quest name"]]["quest completed"]:
								journal.insertln()
								journal.addstr(1, 1, "You have completed my quest, here is your reward.")
								journal.border()
								journal.refresh()
								self.show_options(conversation, "1 - Accept")
								input_key = conversation.getch()
								if input_key is ord("1"):
									player.inventory[self.dialogue["quest"][quest]["reward"]["object"]] += self.dialogue["quest"][quest]["reward"]["amount"]
									player.quest_completed = False
									del player.quests[self.dialogue["quest"][quest]["quest name"]]
									self.conversation_start(conversation)
									break
						break
					else:
						journal.insertln()
						journal.addstr(1, 1, self.dialogue["quest"]["quest 1"]["description"])
						journal.border()
						journal.refresh()
						self.show_options(conversation, "1 - Yes", "2 - No")
						journal.border()
						input_key = conversation.getch()
						if input_key is ord("1"):
							journal.insertln()
							journal.addstr(1, 1, "Quest accepted")
							journal.refresh()
							player.add_quest(self.dialogue["quest"]["quest 1"])
							self.conversation_start(conversation)
							break
						if input_key is ord("2"):
							self.conversation_start(conversation)
							break
			else:
				journal.insertln()
				journal.addstr(1, 1, "I have no quest for you at the moment")
				journal.refresh()
		elif input_key is ord("3"):
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["trade"])
			self.conversation_start(conversation)


class Enemy(NPC):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.dialogue = {"intro": "I'm going to kill you"}

	def attack(self, player):
		if player.location[0] == self.location[0] + 1 or player.location[0] == self.location[0] - 1 or player.location[0] == self.location[0]:
			if player.location[1] == self.location[1] + 1 or player.location[1] == self.location[1] - 1 or player.location[1] == self.location[1]:
				super().attack(player)
