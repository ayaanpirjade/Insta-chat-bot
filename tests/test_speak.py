from maininstabot.src.command_parser import parse_command

# Test 1: Parser
cmd, args = parse_command("!speak what is your name", "!")
print(f"CMD: {cmd!r}")
print(f"ARGS: {args!r}")
print()

# Test 2: Direct tts call
from maininstabot.src import tts
result = tts.handle_speak_command(
    cl=None,
    thread_id="123",
    msg=None,
    user_id="456",
    username="test",
    args="hello baby"
)
print(f"Result: {result!r}")