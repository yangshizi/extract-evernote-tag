#!/usr/bin/env python
# coding=utf-8
import hashlib
import binascii
import os
import codecs
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import json
from cStringIO  import StringIO
from evernote.api.client import EvernoteClient
from bosonnlp import BosonNLP
from evernote.edam.notestore import NoteStore

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import htmlentitydefs


class AllEntities:
    def __getitem__(self, key):
        return unichr(htmlentitydefs.name2codepoint[key])

DEBUG  = False
data_file_dict = {'sync_state':'./data/sync_state.json'}

def data_file(file):
    return data_file_dict[file]

def note_file(guid):
    return './data/note/'+guid+'.txt'

def get_current_sync_state(note_store):
    currnet_sync_state = note_store.getSyncState()
    with open(data_file('sync_state'), 'w') as f:
        json.dump(currnet_sync_state.__dict__, f)
    return currnet_sync_state



def main():
    global last_extrect_tag_time, last_extrect_tag_time
    token = json.load(open('./config/token.json','r'))
    if DEBUG:
        client = EvernoteClient(token=token['en_token'],sandbox=True)
    else:
        client = EvernoteClient(token=token['en_token'])
        client.service_host = 'app.yinxiang.com'

    print '现在服务器是:',client._get_endpoint()
    #bosonNlp
    nlp = BosonNLP(token['boson_nlp_token'])
    note_store = client.get_note_store()



    #获取上一次同步状态
    if os.path.exists(data_file('sync_state')):
        last_sync_state = json.load(open(data_file('sync_state'),'r'))
        last_update_count = last_sync_state['updateCount']
        last_extrect_tag_time = last_sync_state['currentTime']

    #获取当前同步状态
    currnet_sync_state = get_current_sync_state(note_store)

    if currnet_sync_state.updateCount > last_update_count:
        new_updated_count = currnet_sync_state.updateCount - last_update_count
        print currnet_sync_state.__dict__
        new_note_filter = NoteStore.NoteFilter()
        new_note_filter.order = Types.NoteSortOrder.CREATED
        new_notes = note_store.findNotes(new_note_filter,0,new_updated_count)
        print 'totalNumber:%d\tNoteListNum:%d' %(new_notes.totalNotes,len(new_notes.notes))
    else:
        print('没有新增更新...')
        exit(1)

    # 获取用户的所有tags
    allTags = note_store.listTags()
    my_tags = {}
    print '标签云:\n'
    for tag in allTags:
        #DEBUG
        #print "guid: %s\tname:%s" %(tag.guid,tag.name)
        tag_name = tag.name.decode('utf-8').upper()
        my_tags[tag_name] = tag.guid
    print '  '.join(my_tags.keys())

    #操作新note
    for note in new_notes.notes:
        #如果笔记创建时间小于上次同步时间
        if note.created <= last_extrect_tag_time:
            continue
        print '\n'+'*'*120
        content = note_store.getNoteContent(note.guid)
        print "guid:%s\ntitle:%s\ncreated:%s\n作者:%s" %(note.guid,note.title,note.created,note.attributes.author)

        print 'author:%s\nsource:%s\nsourceURL:%s\nsourceApplication:%s' %(note.attributes.author,note.attributes.source,note.attributes.sourceURL,note.attributes.sourceApplication)

        if not note.attributes.sourceURL:
            continue
        print "现有标签(tags):%s" %(",".join(note_store.getNoteTagNames(note.guid)))
        print '-'*120
        #print "内容(%d):created:%s,\n%s" %(note.contentLength,note.created,content)

        #解析note xml 提取出所有的文字
        try:
            parser = ET.XMLParser()
            parser.entity['nbsp'] = ''
            parser.entity['ldquo'] = ''
            parser.entity['rdquo'] = ''
            parser.entity['hellip'] = ''
            tree = ET.parse(StringIO(content),parser=parser)
        except Exception,data:
            print 'ElementTree parser error'
            print content
            print 'errorData:'
            print data
            print 'exception:'
            print Exception
            exit(1)
        en_note = tree.findall('.')[0]

        content_string = ''.join(en_note.itertext())

        #写入文件
        with codecs.open(note_file(note.guid),'w+',encoding='utf-8') as f:
            f.write(content_string)
        #通过 BosonNLP 拿到文章的关键字
        extract_keywords =  nlp.extract_keywords(content_string,top_k=20)
        keywords = [item[1].upper() for item in extract_keywords]
        print '通过 BosonNLP 拿到文章的关键字:'
        for keyword in extract_keywords:
            print '%s \t %s' %(keyword[1],keyword[0])

        #对比 找出交集tag的guid
        new_tag_guid = []
        for keyword in keywords:
            keyword = keyword.upper()
            if my_tags.get(keyword):
                new_tag_guid.append(my_tags.get(keyword))
        newKeyWords = [item for item in set(my_tags.keys()) if item in set(keywords)]
        print '\nBosonNLP与已有的tags交集:'
        print '\t'.join(newKeyWords)

        #追加新笔记的tags
        if note.tagGuids:
            note.tagGuids = note.tagGuids.extend(new_tag_guid)
        else:
            note.tagGuids = new_tag_guid
        note_store.updateNote(note)

        #重新获取同步状态更新
    get_current_sync_state(note_store)
if __name__ == '__main__':
    main()