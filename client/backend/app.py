from fastapi import FastAPI, Request
from pymongo import MongoClient
import settings
import uvicorn
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print('Connecting to MongoDB:', settings.MONGO_URL)

# connect to server
client = MongoClient(settings.MONGO_URL)
db = client.main # Get or create database with name "main"
message_collection = db.live # Get collection name "live"
info_collection = db.info # Get collection name "info"


# Yield the response everytime there is a change in the "live" collection
async def read_stream():
    change_stream = message_collection.watch() # Watch changes from the "live" collection (Get the change_stream object)
    while True: # While there is a change in the "live" collection (If the change_stream object exist.)
        for change in change_stream: # Iterate over the changes
            if change['operationType'] == 'insert': # If the change is made by insertion
                doc = change['fullDocument'] # Get the inserted document (this is a dictionary)
                doc.pop('_id') # pop out the "_id" field
                response = {"data": doc, "event": "message"} # create the json format for the response
                yield response 

# When a client connects to this endpoint, it will receive a continuous stream of server-sent events (SSE) representing changes in the MongoDB collection.
@app.get("/stream")
async def stream_changes(request: Request):

    return EventSourceResponse(read_stream()) # The stream


# Get video info (name, views, time, ....)
@app.get("/video/{video_id}")
async def get_video(video_id: str):
    filter = {"video_id": video_id}
    result = info_collection.find_one(filter)
    result.pop('_id')
    return result


@app.on_event("shutdown")
async def shutdown_event():
    client.close()


if __name__ == '__main__':
    uvicorn.run("app:app", port=3000, reload=True)
