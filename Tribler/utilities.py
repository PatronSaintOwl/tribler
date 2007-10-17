# Written by Jie Yang
# see LICENSE.txt for license information

from socket import inet_aton, gethostbyname, getaddrinfo
from time import time, strftime, gmtime
from base64 import encodestring
from sha import sha
from copy import deepcopy
import sys
import os
import copy
from types import UnicodeType, StringType, LongType, IntType, ListType, DictType
import urlparse

STRICT_CHECK = False

permid_len = 112
infohash_len = 20

def validName(name):
    if not isinstance(name, str) and len(name) == 0:
        raise RuntimeError, "invalid name: " + name
    return True

def validPort(port):
    port = int(port)
    if port < 0 or port > 65535:
        raise RuntimeError, "invalid Port: " + str(port)
    return True

def validIP(ip):
    try:
        getaddrinfo(ip, None)
    except:
        if ip.find(':') >= 0:    # ipv6
            return True
        raise RuntimeError, "invalid IP address: " + ip
    return True
    
def validPermid(permid):
    if not isinstance(permid, str):
        raise RuntimeError, "invalid permid: " + permid
    if STRICT_CHECK and len(permid) != permid_len:
        raise RuntimeError, "invalid permid: " + permid
    return True

def validInfohash(infohash):
    if not isinstance(infohash, str):
        raise RuntimeError, "invalid infohash " + infohash
    if STRICT_CHECK and len(infohash) != infohash_len:
        raise RuntimeError, "invalid infohash " + infohash
    return True
    
def isValidPermid(permid):
    try:
        return validPermid(permid)
    except:
        return False
    
def isValidInfohash(infohash):
    try:
        return validInfohash(infohash)
    except:
        return False

def isValidPort(port):
    try:
        return validPort(port)
    except:
        return False
    
def isValidIP(ip):
    try:
        return validIP(ip)
    except:
        return False

def isValidName(name):
    try:
        return validPort(name)
    except:
        return False
    
    
def validTorrentFile(metainfo):
    if type(metainfo) != DictType:
        raise ValueError('metainfo not dict')
    
    keys = ['announce', 'info']
    for key in keys:
        if key not in metainfo:
            raise ValueError('metainfo misses key '+key)
    if not isValidURL(metainfo['announce']):
        raise ValueError('announce URL bad')
    
    info = metainfo['info']
    if type(info) != DictType:
        raise ValueError('info not dict')
    
    if 'root hash' in info:
        infokeys = ['name','piece length', 'root hash']
    else:
        infokeys = ['name','piece length', 'pieces']
    for key in infokeys:
        if key not in info:
            raise ValueError('info misses key '+key)
    name = info['name']
    if type(name) != StringType:
        raise ValueError('info name is not string')
    pl = info['piece length']
    if type(pl) != IntType:
        raise ValueError('info piece size is not int')
    if 'root hash' in info:
        rh = info['root hash']
        if type(rh) != StringType or len(rh) != 20:
            raise ValueError('info roothash is not 20-byte string')
    else:
        p = info['pieces']
        if type(p) != StringType or len(p) % 20 != 0:
            raise ValueError('info pieces is not multiple of 20 bytes')
        
    if 'length' in info:
        # single-file torrent
        if 'files' in info:
            raise ValueError('info may not contain both files and length key')
        
        l = info['length']
        if type(l) != IntType:
            raise ValueError('info length is not int')
    else:
        # multi-file torrent
        if 'length' in info:
            raise ValueError('info may not contain both files and length key')
        
        files = info['files']
        if type(files) != ListType:
            raise ValueError('info files not list')
        
        filekeys = ['path','length']
        for file in files:
            for key in filekeys:
                if key not in file:
                    raise ValueError('info files missing path or length key')
            
            p = file['path']
            if type(p) != ListType:
                raise ValueError('info files path is not list')
            for dir in p:
                if type(dir) != StringType:
                    raise ValueError('info files path is not string')
            
            l = file['length']
            if type(l) != IntType:
                raise ValueError('info files length is not int')
            
    # common additional fields
    if 'announce-list' in metainfo:
        al = metainfo['announce-list']
        if type(al) != ListType:
            raise ValueErorr('announce-list is not list')
        for tier in al:
            if type(tier) != ListType:
                raise ValueErorr('announce-list tier is not list '+`tier`)
            for url in tier:
                if not isValidURL(url):
                    raise ValueError('announce-list url is not valid '+`url`)

    if 'azureus_properties' in metainfo:
        azprop = metainfo['azureus_properties']
        if type(azprop) != DictType:
            raise ValueError('azureus_properties is not dict')
        if 'Content' in azprop:
                content = azprop['Content']
                if type(content) != DictType:
                    raise ValueError('azureus_properties content is not dict')
                if 'thumbnail' in content:
                    thumb = content['thumbnail']
                    if type(content) != StringType:
                        raise ValueError('azureus_properties content thumbnail is not string')
    
    
