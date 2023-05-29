import json
import area
import battle
import constants
import enemy
import equipment
import item
import job
import messager
import peewee_models
import player
import shop
import skill
import inventory
import peewee

escordia_db = peewee.SqliteDatabase('escordia_db')
escordia_db.connect()

"""
//////////////////
/// CACHE DATA ///
//////////////////
"""

ITEM_CACHE = {}
EQUIPMENT_CACHE = {}
AREAS_CACHE = {}
DUNGEON_CACHE = {}
JOB_CACHE = {}
PLAYER_CACHE = {}
ENEMIES_CACHE = {}
BATTLE_CACHE = {}
SHOP_CACHE = {}
SKILLS_CACHE = {}

"""
///////////////
/// CREATES ///
///////////////
"""


def create_new_player(player_name: str) -> None:
    """
    Records and creates a new player in the system.

    :param player_name: Player's name.
    :return: None.
    """
    player_inst = player.Player(player_name, inventory=inventory.Inventory(player_name),
                                             equipment=constants.INITIAL_EQUIPMENT,
                                             current_job_dict=constants.INITIAL_JOB_DICT)
    PLAYER_CACHE.update({player_name: player_inst})
    peewee_models.PlayerModel.create(name=player_name, stats=json.dumps(player_inst.stats), lvl=player_inst.lvl, xp=player_inst.xp,
                              xp_to_next_lvl=player_inst.xp_to_next_lvl, xp_rate=player_inst.xp_rate, money=player_inst.money,
                              inventory=str(player_inst.inventory.items), equipment=str(player_inst.equipment), skills=str(player_inst.skills),
                              passives=str(player_inst.passives), current_area=player_inst.current_area, in_fight=player_inst.in_fight,
                              in_dungeon=player_inst.in_dungeon, defeated_bosses=str(player_inst.defeated_bosses), job_dict_list=str(player_inst.job_dict_list),
                              current_job_dict=str(player_inst.current_job_dict), current_job=player_inst.current_job)
    messager.messager_add_player(player_name)


def create_new_battle(player_inst: 'Player', enemy_inst: 'Enemy') -> None:
    """
    Creates a new battle in the system.

    :param player_inst: Player instance.
    :param enemy_inst: Enemy instance.
    :return: None.
    """
    BATTLE_CACHE.update({player_inst.name: battle.Battle(player_inst, enemy_inst)})
    print(f"Created battle with player: {player_inst.name} and enemy: {enemy_inst.name}")


def create_escordia_tables() -> None:
    """
    Creates the tables in the database.

    :return: None.
    """
    try:
        escordia_db.create_tables([peewee_models.PlayerModel])
        print("Escordia tables created.")
    except peewee.OperationalError:
        print("Escordia tables already created.")


"""
////////////////
/// UPDATES ///
////////////////
"""


def update_player_info(player_name: str) -> None:
    """
    Updates the player's info in the database.

    :param player_name: Player's name.
    :return: None.
    """
    player_inst = PLAYER_CACHE[player_name]
    peewee_models.PlayerModel.update(stats=json.dumps(player_inst.stats), lvl=player_inst.lvl, xp=player_inst.xp,
                              xp_to_next_lvl=player_inst.xp_to_next_lvl, xp_rate=player_inst.xp_rate, money=player_inst.money,
                              inventory=str(player_inst.inventory.items), equipment=str(player_inst.equipment), skills=str(player_inst.skills),
                              passives=str(player_inst.passives), current_area=player_inst.current_area, in_fight=player_inst.in_fight,
                              in_dungeon=player_inst.in_dungeon, defeated_bosses=str(player_inst.defeated_bosses), job_dict_list=str(player_inst.job_dict_list),
                              current_job_dict=str(player_inst.current_job_dict), current_job=player_inst.current_job).where(
        peewee_models.PlayerModel.name == player_name).execute()
    print(f"Updated player: {player_name} info in database.")


"""
////////////////
/// SEARCHES ///
////////////////
"""


def search_cache_player(player_name: str) -> 'Player':
    """
    Searches a player by name in the player cache.

    :param player_name: Player's name.
    :return: Player if found. Else None.
    """
    try:
        return PLAYER_CACHE[player_name]
    except KeyError:
        return None


def search_cache_battle_by_player(player_name: str) -> 'Battle':
    """
    Searches a battle by the name of the player currently fighting on it.

    :param player_name: Player's name.
    :return: Battle if found. Else None.
    """
    try:
        return BATTLE_CACHE[player_name]
    except KeyError:
        return None


def search_cache_enemy_by_name(enemy_name: str) -> 'Enemy':
    """
    Searches for an enemy in the enemy cache.

    :param enemy_name: Enemy's name.
    :return: Enemy instance. None if not found.
    """
    try:
        return ENEMIES_CACHE[enemy_name]
    except KeyError:
        return None


def search_cache_item_by_name(item_name: str) -> 'Item':
    """
    Searches for an item in the item and equipment cache.

    :param item_name: Item's name.
    :return: Item instance. None if not found.
    """
    try:
        return ITEM_CACHE[item_name]
    except KeyError:
        try:
            return EQUIPMENT_CACHE[item_name]
        except KeyError:
            return None


