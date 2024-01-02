import settings
from models import VideoLiveMessage, SentimentType
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from kafka import KafkaProducer
from kafka import KafkaConsumer
from pprint import pprint
import orjson
import logging
import sys
import typer
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                    handlers=[
                        logging.FileHandler('process.log'),
                        logging.StreamHandler()
                    ])


logger = logging.getLogger(__name__)

app = typer.Typer()


# Define class to analyze message received from "scraper.py" file
class Analyser:
    def __init__(self, sentiment: bool = True, profanity: bool = False) -> None:
        self.server = settings.KAFKA_SERVER  # Get the kafka URL
        self.consume_topic = settings.RAW_TOPIC  # Get the consumer topic's name
        self.produce_topic = settings.ANALYZED_TOPIC  # Get the producer topic's name
        self.enable_sentiment = sentiment

    # Start the consumer topic to consume message from scraper 
    def __start_consumer(self):
        self.consumer = KafkaConsumer(
            self.consume_topic, bootstrap_servers=self.server)
        logger.info(
            f'Started Analyser to consume on topic: {self.consume_topic}')

    # Start the producer topic for analyzing
    def __start_producer(self):
        self.producer = KafkaProducer(bootstrap_servers=self.server)
        logger.info(
            f'Started Producer to produce on topic: {self.produce_topic}')

    # Start the sentiment analyzer
    def __start_analyzers(self):
        if self.enable_sentiment:
            self.sentiment = SentimentIntensityAnalyzer()

    # Start the working pipe
    def __start_session(self):
        self.__start_consumer()
        self.__start_producer()
        self.__start_analyzers()

        while True:
            for message in self.receive_upstream(): # Get the raw message from "scraper.py" file
                processed = self.process_message(raw_message=message) # Process the message
                if processed:
                    self.send_downstream(processed) # Once finished processing, send the processed message to the producer

    # Get the message received from the "scraper.py" file (consumer topic)
    def receive_upstream(self):
        for message in self.consumer:
            raw_message = message.value
            yield raw_message

    # Get the sentiment of a sentence
    def get_sentiment(self, message: str):
        sentiment_dict = self.sentiment.polarity_scores(message) # Get the analyzed dictionary
        if sentiment_dict['compound'] >= 0.05: # If the sentiment intensity score > 0.05 => Positive
            return SentimentType.POSITIVE
        elif sentiment_dict['compound'] <= -0.05: # < -0.05 => Negative
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL # Else => Neutral


    # Process the message
    def process_message(self, raw_message):
        json_message = orjson.loads(raw_message) # Parse the raw message receive from the scraper.py file as JSON format
        if json_message['info_type'] != 'VIDEO_LIVE_MESSAGE': # Check if the received message's info is a video live chat or not
            return raw_message # If not video live chat => return raw message

        message_obj = VideoLiveMessage(**json_message) # If message is video live chat => Create message object based on the defined model.

        message_obj.inferred_sentiment = self.get_sentiment(message_obj.message_content) # Get the sentiment of the message


        logger.info(f'Completed analysis for :{message_obj}')
        return message_obj.to_json()

    # Send the processed message to the producer
    def send_downstream(self, message):
        self.producer.send(self.produce_topic, message)

    
    def analyse(self):
        self.__start_session()


@app.command()
def run(sentiment: bool = True, profanity: bool = False):
    process = Analyser(sentiment=sentiment, profanity=profanity)
    process.analyse()


if __name__ == '__main__':
    app()
