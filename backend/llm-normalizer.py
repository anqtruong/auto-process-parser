import anthropic

client = anthropic.Anthropic()

'''
This is currently just code pasted from Claude's Message API docs. 
'''

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What should I search for to find the latest developments in renewable energy?",
        }
    ],
)
print(message.content)