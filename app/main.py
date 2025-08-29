from fastapi import FastAPI

app = FastAPI(title='Omnichannel Conversational Platform')

@app.get('/')
async def root():
    return {"message": "OmniConversationAI backend is running"}
