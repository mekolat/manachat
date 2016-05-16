import time
# import random
import net.mapserv as mapserv
import net.charserv as charserv
import chatbot
import commands
import walkto
import logicmanager
from net.inventory import get_item_index
from utils import extends
# from itemdb import item_name
from actor import find_nearest_being
import npc
import autofollow
import status


__all__ = [ 'PLUGIN', 'init' ]


PLUGIN = {
    'name': 'manaboy',
    'requires': ('chatbot', 'npc', 'autofollow'),
    'blocks': (),
}

whisper = mapserv.cmsg_chat_whisper
# spells = ['inma', 'betsanc', 'asorm', 'plugh', 'ingrav',
#           'parum', 'kalmurk', ]

npcdialog = {
    'start_time': -1,
    'program': [],
}

_times = {
    'follow': 0,
    'where' : 0,
    'status' : 0,
    'inventory' : 0,
    'say' : 0,
    'zeny' : 0,
}

admins = ['Trav', 'Travolta', 'Komornyik']


@extends('smsg_being_remove')
def being_remove(data):
    if data.id == charserv.server.account:
        mapserv.cmsg_player_respawn()


@extends('smsg_npc_message')
@extends('smsg_npc_choice')
@extends('smsg_npc_close')
@extends('smsg_npc_next')
@extends('smsg_npc_int_input')
@extends('smsg_npc_str_input')
def npc_activity(data):
    npcdialog['start_time'] = time.time()


def cmd_where(nick, message, is_whisper, match):
    if not is_whisper:
        return

    pp = mapserv.player_pos
    msg = "Map: {}, coor: {}, {}".format(pp['map'], pp['x'], pp['y'])
    whisper(nick, msg)


def cmd_goto(nick, message, is_whisper, match):
    if not is_whisper:
        return

    try:
        x = int(match.group(1))
        y = int(match.group(2))
    except ValueError:
        return

    mapserv.cmsg_player_change_dest(x, y)


def cmd_pickup(nick, message, is_whisper, match):
    if not is_whisper:
        return

    commands.pickup()


def cmd_drop(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if nick not in admins:
        return

    try:
        amount = int(match.group(1))
        item_id = int(match.group(2))
    except ValueError:
        return

    index = get_item_index(item_id)
    if index > 0:
        mapserv.cmsg_player_inventory_drop(index, amount)


def cmd_item_action(nick, message, is_whisper, match):
    if not is_whisper:
        return

    try:
        itemId = int(match.group(1))
    except ValueError:
        return

    index = get_item_index(itemId)
    if index <= 0:
        return

    if message.startswith('!equip'):
        mapserv.cmsg_player_equip(index)
    elif message.startswith('!unequip'):
        mapserv.cmsg_player_unequip(index)
    elif message.startswith('!use'):
        mapserv.cmsg_player_inventory_use(index, itemId)


def cmd_emote(nick, message, is_whisper, match):
    if not is_whisper:
        return

    try:
        emote = int(match.group(1))
    except ValueError:
        return

    mapserv.cmsg_player_emote(emote)


def cmd_attack(nick, message, is_whisper, match):
    if not is_whisper:
        return

    target_s = match.group(1)

    try:
        target = mapserv.beings_cache[int(target_s)]
    except (ValueError, KeyError):
        target = find_nearest_being(name=target_s,
                                    ignored_ids=walkto.unreachable_ids)

    if target is not None:
        walkto.walkto_and_action(target, 'attack')


def cmd_say(nick, message, is_whisper, match):
    if not is_whisper:
        return

    msg = match.group(1)
    whisper(nick, msg)


def cmd_sit(nick, message, is_whisper, match):
    if not is_whisper:
        return

    mapserv.cmsg_player_change_act(0, 2)


def cmd_follow(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if autofollow.follow == nick:
        autofollow.follow = ''
    else:
        now = time.time()
        if now > _times['follow'] + 300:
            autofollow.follow = nick
            _times['follow'] = now


def cmd_lvlup(nick, message, is_whisper, match):
    if not is_whisper:
        return

    stat = match.group(1).lower()
    stats = {'str': 13, 'agi': 14, 'vit': 15,
             'int': 16, 'dex': 17, 'luk': 18}

    skills = {'mallard': 45, 'brawling': 350, 'speed': 352,
              'astral': 354, 'raging': 355, 'resist': 353}

    if stat in stats:
        mapserv.cmsg_stat_update_request(stats[stat], 1)
    elif stat in skills:
        mapserv.cmsg_skill_levelup_request(skills[stat])


def cmd_inventory(nick, message, is_whisper, match):
    if not is_whisper:
        return

    ls = status.invlists(50)
    for l in ls:
        whisper(nick, l)


def cmd_status(nick, message, is_whisper, match):
    if not is_whisper:
        return

    all_stats = ('stats', 'hpmp', 'weight', 'points',
                 'zeny', 'attack', 'skills')

    sr = status.stats_repr(*all_stats)
    whisper(nick, ' | '.join(sr.values()))


def cmd_zeny(nick, message, is_whisper, match):
    if not is_whisper:
        return

    whisper(nick, 'I have {} GP'.format(mapserv.player_money))


def cmd_talk2npc(nick, message, is_whisper, match):
    if not is_whisper:
        return

    npc_s = match.group(1)
    jobs = []
    name = ''
    try:
        jobs = [int(npc_s)]
    except ValueError:
        name = npc_s

    b = find_nearest_being(name=name, type='npc', allowed_jobs=jobs)
    if b is None:
        return

    mapserv.cmsg_npc_talk(b.id)


def cmd_input(nick, message, is_whisper, match):
    if not is_whisper:
        return

    npc.cmd_npcinput('', match.group(1))


def cmd_close(nick, message, is_whisper, match):
    if not is_whisper:
        return

    npc.cmd_npcclose()


def cmd_help(nick, message, is_whisper, match):
    if not is_whisper:
        return

    m = 'I am ManaBoy'
    whisper(nick, m)


# =========================================================================
def manaboy_logic(ts):

    def reset():
        npcdialog['start_time'] = -1
        npc.cmd_npcclose()

    if npcdialog['start_time'] <= 0:
        return

    if ts > npcdialog['start_time'] + 10.0:
        reset()


# =========================================================================
manaboy_commands = {
    '!where' : cmd_where,
    '!goto (\d+) (\d+)' : cmd_goto,
    '!pickup' : cmd_pickup,
    '!drop (\d+) (\d+)' : cmd_drop,
    '!equip (\d+)' : cmd_item_action,
    '!unequip (\d+)' : cmd_item_action,
    '!use (\d+)' : cmd_item_action,
    '!emote (\d+)' : cmd_emote,
    '!attack (.+)' : cmd_attack,
    '!say ((@|#).+)' : cmd_say,
    '!sit' : cmd_sit,
    '!follow' : cmd_follow,
    '!lvlup (\w+)' : cmd_lvlup,
    '!inventory' : cmd_inventory,
    '!status' : cmd_status,
    '!zeny' : cmd_zeny,
    '!talk2npc (\w+)' : cmd_talk2npc,
    '!input (.+)' : cmd_input,
    '!close' : cmd_close,
    '!(help|info)' : cmd_help,
}


def init(config):
    for cmd, action in manaboy_commands.items():
        chatbot.add_command(cmd, action)

    logicmanager.logic_manager.add_logic(manaboy_logic)