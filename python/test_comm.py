#import os
from modes import InputMode, ReplyType
from communication import QueryOpen, QueryChoice, QueryBoolean, QueryMemory

# song_dir_in = 'test_songs'
# song_dir_out = 'songs_out'

brain = QueryMemory()

print('\n\n####Testing QueryOpen####\n')

q_open = QueryOpen(sender='music-cog', recipient='bot', question='What is your name?', foreword='', afterword=None,
                   reply_type=ReplyType.TEXT, limits='')
brain.store(q_open)

q_open.send()
q_open.receive('Tracey')

print(q_open)
print(q_open.get_reply())
print('\n')
print(q_open.get_result())
print(q_open.get_reply().get_result())

regex = r'([ABCDEFGabcdefg][b#]?\d)'
q_open2 = QueryOpen(sender='music-cog', recipient='bot', question='What is the song key?', foreword='', afterword=None,
                    reply_type=ReplyType.NOTE, limits=regex)
brain.store(q_open2)

q_open2.send()
q_open2.receive('Ab6')

print(q_open2)
print(q_open2.get_reply())
print('\n')
print(q_open2.get_result())
print(q_open2.get_reply().get_result())

print('\n\n####Testing QueryBoolean####\n')

choices = ('dad', 'mom')
q_boolean = QueryBoolean(sender='music-cog', recipient='bot', question='Which one do you prefer?', foreword='',
                         afterword=None, reply_type=ReplyType.TEXT, limits=choices)
brain.store(q_boolean)

q_boolean.send()
q_boolean.receive('myself')  # testing out of range reply
q_boolean.receive('dad')  # testing answering twice

print(q_boolean)
print(q_boolean.get_reply())
print(q_boolean.get_result())
print(q_boolean.get_reply().get_result())

q_boolean2 = QueryBoolean(sender='music-cog', recipient='bot', question='Are you happy?', foreword='', afterword=None,
                          reply_type=ReplyType.TEXT, limits='yn')
brain.store(q_boolean2)

q_boolean2.send()
q_boolean2.receive('y')  # testing out of initial limits reply

print(q_boolean2)
print(q_boolean2.get_reply())
print('\n')
print(q_boolean2.get_result())
print(q_boolean2.get_reply().get_result())


q_boolean3 = QueryBoolean(sender='music-cog', recipient='bot', question='Are you happy?', foreword='', afterword=None,
                          reply_type=ReplyType.TEXT, limits='yn')
brain.store(q_boolean3)
q_boolean3.send()


print('\n\n####Testing QueryChoice####\n')

modes_list = [InputMode.JIANPU, InputMode.SKY]
q_choice = QueryChoice(sender='music-cog', recipient='bot', question="Mode (1-" + str(len(modes_list)) + "): ",
                       foreword="Please choose your note format:\n", afterword=None, reply_type=ReplyType.INPUTMODE,
                       limits=modes_list)
brain.store(q_choice)

q_choice.send()
q_choice.receive('1')

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

print('\n\nQueries with invalid replies:\n')
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

'''
print('\n\nBrain inventory:\n')
brain.erase('all')
print(brain)
'''
