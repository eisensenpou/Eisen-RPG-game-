import random as r


class Player:
    def __init__(self, name, health, strength, password, mana, max_health, health_growth_per_level=10,
                 strength_growth_per_level=2, gold=0, xp=0, level=1, weapon=None, armor=None, inventory=None):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.strength = strength
        self.mana = mana
        self.xp = xp
        self.level = level
        self.password = password
        self.weapon = weapon
        self.armor = armor
        self.health_growth_per_level = health_growth_per_level
        self.strength_growth_per_level = strength_growth_per_level
        self.gold = gold
        self.inventory = {
            "weapons": {},
            "armors": {},
            "potions": {
                "health potions": 0,
                "mana potions": 0
            }
        }

    def level_up(self):
        required_xp = 100 * (2 ** self.level)
        while self.xp >= required_xp:
            self.xp -= required_xp  # we need to deduct player's xp after each level up
            self.level += 1
            self.strength += self.strength_growth_per_level
            self.health += self.health_growth_per_level
            self.max_health += self.health.growth_per_level
            print(f"{self.name} levelled up! Current level: {self.level}")

    def gain_xp(self, xp):
        self.xp += xp  # adds new xp to old xp
        print(f"{self.name} gained {xp} total xp: {self.xp}")
        self.level_up()

    def show_stats(self):
        print(f"------STATS------")
        print(f"---{self.name}---")
        print(f"Health: {self.health}")
        print(f"Strength:{self.strength}")
        print(f"XP:{self.xp}")
        print(f"Level:{self.level}")
        print(f"Weapon:{self.weapon}")
        print(f"Armor:{self.armor}")

    def gain_gold(self, generated_gold):
        if generated_gold < 0:
            print("Error: Cannot gain negative gold!")
            return
        self.gold += generated_gold
        print(f"{self.name} gained {generated_gold} gold. Total gold: {self.gold}")

    def receive_loot(self, loot):
        for item in loot:

            if isinstance(item, Weapon):  # to check the type of the loot
                if item.name in self.inventory["weapons"]:
                    self.inventory["weapons"][item.name] += 1
                else:
                    self.inventory["weapons"][item.name] = 1
                print(f"Received weapon: {item.name}")
            elif isinstance(item, Armor):
                if item.name in self.inventory["armors"]:
                    self.inventory["armors"][item.name] += 1
                else:
                    self.inventory["armors"][item.name] = 1
                print(f"Received armor: {item.name}")
            elif isinstance(item, Potion):
                if item.name in self.inventory["potions"]:
                    self.inventory["potions"][item.name] += 1
                else:
                    self.inventory["potions"][item.name] = 1
                print(f"Received potion: {item.name}")
            else:
                print(f"Unknown item type: {item.name}")


#        def view_inventory(self):
#            print("Inventory:")
#            for category, items in self.inventory.items():
#                print(f"\n{category.capitalize()}:")
#                if items:
#                    for item, count in items.items():
#                        print(f"  {item}: {count}")
#                else:
#                    print("  (empty)")

class Enemy:
    def __init__(self, name, health, strength, level, weapon=None, armor=None):
        self.name = name
        self.health = health
        self.strength = strength
        self.level = level
        self.weapon = weapon
        self.armor = armor

    def generate_xp(self):
        if self.health <= 0:
            xp = self.level * r.randint(self.level * 3, self.level * 6)
            return xp
        else:
            return 0  # enemy is not defeated

    def generate_gold_loot(self):
        min_gold = self.level * 2
        max_gold = self.level * 5
        return r.randint(min_gold, max_gold)  # generates a random gold loot based on the enemy character's level

    def loot_drop(self):
        # loot drops occur with a little chance when enemy has items
        drop_chance = 0
        drop = []
        if self.weapon and self.armor:
            drop_chance = 0.05
            drop = [self.weapon, self.armor]
        elif self.weapon or self.armor:
            drop_chance = 0.1
            drop = [self.armor, self.weapon] if self.armor else self.weapon

        if r.random() <= drop_chance:
            return [item for item in drop if item]
        else:
            return None


class Item:
    def __init__(self, name, description, effect, cost):
        self.name = name
        self.description = description
        self.effect = effect  # attack or defense attribution
        self.cost = cost


