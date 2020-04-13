#import os
import sys
sys.path.append('..')
from modes import InputMode, ReplyType
from communication import QueryOpen, QueryChoice, QueryMultipleChoices, QueryBoolean, QueryMemory

# song_dir_in = 'test_songs'
# song_dir_out = 'songs_out'

class locutor():
    
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name

maker = locutor('music-sheet-maker')
cog = locutor('music-cog')

brain = QueryMemory(cog)

print('\n\n####Testing QueryOpen####\n')

q_open = QueryOpen(sender=cog, recipient=maker, question='What is your name?', foreword='', afterword=None,
                   reply_type=ReplyType.TEXT, limits='')
brain.store(q_open)

#q_open.send()
q_open.reply_to('Tracey')

print(q_open)
print(q_open.get_reply())
print('\n')
print(q_open.get_result())
print(q_open.get_reply().get_result())

regex = r'([ABCDEFGabcdefg][b#]?\d)'
q_open2 = QueryOpen(sender=cog, recipient=maker, question='What is the song key?', foreword='', afterword=None,
                    reply_type=ReplyType.NOTE, limits=regex)
brain.store(q_open2)

#q_open2.send()
q_open2.reply_to('Ab6')

print(q_open2)
print(q_open2.get_reply())
print('\n')
print(q_open2.get_result())
print(q_open2.get_reply().get_result())

print('\n\n####Testing QueryBoolean####\n')

choices = ('dad', 'mom')
q_boolean = QueryBoolean(sender=cog, recipient=maker, question='Which one do you prefer?', foreword='',
                         afterword=None, reply_type=ReplyType.TEXT, limits=choices)
brain.store(q_boolean)

#q_boolean.send()
q_boolean.reply_to('myself')  # testing out of range reply
q_boolean.reply_to('dad')  # testing answering twice

print(q_boolean)
print(q_boolean.get_reply())
print(q_boolean.get_result())
print(q_boolean.get_reply().get_result())

q_boolean2 = QueryBoolean(sender=cog, recipient=maker, question='Are you happy?', foreword='', afterword=None,
                          reply_type=ReplyType.TEXT, limits='yn')
brain.store(q_boolean2)

#q_boolean2.send()
q_boolean2.reply_to('y')  # testing out of initial limits reply

print(q_boolean2)
print(q_boolean2.get_reply())
print('\n')
print(q_boolean2.get_result())
print(q_boolean2.get_reply().get_result())


q_boolean3 = QueryBoolean(sender=cog, recipient=maker, question='Are you happy?', foreword='', afterword=None,
                          reply_type=ReplyType.TEXT, limits='yn')
brain.store(q_boolean3)
#q_boolean3.send()


print('\n\n####Testing QueryChoice####\n')

modes_list = [InputMode.JIANPU, InputMode.SKY]
q_choice = QueryChoice(sender=cog, recipient=maker, question="Mode (1-" + str(len(modes_list)) + "): ",
                       foreword="Please choose your note format:\n", afterword=None, reply_type=ReplyType.INPUTMODE,
                       limits=modes_list)
brain.store(q_choice)

#q_choice.send()
q_choice.reply_to('1')

print(q_choice)
print(q_choice.get_reply())
print('\n')
print(q_choice.get_result())
print(q_choice.get_reply().get_result())

print('\n\n####Below the result of brain testing')

print('\nAll queries:\n')
for q in brain.recall():
    print(q)

print('\nUnsent queries:\n')
for q in brain.recall_unsent():
    print(q)

print('\nUnreplied queries:\n')
for q in brain.recall_unreplied():
    print(q)

print('\n\nQueries with invalid reply:\n')
for q in brain.recall_by_invalid_reply():
    print(q)
    print(q.get_reply())

print('\nRepeated queries:\n')
for q in brain.recall_repeated():
    print(q)
    
brain.erase_repeated()
print('\nRepeated queries after cleaning:\n')
for q in brain.recall_repeated():
    print(q)

print('\n\nStored TEXT queries:\n')
qs = brain.recall(ReplyType.TEXT)
[print(q) for q in qs]

print('\n\nBrain inventory:\n')
print(brain)

q_file = QueryOpen(sender=cog,recipient=maker,question='Please reply a file name',reply_type=ReplyType.FILEPATH,limits=('../test_songs','.txt','.py'))
brain.store(q_file)
q_file.reply_to('englishC.txt')

print('\n####Testing file name handling\n###')
print(q_file)

###Testing topological sort
graph = QueryMemory('main')
q5 = QueryOpen(sender=cog, recipient=maker, question='5', prerequisites=[])
q7 = QueryOpen(sender=cog, recipient=maker, question='7', prerequisites=[])
q3 = QueryOpen(sender=cog, recipient=maker, question='3', prerequisites=[])
q11 = QueryOpen(sender=cog, recipient=maker, question='11', prerequisites=[q5, q7])
q8 = QueryOpen(sender=cog, recipient=maker, question='8', prerequisites=[q7, q3])
q2 = QueryOpen(sender=cog, recipient=maker, question='2', prerequisites=[q11])
q9 = QueryOpen(sender=cog, recipient=maker, question='9', prerequisites=[q11, q8])
q10 = QueryOpen(sender=cog, recipient=maker, question='10', prerequisites=[q11, q3])
graph.store([q5, q7, q3, q11, q8, q2, q9, q10])

print('\n\nGraph of dependencies:\n')
for i in range(len(graph)):
    print(graph.recall(i))

graph.topological_sort()

print('\n\nSorted Graph:\n')
for i in range(len(graph)):
    print(graph.recall(i))

test_dict = {'sender': cog, 'recipient': maker, 'question': 'how are you?'}
test_q = QueryOpen(**test_dict)


