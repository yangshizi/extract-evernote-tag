# -*- coding: utf-8 -*-
'''''
    @author: Yang
    @created 2016-01-11 22:10:03
'''''
class Ner(object):

    content = ''
    collect_type = ['person_name','company_name','location','org_name','product_name','job_title']
    entity_dict = {}
    entity_list = []
    typeDict = {}

    def __init__(self,content):
        self.content = content

    @property
    def allType(self):
        return self.typeDict.keys()

    def process(self,nlp):
        return self.__request(nlp).__format()

    def __request(self,nlp):
        self.result = nlp.ner(self.content)[0]
        self.words = self.result['word']
        self.entities = self.result['entity']
        return self

    def __format(self):
        entity_dict = {}
        for item in self.entities:
            name = ''.join(self.words[item[0]:item[1]])
            type_name = item[2].encode('ascii')

            try:
                if entity_dict.has_key(name):
                    entity_dict[name]['count'] += 1
                else:
                    entity_dict[name] = {'name':name,'type':type_name,'count':1}

                if self.typeDict.has_key(type_name):
                    self.typeDict[type_name] += 1
                else:
                    self.typeDict[type_name] = 1
            except KeyError as e:
                print type(e)
                print e
                print entity_dict[name]
                print entity_dict.has_key(name)
                print self.typeDict
                exit(1)

        self.entity_dict = entity_dict
        self.entity_list = entity_dict.values()
        return self

    def entity_filter(self, count=0, type=None):
        if type:
            entity_list =  [item for item in self.entity_list if item['count']>=count and item['type']==type]
        else:
            entity_list = [item for item in self.entity_list if item['count']>=count]

        entity_list.sort(key=lambda x:x['count'],reverse=True)
        return entity_list

    def collect_type_entity(self,count=0):
        collection = []
        for type in self.collect_type:
            collection.extend([item['name'] for item in self.entity_filter(count=count,type=type)])
        return collection