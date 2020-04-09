import asyncio
import sys
sys.path.append('..')
from concurrent.futures import ThreadPoolExecutor
from command_line_player import CommandLinePlayer
from music_sheet_maker import MusicSheetMaker

#A method declared with async def ... must be called with await, or run in an asyncio executor


async def ainput(prompt: str = ""):
    #with ThreadPoolExecutor(max_workers=1, thread_name_prefix="AsyncInput", initializer=lambda x: print(x, end="", flush=True), initargs=(prompt,)) as executor:
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="AsyncInput") as executor:
        print(prompt)
        return (await asyncio.get_event_loop().run_in_executor(executor, sys.stdin.readline)).rstrip()


async def main():
    
    toto = CommandLinePlayer()
    #name = await ainput("What's your name? ")
    #print("Hello, {}!".format(name))
    #await means: Suspend execution of main() until the result of ainput() is returned
    return


if asyncio.get_event_loop().is_closed():
    asyncio.set_event_loop(asyncio.new_event_loop())
    
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except:
    pass
