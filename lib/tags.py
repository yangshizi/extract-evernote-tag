# -*- coding: utf-8 -*-
'''''
    @author: Yang
    @created 2016-01-11 22:10:03
'''''
import evernote.edam.type.ttypes as Types
class Tags(Types.Tag):
    tags = {}
    evernote_note_store = None
    def __init__(self,tags = {},note_store=None):
        if not note_store:
            self.tags = tags
        else:
            self.set_evernote_note_store(note_store)

    def add(self,tag):
        tag = tag.replace(',','')# , 不允许使用
        tag_key = tag.upper()
        if not self.exist(tag_key):
            self.tags.setdefault(tag_key,{'name':tag})
            if self.evernote_note_store:
                evernote_tag = Types.Tag()
                evernote_tag.name = tag.encode('utf-8')
                self.tags[tag_key] = self.evernote_note_store.createTag(evernote_tag)
        return self.tags[tag_key]

    def get(self,tag):
        return self.tags[tag.upper()]

    def exist(self,tag):
        return self.tags.has_key(tag.upper())

    def set_evernote_note_store(self,note_store):
        self.evernote_note_store = note_store
        evernote_tags = note_store.listTags()
        for tag in evernote_tags:
            name = tag.name.decode('utf-8')
            self.tags[name.upper()] = tag