class Weapon(Item):  # subclass of item to handle weapons
    def __init__(self, name, description, effect, cost):
        super().__init__(name, description, cost)
        self.effect = effect

    def weapon_use(self, player):
        if player.weapon is None:
            player.strength += self.effect
            player.weapon = self
            print(f"{player.name} equipped {player.weapon.name}")
        else:
            action = input(
                f"{player.name} has already have a weapon. Do you want to (1) change your weapon or (2) see your weapon's damage?")
            if action == "1":
                change = input("Do you want to change your weapon? (yes/no)").lower()
                if change == "yes":
                    player.strength -= player.weapon.effect
                    player.weapon = self
                    player.strength += player.weapon.effect
                    print(f"{player.name} swapped to {player.weapon.name}.")
                else:
                    print(f"{player.name} keeps their current weapon {player.weapon.name}.")
            elif action == "2":
                print(f"{player.name}'s current weapon is {player.weapon.name} with {player.weapon.effect} damage.")
            else:
                print("Incorrect choice, please enter 1 or 2!")

    def weapon_status(self, player):
        if player.weapon == self:
            print(f"{player.name} has {self.name} equipped with {self.effect} damage.")
        else:
            print(f"{player.name} doesn't have {self.name} equipped.")


class Armor(Item):  # subclass to handle armor
    def __init__(self, name, description, effect, cost):
        super().__init__(name, description, cost)
        self.effect = effect

    def armor_use(self, player):
        if player.armor is None:
            player.armor = self
            player.health += self.effect
            print(f"{player.name} equipped {self.name} with {self.effect} protection. ")
        else:

            action = input(
                f"{player.name} has {player.armor.name} equipped. Do you want to (1) change your armor or (2) see your armor's protection?")
            if action == "1":
                player.health -= player.armor.effect
                player.armor = self
                player.health += self.effect
                print(f"{player.name} swapped to {self.name}.")

            elif action == "2":
                print(f"{player.name}'s current armor is {player.armor.name} with {player.armor.effect}.")

            else:
                print("Incorrect choice, please enter 1 or 2!")


class Potion(Item):
    def __init__(self, name, description, effect, cost, count=0):
        super().__init__(name, description, cost, )
        self.count = count
        self.effect = effect

    def potion_use(self, player, potion_type):
        if player.inventory["potions"][potion_type] > 0:
            if potion_type == "health potions":

                player.health += self.effect
                print(f"{player.name} uses {self.name}, health increased by {self.effect}.")
            elif potion_type == "mana potions":
                player.mana += self.effect
                print(f"{player.name} uses {self.name}, health increased by {self.effect}.")
                player.inventory["potions"][potion_type] -= 1
        else:
            print(f"{self.name} has no {self.name} left.")


def combat(attacker, defender):
    weapon_damage = 0

    if attacker.weapon:
        weapon_damage = attacker.weapon.effect
    damage = attacker.strength + weapon_damage
    critical_hit = r.random() < 0.02
    if critical_hit:
        damage *= 2
        print("Critical hit! Damage doubled!")
    if defender.armor:
        armor_protection = defender.armor.effect * (1 / 3)
        damage -= armor_protection
        print(f"{defender.name}'s armor absorbs {armor_protection} damage!")
    damage = max(damage, 0)
    defender.health -= damage
    print(
        f"{attacker.name} attacked {defender.name} for {damage} damage! {defender.name}'s health is {defender.health} now!")


import random  # Make sure to import random


class Combat:
    def __init__(self, attack_type, damage, weapon=None, armor=None):
        self.attack_type = attack_type
        self.damage = damage
        self.weapon = weapon
        self.armor = armor

    def perform_attack(self, attacker, defender):

        damage = self.damage
        if attacker.weapon:
            weapon_damage = attacker.weapon.effect
            damage += weapon_damage
            print(f"{attacker.name} uses {attacker.weapon.name} for {weapon_damage} extra damage!")

        critical_hit = random.random() < 0.02  #
        if critical_hit:
            damage *= 2  # Double the damage for critical hit
            print("Critical hit! Damage doubled!")

        # If the defender has armor, reduce damage
        if defender.armor:
            armor_protection = defender.armor.effect * (1 / 3)  # Reduce damage by 1/3 of armor's effect
            damage -= armor_protection
            print(f"{defender.name}'s armor absorbs {armor_protection} damage!")

        # Ensure that damage cannot be negative
        damage = max(damage, 0)

        # Apply damage to the defender's health
        defender.health -= damage
        print(
            f"{attacker.name} attacked {defender.name} for {damage} damage! {defender.name}'s health is {defender.health} now!")


class Loot:
    def __init__(self, name, loot_type, value):
        self.name = name
        self.loot_type = loot_type
        self.value = value


class Action:
    def __init__(self, name, description, method):
        self.name = name
        self.description = description
        self.method = method

    def execute(self, player):
        if self.method:
            self.method(player)
        else:
            print(f"The action '{self.name}' is not implemented yet.")
