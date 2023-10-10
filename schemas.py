from pydantic import BaseModel, Field


d = {'update_id': 706059211,
     'message':
        {    'message_id': 262,
             'from':
                 {
                     'id': 369027587,
                     'is_bot': False,
                     'first_name': 'Ivan',
                     'last_name': 'Shumilin',
                     'username': 'shumilinivan',
                     'language_code': 'ru'
                 },
             'chat':
                 {
                     'id': 369027587,
                     'first_name': 'Ivan',
                     'last_name': 'Shumilin',
                     'username': 'shumilinivan',
                     'type': 'private'
                 },
             'date': 1694010556,
             'reply_to_message':
             {
                 'message_id': 235,
                 'from':
                     {
                         'id': 6688209134,
                         'is_bot': True,
                         'first_name': 'BigBrotherBot',
                         'username': 'PetrushkaTrackerBot'
                     },
              'chat':
                  {
                      'id': 369027587,
                      'first_name': 'Ivan',
                      'last_name': 'Shumilin',
                      'username': 'shumilinivan',
                      'type': 'private'
                  },
              'date': 1694008573,
                 'text': 'Привет'},
         'location': {
             'latitude': 60.056501,
             'longitude': 30.43936
         }
         }
     }

class Location(BaseModel):
    latitude: float
    longitude: float

class FromTg(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: str = None
    username: str = None
    language_code: str

class Chat(BaseModel):
    id: int
    first_name: str
    last_name: str = None
    username: str = None
    type: str

class Message(BaseModel):
    message_id: int
    from_tg: FromTg = Field(alias='from')
    chat: Chat
    date: int
    text: str = None
    reply_to_message: dict = None
    location: Location = None

class Answer(BaseModel):
    update_id: int
    message: Message


# obj = Answer.model_validate(d)
#
# print(obj.message.chat)

