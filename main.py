import json
import random as r

from classes import Player, Enemy, Item, Action, Armor, Potion, Weapon

player_database = {}

item_database = {
    "weapons": [
        Item("wooden sword", "a simple wooden sword", 10, 30),
        Item("giant wooden club", "a giant club used by ogres", 15, 75),
        Item("Iron axe", "an iron axe made for lumbering", 25, 100),
    ],
    "armors": [
        Item("wooden armor", "a simple wooden armor", 5, 35),
        Item("Leather Armor", "a light leather armor", 10, 80),
    ],
    "potions": [
        Item("health potion (small)", "a magical healing solution", 50, 10),
    ]
}
weapon_dict = {weapon.name: weapon for weapon in item_database["weapons"]}
armor_dict = {armor.name: armor for armor in item_database["armors"]}
potion_dict = {potion.name: potion for potion in item_database["potions"]}

enemy_database = {
    1: [Enemy("Goblin", 20, 1, 1), Enemy("Rat", 15, 1, 1)],
    2: [Enemy("Wild dog", 35, 4, 2), Enemy("Hobgoblin", 40, 5, 2)],
    3: [Enemy("Thief", 100, 14, 3, item_database["weapons"][0], item_database["armors"][0]),
        Enemy("Ogre", 150, 20, 3, weapon_dict["giant wooden club"])],
    4: [Enemy("Raider", 125, 25, 4, weapon_dict["Iron axe"], armor_dict["Leather Armor"])]
}

actions = {
    "1": Action("hunt", "go hunting for xp and loot", lambda player: hunt(player)),
    "2": Action("trade", "trade with the merchant", lambda player: market(player)),
    "3": Action("inventory", "View your items", lambda player: view_inventory(player)),
}


def log_in():
    attempts = 3
    print("======LOG IN======")
    name = input("Please enter your name: ")
    while attempts > 0:
        if name in player_database:
            password = input("Please enter your password: ")
            if player_database[name].password == password:
                print("Welcome!")
                return player_database[name]
            else:
                print("Incorrect password!")
                attempts -= 1
        else:
            print("No character found with this name!")
            new_character = input("Would you like to create a new character? (yes/no): ")
            if new_character.lower() == "yes":
                create_char()
                return log_in()
            else:
                print("Exiting login process.")
                exit()
    print("Too many failed attempts!")
    return None


def save_player_database():
    with open("player_database.json", "w") as file:
        json.dump({name: vars(player) for name, player in player_database.items()}, file)


def load_player_database():
    global player_database
    try:
        with open("player_database.json", "r") as file:
            data = json.load(file)
            player_database = {name: Player(**details) for name, details in data.items()}
    except FileNotFoundError:
        player_database = {}


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


def action_choice(player):
    while True:
        print("Available actions:")
        for key, action in actions.items():
            print(f"{key}: {action.name} - {action.description}")

        user_input = input("What do you want to do? (1: Hunt, 2: Trade, 3: Inventory, 0: Exit): ").strip()

        if user_input in actions:
            action = actions[user_input]

            if action.method is not None:
                action.method(player)  # Execute the associated method
                save_player_database()
            else:
                print(f"{action.name} is not implemented yet!")
        else:
            print("Invalid choice! Try again.")


def generate_enemy(player):
    enemies = enemy_database[player.level]
    enemy = r.choice(enemies)
    return enemy


def hunt(player):
    enemy = generate_enemy(player)
    while player.health > 0 and enemy.health > 0:
        combat(player, enemy)
        if enemy.health <= 0:
            print(f"{enemy.name} died. {player.name} won!")
            gained_xp = enemy.generate_xp()
            player.gain_xp(gained_xp)
            player.gain_gold(enemy.generate_gold_loot())
            break
        combat(enemy, player)
        if player.health <= 0:
            print(f"{player.name} is slew by {enemy.name}")
            break
    player.show_stats()


def view_inventory(player):
    print("Inventory:")
    for category, items in player.inventory.items():
        print(f"\n{category.capitalize()}:")
        if items:
            for item, count in items.items():
                print(f"  {item}: {count}")
        else:
            print("  (empty)")