def isValidTorrentFile(metainfo):
    try:
        validTorrentFile(metainfo)
        return True
    except:
        return False
    
    
def isValidURL(url):
    r = urlparse.urlsplit(url)
    if r[0] == '' or r[1] == '' or r[2] == '':
        return False
    return True
    
def show_permid(permid):
    # Full BASE64-encoded 
    if not permid:
        return 'None'
    return encodestring(permid).replace("\n","")
    # Short digest
    ##return sha(permid).hexdigest()

def show_permid_short(permid):
    if not permid:
        return 'None'
    s = encodestring(permid).replace("\n","")
    return s[-10:]
    #return encodestring(sha(s).digest()).replace("\n","")

def show_permid_shorter(permid):
    if not permid:
        return 'None'
    s = encodestring(permid).replace("\n","")
    return s[-5:]

def readableBuddyCastMsg(buddycast_data):
    # convert msg to readable format
    prefxchg_msg = deepcopy(buddycast_data)
    
    if prefxchg_msg.has_key('permid'):
        prefxchg_msg.pop('permid')
    if prefxchg_msg.has_key('ip'):
        prefxchg_msg.pop('ip')
    if prefxchg_msg.has_key('port'):
        prefxchg_msg.pop('port')
        
    name = repr(prefxchg_msg['name'])    # avoid coding error
    prefs = []
    if prefxchg_msg['preferences']:
        for pref in prefxchg_msg['preferences']:
            prefs.append(show_permid(pref))
    prefxchg_msg['preferences'] = prefs
        
    if prefxchg_msg.get('taste buddies', []):
        buddies = []
        for buddy in prefxchg_msg['taste buddies']:
            buddy['permid'] = show_permid(buddy['permid'])
            if buddy.get('preferences', []):
                prefs = []
                for pref in buddy['preferences']:
                    prefs.append(show_permid(pref))
                buddy['preferences'] = prefs
            buddies.append(buddy)
        prefxchg_msg['taste buddies'] = buddies
        
    if prefxchg_msg.get('random peers', []):
        peers = []
        for peer in prefxchg_msg['random peers']:
            peer['permid'] = show_permid(peer['permid'])
            peers.append(peer)
        prefxchg_msg['random peers'] = peers
        
    return prefxchg_msg
    
def print_prefxchg_msg(prefxchg_msg):
    def show_permid(permid):
        return permid
    print "------- preference_exchange message ---------"
    print prefxchg_msg
    print "---------------------------------------------"
    print "permid:", show_permid(prefxchg_msg['permid'])
    print "name", prefxchg_msg['name']
    print "ip:", prefxchg_msg['ip']
    print "port:", prefxchg_msg['port']
    print "preferences:"
    if prefxchg_msg['preferences']:
        for pref in prefxchg_msg['preferences']:
            print "\t", pref#, prefxchg_msg['preferences'][pref]
    print "taste buddies:"
    if prefxchg_msg['taste buddies']:
        for buddy in prefxchg_msg['taste buddies']:
            print "\t permid:", show_permid(buddy['permid'])
            #print "\t permid:", buddy['permid']
            print "\t ip:", buddy['ip']
            print "\t port:", buddy['port']
            print "\t age:", buddy['age']
            print "\t preferences:"
            if buddy['preferences']:
                for pref in buddy['preferences']:
                    print "\t\t", pref#, buddy['preferences'][pref]
            print
    print "random peers:"
    if prefxchg_msg['random peers']:
        for peer in prefxchg_msg['random peers']:
            print "\t permid:", show_permid(peer['permid'])
            #print "\t permid:", peer['permid']
            print "\t ip:", peer['ip']
            print "\t port:", peer['port']
            print "\t age:", peer['age']
            print    
            
