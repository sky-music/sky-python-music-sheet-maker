#!/usr/bin/env python3
from music_sheet_maker import MusicSheetMaker
from communicator import Communicator
#from modes import ResponseMode
#song_responder = Responder()
#song_responder.set_response_mode(ResponseMode.COMMAND_LINE)
#song_responder.create_song_command_line()
me = 'bot'


comm = Communicator(owner=me)

maker = MusicSheetMaker()

q = comm.formulate('song_creation')
comm.store(q)
q.send(recipient=maker)

#maker.ask



