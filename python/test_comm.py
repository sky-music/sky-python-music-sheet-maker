import os
from modes import InputMode, ReplyType
from communication import QueryOpen, QueryChoice, QueryBoolean, QueryMemory


song_dir_in = 'test_songs'
song_dir_out = 'songs_out'

brain = QueryMemory()

modes_list = [InputMode.JIANPU, InputMode.SKY]
q = QueryChoice(sender='music-cog', recipient='bot', question="Mode (1-" + str(len(modes_list)) + "): ", foreword="Please choose your note format:\n", afterword=None, reply_type=ReplyType.INPUTMODE, limits=modes_list)

q.send()
brain.store(q)

print(q)

choices = ('dad', 'mom')
q = QueryBoolean(sender='music-cog', recipient='bot', question='Which one do you prefer?', foreword='', afterword=None, reply_type=ReplyType.TEXT, limits=choices)

q.send()
brain.store(q)

print(q)

q.receive_reply('myself')


print('\n####Below the result of brain testing\n')
print(brain.recall_last())

print('Pending queries:\n')
for q in brain.get_pending():
	print(q)
	print('')

print('\n Stored TEXT queries:')
qs = brain.recall(ReplyType.TEXT)
[print(q) for q in qs]

print(brain)
q = brain.recall_last()
brain.erase(q)
print(brain)
