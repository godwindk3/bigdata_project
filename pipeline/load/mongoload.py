from kafka import KafkaConsumer
from pymongo import MongoClient
import orjson
import settings
from pprint import pprint
import logging
import sys
import typer
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                    handlers=[
                        logging.FileHandler('loader.log'),
                        logging.StreamHandler()
                    ])


logger = logging.getLogger(__name__)

app = typer.Typer()

logger = logging.getLogger(__name__)


class MongoLoader:
    # Init connection URL to Kafka server and mongodb's server
    def __init__(self) -> None:
        self.server = settings.KAFKA_SERVER 
        self.connection_url = settings.MONGO_DB_URL

    # Connect to mongodb
    def init_db(self):
        client = MongoClient(self.connection_url)
        self.client = client

        try:
            client.admin.command('ping')
            logger.info('Ping db successfully.')
        except Exception as e:
            logger.exception(e, stack_info=True)
            exit(1)
        db = self.client.main # Get or create database with name "main"
        self.db = db

    # start consumer topic
    def __start_consumer(self):
        consume_topic = settings.ANALYZED_TOPIC # Get consumer topic's name
        self.consumer = KafkaConsumer(
            consume_topic, bootstrap_servers=self.server)
        logger.info(f'Started Kafka Consumer on topic :{consume_topic}')


    # get message in the consumer
    def receive_upstream(self):
        for message in self.consumer:
            raw_message = message.value # Get the message in byte format
            yield raw_message # yield the message receive from the consumer

    # Push the chat messages to db
    def push_to_db(self, json_message, collection_name):
        if collection_name not in self.db.list_collection_names(): # Check if collection_name is exist in mongodb's server, if not => create collection_name
            self.db.create_collection(collection_name)

        collection = self.db.get_collection(collection_name) # get collection
        response = collection.insert_one(json_message) # add the message in json form to collection
        logger.info(f'Inserted message with ID of:{response.inserted_id}')
        return response.inserted_id # return the id of the inserted message


    # create the process pipe
    def __start_session(self):
        self.init_db() # Init and connect to the mongodb, kafka server
        self.__start_consumer() # Start the consumer topic
        for message in self.receive_upstream(): # Get the message from the consumer topic
            json_message = orjson.loads(message) # Parse the message from bytes into JSON
            message_type = json_message['info_type'] # get the type of message
            if message_type == 'VIDEO_STATIC_INFO': # First type: video informations => push into "info" collection
                self.push_to_db(json_message, 'info')
            if message_type == 'VIDEO_LIVE_MESSAGE': # Second type: live chat message => push into "live" collection
                self.push_to_db(json_message, 'live')

    def load(self):
        try:
            self.__start_session()
        except Exception as e:
            print(e)
            logger.error(e)


@app.command()
def run():
    loader = MongoLoader()
    loader.load()


if __name__ == '__main__':
    app()