def print_dict(data, level=0):
    if isinstance(data, dict):
        print
        for i in data:
            print "  "*level, str(i) + ':',
            print_dict(data[i], level+1)
    elif isinstance(data, list):
        if not data:
            print "[]"
        else:
            print
        for i in xrange(len(data)):
            print "  "*level, '[' + str(i) + ']:',
            print_dict(data[i], level+1)
    else:
        print data
        
def friendly_time(old_time):
    curr_time = time()
    try:
        old_time = int(old_time)
        assert old_time > 0
        diff = int(curr_time - old_time)
    except:
        if isinstance(old_time, str):
            return old_time
        else:
            return '?'
    if diff < 0:
        return '?'
    elif diff < 2:
        return str(diff) + " sec. ago"
    elif diff < 60:
        return str(diff) + " secs. ago"
    elif diff < 120:
        return "1 min. ago"
    elif diff < 3600:
        return str(int(diff/60)) + " mins. ago"
    elif diff < 7200:
        return "1 hour ago"
    elif diff < 86400:
        return str(int(diff/3600)) + " hours ago"
    elif diff < 172800:
        return "Yesterday"
    elif diff < 259200:
        return str(int(diff/86400)) + " days ago"
    else:
        return strftime("%d-%m-%Y", gmtime(old_time))
        
def sort_dictlist(dict_list, key, order='increase'):
    
    aux = []
    for i in xrange(len(dict_list)):
        #print >>sys.stderr,"sort_dictlist",key,"in",dict_list[i].keys(),"?"
        if key in dict_list[i]:
            aux.append((dict_list[i][key],i))
    aux.sort()
    if order == 'decrease' or order == 1:    # 0 - increase, 1 - decrease
        aux.reverse()
    return [dict_list[i] for x, i in aux]


def dict_compare(a, b, keys):
    for key in keys:
        order = 'increase'
        if type(key) == tuple:
            skey, order = key
        else:
            skey = key

        if a.get(skey) > b.get(skey):
            if order == 'decrease' or order == 1:
                return -1
            else:
                return 1
        elif a.get(skey) < b.get(skey):
            if order == 'decrease' or order == 1:
                return 1
            else:
                return -1

    return 0


def multisort_dictlist(dict_list, keys):

    listcopy = copy.copy(dict_list)
    cmp = lambda a, b: dict_compare(a, b, keys)
    listcopy.sort(cmp=cmp)
    return listcopy


def find_content_in_dictlist(dict_list, content, key='infohash'):
    title = content.get(key)
    if not title:
        print 'Error: content had no content_name'
        return False
    for i in xrange(len(dict_list)):
        if title == dict_list[i].get(key):
            return i
    return -1

def remove_torrent_from_list(list, content, key = 'infohash'):
    remove_data_from_list(list, content, key)

def remove_data_from_list(list, content, key = 'infohash'):
    index = find_content_in_dictlist(list, content, key)
    if index != -1:
        del list[index]
    
def sortList(list_to_sort, list_key, order='decrease'):
        aux = zip(list_key, list_to_sort)
        aux.sort()
        if order == 'decrease':
            aux.reverse()
        return [i for k, i in aux]    

def getPlural( n):
        if n == 1:
            return ''
        else:
            return 's'


def find_prog_in_PATH(prog):
    envpath = os.path.expandvars('${PATH}')
    if sys.platform == 'win32':
        splitchar = ';'
    else:
        splitchar = ':'
    paths = envpath.split(splitchar)
    foundat = None
    for path in paths:
        fullpath = os.path.join(path,prog)
        if os.access(fullpath,os.R_OK|os.X_OK):
            foundat = fullpath
            break
    return foundat
    

if __name__=='__main__':

    torrenta = {'name':'a', 'swarmsize' : 12}
    torrentb = {'name':'b', 'swarmsize' : 24}
    torrentc = {'name':'c', 'swarmsize' : 18, 'Web2' : True}
    torrentd = {'name':'b', 'swarmsize' : 36, 'Web2' : True}

    torrents = [torrenta, torrentb, torrentc, torrentd]
    print multisort_dictlist(torrents, ["Web2", ("swarmsize", "decrease")])


    #d = {'a':1,'b':[1,2,3],'c':{'c':2,'d':[3,4],'k':{'c':2,'d':[3,4]}}}
    #print_dict(d)    