def market(player):  # Trade
    print("Welcome to the market!")

    while True:
        choice = input(
            "What would you like to do?: \nBuy: \n(1) Weapons \n(2) Armors \n(3) Potions \n\n(4) Sell your items\n(0) to exit: ")
        if choice == "1":
            index = 1  
            print("Weapons:")
            for weapon in item_database["weapons"]:
                print(
                    f"({index}) {weapon.name} : {weapon.description} \nPrice: {weapon.cost}G\nDamage: {weapon.effect}")
                index += 1
            selected_weapon = input("Choose the weapon number to buy or '0' to go back: ")
            if selected_weapon != "0":
                selected_weapon = int(selected_weapon) - 1
                weapon = item_database["weapons"][selected_weapon]
                if weapon in player.inventory["weapons"]:
                    print("You already have this!")
                    pass
                if player.gold >= weapon.cost:
                    player.gold -= weapon.cost
                    player.inventory["weapons"][weapon.name] = weapon
                    print(f"You bought {weapon.name}.")
                    equip = input("Do you want to equip it? (yes/no): ").lower()
                    if equip == "yes":
                        if isinstance(weapon, Weapon):
                            weapon.weapon_use(player)
                        else:
                            print(f"{weapon.name} is not an armor!")
                        weapon.weapon_use(player)
                        print(f"You equipped {weapon.name}.")
                    else:
                        print(f"You didn't equip {weapon.name}.")
                else:
                    print("You don't have enough gold!")
            else:
                print("Going back...")

        elif choice == "2":
            index = 1  
            print("Armors:")
            for armor in item_database["armors"]:
                print(
                    f"({index}) {armor.name} : {armor.description} \nPrice: {armor.cost}G\nProtection: {armor.effect}")
                index += 1
            selected_armor = input("Choose the armor number to buy or '0' to go back: ")
            if selected_armor != "0":
                selected_armor = int(selected_armor) - 1
                armor = item_database["armors"][selected_armor]
                if player.gold >= armor.cost:
                    player.gold -= armor.cost
                    player.inventory["armors"][armor.name] = armor
                    print(f"You bought {armor.name}.")
                    equip = input("Do you want to equip it? (yes/no): ").lower()
                    if equip == "yes":
                        if isinstance(armor, Armor):
                            armor.armor_use(player)
                        else:
                            print(f"{armor.name} is not an armor!")
                        print(f"You equipped {armor.name}.")
                    else:
                        print(f"You didn't equip {armor.name}.")
                else:
                    print("You don't have enough gold!")
            else:
                print("Going back...")

        elif choice == "3":
            index = 1  
            print("Potions:")
            for potion in item_database["potions"]:
                print(
                    f"({index}) {potion.name} : {potion.description} \nPrice: {potion.cost}G\nEffect: {potion.effect}")
                index += 1
            selected_potion = input("Choose the potion number to buy or '0' to go back: ")
            if selected_potion != "0":
                selected_potion = int(selected_potion) - 1
                potion = item_database["potions"][selected_potion]
                if player.gold >= potion.cost:
                    if potion.name in player.inventory["potions"]:
                        player.inventory["potions"][potion.name] += 1
                    else:
                        player.inventory["potions"][potion.name] = 1
                    player.gold -= potion.cost
                    print(
                        f"You bought {potion.name}. You now have {player.inventory['potions'][potion.name]} of this potion.")
                else:
                    print("You don't have enough gold!")
            else:
                print("Going back...")

        elif choice == "0":
            print("Exiting...")
            break

        else:
            print("Invalid choice! Please enter a valid option.")


def create_char():
    name = input("Name: ")
    if name in player_database:
        print("This name is in use!")
        return
    health = 30  # Default health value
    max_health = 30  # Default max health
    strength = 2  # Default strength value
    mana = 0  # Default mana value
    while True:
        password = input("Password: ")
        ver_password = input("Type the password again: ")
        if password != ver_password:
            print("Passwords don't match")
        else:
            break
    player = Player(name, health, strength, password, mana, max_health) 
    player_database[name] = player
    save_player_database()
    print(f"Success! The character {name} has been created!")


def main():
    load_player_database()
    player = log_in()
    if player:
        print("Welcome to the game!")
        while True:
            action_choice(player)
    save_player_database()


if __name__ == "__main__":
    main()