def search_cache_shop_by_area(area_index: int) -> 'Shop':
    """
    Searches for a shop in the shop cache.

    :param area_index: Area's index.
    :return: Shop instance. None if not found.
    """
    try:
        return SHOP_CACHE[area_index]
    except KeyError:
        return None


def search_cache_skill_by_name(skill_name: str) -> 'Skill':
    """
    Searches for a skill in the skill cache.

    :param skill_name: Skill's name.
    :return: Skill instance. None if not found.
    """
    try:
        return SKILLS_CACHE[skill_name]
    except KeyError:
        return None


def search_cache_job_by_name(job_name: str) -> 'Job':
    """
    Searches for a job in the job cache.

    :param job_name: Job's name.
    :return: Job instance. None if not found.
    """
    try:
        return JOB_CACHE[job_name]
    except KeyError:
        return None


"""
///////////////
/// DELETES ///
///////////////
"""


def delete_cache_battle_by_player(player_name: str) -> None:
    """
    Deletes a battle searching by the player's name.

    :param player_name: Player's name.
    :return: None.
    """
    b = search_cache_battle_by_player(player_name)
    if b is not None:
        BATTLE_CACHE.pop(player_name)


"""
/////////////
/// LOADS ///
/////////////
"""


def load_items_from_json() -> None:
    """
    Loads items from JSON file.

    :return: None.
    """
    with open("data/items.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)

        for i in json_file:
            param_list = [i[key] for key in constants.ITEM_KEYS]
            ITEM_CACHE.update({i["NAME"]: item.Item(*param_list)})


def load_equipment_from_json() -> None:
    """
    Loads equipment from JSON file.

    :return: None.
    """
    with open("data/equipment.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)

        for e in json_file:
            param_list = [e[key] for key in constants.EQUIPMENT_KEYS]
            EQUIPMENT_CACHE.update({e["NAME"]: equipment.Equipment(*param_list)})


def load_enemies_from_json() -> None:
    """
    Loads enemies from JSON file.

    :return: None.
    """
    with open("data/enemies.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)

        for e in json_file:
            param_list = [e[key] for key in constants.ENEMY_KEYS]
            print(*param_list)
            ENEMIES_CACHE.update({e["NAME"]: enemy.Enemy(*param_list)})


def load_areas_from_json() -> None:
    """
    Loads areas from JSON file.

    :return: None.
    """
    with open("data/areas.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)

        for a in json_file:
            param_list = [a[key] for key in constants.AREAS_KEYS]
            AREAS_CACHE.update({a["NUMBER"]: area.Area(*param_list)})


def load_dungeons_from_json() -> None:
    """
    Loads dungeons from JSON file.

    :return: None.
    """
    pass


def load_jobs_from_json() -> None:
    """
    Loads jobs from JSON file.

    :return: None.
    """
    with open("data/jobs.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)

        for j in json_file:
            param_list = [j[key] for key in constants.JOB_KEYS]
            JOB_CACHE.update({j["NAME"]: job.Job(*param_list)})


def load_shops_from_json() -> None:
    """
    Loads shops from JSON file.

    :return: None.
    """
    with open("data/shops.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)

        for s in json_file:
            param_list = [s[key] for key in constants.SHOP_KEYS]
            SHOP_CACHE.update({s["AREA_NUMBER"]: shop.Shop(*param_list)})


def load_skills_from_json() -> None:
    """
    Loads skills from JSON file.

    :return: None.
    """
    with open("data/skills.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)

        for s in json_file:
            param_list = [s[key] for key in constants.SKILL_KEYS]
            SKILLS_CACHE.update({s["NAME"]: skill.Skill(*param_list)})


def load_players_from_db() -> None:
    """
    Loads players from database.

    :return: None.
    """
    for player_model in peewee_models.PlayerModel.select():
        print(f"Loading player {player_model.name} into cache...")
        player_inst = player.Player(player_model.name, lvl=player_model.lvl, xp=player_model.xp,
                                    xp_to_next_lvl=player_model.xp_to_next_lvl,
                                    xp_rate=player_model.xp_rate, money=player_model.money,
                                    inventory=inventory.Inventory(player_model.name,
                                                                  items=eval(player_model.inventory)),
                                    equipment=eval(player_model.equipment), skills=eval(player_model.skills),
                                    passives=eval(player_model.passives), current_area=player_model.current_area,
                                    in_fight=player_model.in_fight,
                                    in_dungeon=player_model.in_dungeon,
                                    defeated_bosses=eval(player_model.defeated_bosses),
                                    job_dict_list=eval(player_model.job_dict_list),
                                    current_job_dict=eval(player_model.current_job_dict),
                                    current_job=player_model.current_job)
        messager.messager_add_player(player_inst.name)
        PLAYER_CACHE.update({player_model.name: player_inst})


def load_everything():
    create_escordia_tables()
    print("Loading data...")
    load_items_from_json()
    load_equipment_from_json()
    load_enemies_from_json()
    load_areas_from_json()
    load_dungeons_from_json()
    load_jobs_from_json()
    load_shops_from_json()
    load_skills_from_json()
    load_players_from_db()
