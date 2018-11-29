config = {
    'skill_name': 'Coffee Maker'
}

replay = [
    {
        'text': '<prosody volume="x-loud">{maker}, <break time="500ms"/> {user} want a {coffee}</prosody>',
        'card': '{maker}, {user} want a {coffee}'
    },
    {
        'text': '<prosody volume="x-loud">{maker}, <break time="500ms"/> make a {coffee} for {user}. NOW</prosody>',
        'card': '{maker}, make a {coffee} for {user}. NOW!'
    },
    {
        'text': '<prosody volume="x-loud">{maker}, <break time="500ms"/> please make a {coffee} for {user}</prosody>',
        'card': '{maker}, please make a {coffee} for {user}',
    },
    {
        'text': '<prosody volume="x-loud">{maker}, <break time="500ms"/> guess who want to drink a {coffee}? <break time="1s"/> Right, <break time="500ms"/> {user} want to drink a {coffee}</prosody>',
        'card': '{maker}, guess who want to drink a {coffee}? Right, {user} want to drink a {coffee}'
    }
]
