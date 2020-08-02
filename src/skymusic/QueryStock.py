from src.skymusic.modes import ReplyType, AspectRatio, InstrumentType
from src.skymusic.communication import QueryOpen, QueryChoice, QueryMultipleChoices, Information
from src.skymusic import Lang

"""
NOTE ABOUT LIMITS

Limits should be a list (even though entering another iterable is possible)
For QueryChoice, it will be a list of choices
For QueryBoolean, it is a list of keywords grouped by pairs (yes, no, oui, non)

If a ReplyType is specified in reply_type, limits must be of the same type

For ReplyType.FILEPATH, it contains valid search directories and valid file extensions, in any order

For ReplyType.NUMBER, it is a list of [min, max, default], default being optional

For ReplyType.TEXT, limits can be a (compilable) regular expression

If a non-None value for 'default' is set, then a blank answer will revert to this value.
Otherwise, blank answers are forbidden

'expect_long_answer' is a special setting to display a textarea on the website

"""

def load(locale):
    
    return {
            # Queries asked by the Player / Music Cog
            'create_song': {'class': QueryOpen,
                            'handler': 'create_song',  # The name of the method that must be executed by the recipient
                            'question': 'create_song',
                            'reply_type': ReplyType.OTHER
                            },
        
            # Generic Query
            'information': {'class': Information,
                            'handler': 'None',
                            'question': '',
                            'reply_type': ReplyType.TEXT
                            },

            'instrument_type': {'class': QueryChoice,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/instrument_type/foreword", locale),
                             'question': Lang.get_string("stock_queries/instrument_type/question", locale),
                             'afterword': Lang.get_string("stock_queries/instrument_type/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/instrument_type/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/instrument_type/help_text", locale),
                             'reply_type': ReplyType.INSTRUMENT,
                             'limits': list(InstrumentType),
                             'default': InstrumentType.NORMAL
                             },
        
            'instructions_command_line': {'class': Information,
                                    'handler': 'None',
                                    'foreword': Lang.get_string("stock_queries/instructions_command_line/foreword", locale),
                                    'question': Lang.get_string("stock_queries/instructions_command_line/question", locale),
                                    'afterword': Lang.get_string("stock_queries/instructions_command_line/afterword", locale),
                                    'input_tip': Lang.get_string("stock_queries/instructions_command_line/input_tip", locale),
                                    'help_text': Lang.get_string("stock_queries/instructions_command_line/help_text", locale)
                                    },
        
           'instructions_sky_music_website': {'class': Information,
                                    'handler': 'None',
                                    'foreword': Lang.get_string("stock_queries/instructions_sky_music_website/foreword", locale),
                                    'question': Lang.get_string("stock_queries/instructions_sky_music_website/question", locale),
                                    'afterword': Lang.get_string("stock_queries/instructions_sky_music_website/afterword", locale),
                                    'input_tip': Lang.get_string("stock_queries/instructions_sky_music_website/input_tip", locale),
                                    'help_text': Lang.get_string("stock_queries/instructions_sky_music_website/help_text", locale)
                                    },
                                        
            'instructions_music_cog': {'class': Information,
                                    'handler': 'None',
                                    'foreword': Lang.get_string("stock_queries/instructions_music_cog/foreword", locale),
                                    'question': Lang.get_string("stock_queries/instructions_music_cog/question", locale),
                                    'afterword': Lang.get_string("stock_queries/instructions_music_cog/afterword", locale),
                                    'input_tip': Lang.get_string("stock_queries/instructions_music_cog/input_tip", locale),
                                    'help_text': Lang.get_string("stock_queries/instructions_music_cog/help_text", locale)
                                    },
        
            'render_modes': {'class': QueryMultipleChoices,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/render_modes/foreword", locale),
                             'question': Lang.get_string("stock_queries/render_modes/question", locale),
                             'afterword': Lang.get_string("stock_queries/render_modes/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/render_modes/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/render_modes/help_text", locale),
                             'reply_type': ReplyType.RENDERMODES,
                             'limits': [],
                             'default': 'all'
                             },
        
            'aspect_ratio': {'class': QueryChoice,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/aspect_ratio/foreword", locale),
                             'question': Lang.get_string("stock_queries/aspect_ratio/question", locale),
                             'afterword': Lang.get_string("stock_queries/aspect_ratio/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/aspect_ratio/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/aspect_ratio/help_text", locale),
                             'reply_type': ReplyType.ASPECTRATIO,
                             'limits': list(AspectRatio),
                             'default': AspectRatio.WIDESCREEN
                             },
        
            'song_bpm': {'class': QueryOpen,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/song_bpm/foreword", locale),
                             'question': Lang.get_string("stock_queries/song_bpm/question", locale),
                             'afterword': Lang.get_string("stock_queries/song_bpm/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/song_bpm/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/song_bpm/help_text", locale),
                             'reply_type': ReplyType.NUMBER,
                             'limits': [12, 1200],
                             'default': 220
                             },
        
        
            'song_title': {'class': QueryOpen,
                           'handler': 'None',
                           'foreword': Lang.get_string("stock_queries/song_title/foreword", locale),
                           'question': Lang.get_string("stock_queries/song_title/question", locale),
                           'afterword': Lang.get_string("stock_queries/song_title/afterword", locale),
                           'input_tip': Lang.get_string("stock_queries/song_title/input_tip", locale),
                           'help_text': Lang.get_string("stock_queries/song_title/help_text", locale),
                           'reply_type': ReplyType.TEXT,
                           'limits': None,
                           'default': Lang.get_string("song_meta/untitled", locale)
                           },
        
            'original_artist': {'class': QueryOpen,
                                'handler': 'None',
                                'foreword': Lang.get_string("stock_queries/original_artist/foreword", locale),
                                'question': Lang.get_string("stock_queries/original_artist/question", locale),
                                'afterword': Lang.get_string("stock_queries/original_artist/afterword", locale),
                                'input_tip': Lang.get_string("stock_queries/original_artist/input_tip", locale),
                                'help_text': Lang.get_string("stock_queries/original_artist/help_text", locale),
                                'reply_type': ReplyType.TEXT,
                                'limits': None,
                                'default': None #Required by Discord
                                },
        
            'transcript_writer': {'class': QueryOpen,
                                  'handler': 'None',
                                  'foreword': Lang.get_string("stock_queries/transcript_writer/foreword", locale),
                                  'question': Lang.get_string("stock_queries/transcript_writer/question", locale),
                                  'afterword': Lang.get_string("stock_queries/transcript_writer/afterword", locale),
                                  'input_tip': Lang.get_string("stock_queries/transcript_writer/input_tip", locale),
                                  'help_text': Lang.get_string("stock_queries/transcript_writer/help_text", locale),
                                  'reply_type': ReplyType.TEXT,
                                  'limits': None,
                                  'default': ''
                                  },
        
            'notes_file': {'class': QueryOpen,
                           'handler': 'None',
                           'foreword': Lang.get_string("stock_queries/notes_file/foreword", locale),
                           'question': Lang.get_string("stock_queries/notes_file/question", locale),
                           'afterword': Lang.get_string("stock_queries/notes_file/afterword", locale),
                           'input_tip': Lang.get_string("stock_queries/notes_file/input_tip", locale),
                           'help_text': Lang.get_string("stock_queries/notes_file/help_text", locale),
                           'reply_type': ReplyType.OTHER,
                           'expect_long_answer': True,
                           'limits': None
                           },
        
            'file': {'class': QueryOpen,
                     'handler': 'None',
                     'foreword': Lang.get_string("stock_queries/file/foreword", locale),
                     'question': Lang.get_string("stock_queries/file/question", locale),
                     'afterword': Lang.get_string("stock_queries/file/afterword", locale),
                     'input_tip': Lang.get_string("stock_queries/file/input_tip", locale),
                     'help_text': Lang.get_string("stock_queries/file/help_text", locale),
                     'reply_type': ReplyType.FILEPATH,
                     'limits': '.'
                     },
        
            'notes': {'class': QueryOpen,
                      'handler': 'None',
                      'foreword': Lang.get_string("stock_queries/notes/foreword", locale),
                      'question': Lang.get_string("stock_queries/notes/question", locale),
                      'afterword': Lang.get_string("stock_queries/notes/afterword", locale),
                      'input_tip': Lang.get_string("stock_queries/notes/input_tip", locale),
                      'help_text': Lang.get_string("stock_queries/notes/help_text", locale),
                      'reply_type': ReplyType.TEXT,
                      'expect_long_answer': True,
                      'limits': None,
                      'default': ''
                      },
        
            'one_input_mode': {'class': Information,
                               'handler': 'None',
                               'foreword': Lang.get_string("stock_queries/one_input_mode/foreword", locale),
                               'question': Lang.get_string("stock_queries/one_input_mode/question", locale),
                               'afterword': Lang.get_string("stock_queries/one_input_mode/afterword", locale),
                               'input_tip': Lang.get_string("stock_queries/one_input_mode/input_tip", locale),
                               'help_text': Lang.get_string("stock_queries/one_input_mode/help_text", locale)
                            },                               
                                                       
            'musical_notation': {'class': QueryChoice,
                                 'handler': 'None',
                                 'foreword': Lang.get_string("stock_queries/musical_notation/foreword", locale),
                                 'question': Lang.get_string("stock_queries/musical_notation/question", locale),
                                 'afterword': Lang.get_string("stock_queries/musical_notation/afterword", locale),
                                 'input_tip': Lang.get_string("stock_queries/musical_notation/input_tip", locale),
                                 'help_text': Lang.get_string("stock_queries/musical_notation/help_text", locale),
                                 'reply_type': ReplyType.INPUTMODE,
                                 'limits': []
                                 },
        
            'no_possible_key': {'class': Information,
                                'handler': 'None',
                                'foreword': Lang.get_string("stock_queries/no_possible_key/foreword", locale),
                                'question': Lang.get_string("stock_queries/no_possible_key/question", locale),
                                'afterword': Lang.get_string("stock_queries/no_possible_key/afterword", locale),
                                'input_tip': Lang.get_string("stock_queries/no_possible_key/input_tip", locale),
                                'help_text': Lang.get_string("stock_queries/no_possible_key/help_text", locale)
                                },
        
            'one_possible_key': {'class': Information,
                                 'handler': 'None',
                                 'foreword': Lang.get_string("stock_queries/one_possible_key/foreword", locale),
                                 'question': Lang.get_string("stock_queries/one_possible_key/question", locale),
                                 'afterword': Lang.get_string("stock_queries/one_possible_key/afterword", locale),
                                 'input_tip': Lang.get_string("stock_queries/one_possible_key/input_tip", locale),
                                 'help_text': Lang.get_string("stock_queries/one_possible_key/help_text", locale)
                                 },
        
            'possible_keys': {'class': QueryChoice,
                              'handler': 'None',
                              'foreword': Lang.get_string("stock_queries/possible_keys/foreword", locale),
                              'question': Lang.get_string("stock_queries/possible_keys/question", locale),
                              'afterword': Lang.get_string("stock_queries/possible_keys/afterword", locale),
                              'input_tip': Lang.get_string("stock_queries/possible_keys/input_tip", locale),
                              'help_text': Lang.get_string("stock_queries/possible_keys/help_text", locale),
                              'reply_type': ReplyType.NOTE,
                              'limits': []
                              },
        
            'recommended_key': {'class': QueryOpen,
                              'handler': 'None',
                              'foreword': Lang.get_string("stock_queries/recommended_key/foreword", locale),
                              'question': Lang.get_string("stock_queries/recommended_key/question", locale),
                              'afterword': Lang.get_string("stock_queries/recommended_key/afterword", locale),
                              'input_tip': Lang.get_string("stock_queries/recommended_key/input_tip", locale),
                              'help_text': Lang.get_string("stock_queries/recommended_key/help_text", locale),
                              'reply_type': ReplyType.NOTE,
                              'limits': None,
                              'default': 'C'
                              },
                            
            'octave_shift': {'class': QueryOpen,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/octave_shift/foreword", locale),
                             'question': Lang.get_string("stock_queries/octave_shift/question", locale),
                             'afterword': Lang.get_string("stock_queries/octave_shift/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/octave_shift/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/octave_shift/help_text", locale),
                             'reply_type': ReplyType.NUMBER,
                             'limits': [-6, 6],
                             'default': 0
                             },
        
            'one_song_file': {'class': Information,
                              'handler': 'None',
                              'foreword': Lang.get_string("stock_queries/one_song_file/foreword", locale),
                              'question': Lang.get_string("stock_queries/one_song_file/question", locale),
                              'afterword': Lang.get_string("stock_queries/one_song_file/afterword", locale),
                              'input_tip': Lang.get_string("stock_queries/one_song_file/input_tip", locale),
                              'help_text': Lang.get_string("stock_queries/one_song_file/help_text", locale)
                              },
        
            'several_song_files': {'class': Information,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/several_song_files/foreword", locale),
                             'question': Lang.get_string("stock_queries/several_song_files/question", locale),
                             'afterword': Lang.get_string("stock_queries/several_song_files/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/several_song_files/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/several_song_files/help_text", locale)
                             },
                             
            'no_song_file': {'class': Information,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/no_song_file/foreword", locale),
                             'question': Lang.get_string("stock_queries/no_song_file/question", locale),
                             'afterword': Lang.get_string("stock_queries/no_song_file/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/no_song_file/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/no_song_file/help_text", locale)
                             },
        
            'few_errors': {'class': Information,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/few_errors/foreword", locale),
                             'question': Lang.get_string("stock_queries/few_errors/question", locale),
                             'afterword': Lang.get_string("stock_queries/few_errors/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/few_errors/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/few_errors/help_text", locale)
                             },
                                                                                                                                           
            'many_errors': {'class': Information,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/many_errors/foreword", locale),
                             'question': Lang.get_string("stock_queries/many_errors/question", locale),
                             'afterword': Lang.get_string("stock_queries/many_errors/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/many_errors/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/many_errors/help_text", locale)
                             },
                             
            'empty_song': {'class': Information,
                           'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/empty_song/foreword", locale),
                             'question': Lang.get_string("stock_queries/empty_song/question", locale),
                             'afterword': Lang.get_string("stock_queries/empty_song/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/empty_song/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/empty_song/help_text", locale)
                             },
                             
            'skyjson_url': {'class': Information,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/skyjson_url/foreword", locale),
                             'question': Lang.get_string("stock_queries/skyjson_url/question", locale),
                             'afterword': Lang.get_string("stock_queries/skyjson_url/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/skyjson_url/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/skyjson_url/help_text", locale)
                             },
             
            'discord_ad': {'class': Information,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/discord_ad/foreword", locale),
                             'question': Lang.get_string("stock_queries/discord_ad/question", locale),
                             'afterword': Lang.get_string("stock_queries/discord_ad/afterword", locale),
                             'input_tip': Lang.get_string("stock_queries/discord_ad/input_tip", locale),
                             'help_text': Lang.get_string("stock_queries/discord_ad/help_text", locale)
                             }                  

            }
