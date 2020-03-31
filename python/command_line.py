#!/usr/bin/env python3
from responder import Responder
from modes import ResponseMode

try:
    import readline
except ModuleNotFoundError:
    pass  # probably Windows

song_responder = Responder()
song_responder.set_response_mode(ResponseMode.COMMAND_LINE)
song_responder.create_song_command_line()
