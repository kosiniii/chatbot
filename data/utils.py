import logging
import time
from .redis_instance import __redis_room__, __redis_users__, room, redis_random_waiting, random_users
from utils.time import dateMSC

# rooms = {chat_id: {users: {user_id: {status_online: str, activity: bool, connected: datetime}}, created: datetime}}
# random_waiting = {num_meet: {users: {user_id: {ready: bool = False}}}, created: datetime}
# random_users = {user_id: {skip_users: [int], tolk_users: [int],"added_time": время_добавления, "message_id": id_сообщения_или_null, data_activity: datetime}}

logger = logging.getLogger(__name__)

class CreatingJson:
    def __init__(self) -> None:
        pass

    def rooms(self, invite_link: str, chat_id: int, users: list = None):
            data = {
                chat_id: {
                    'users': {
                        user_id: {
                            'status_online': 'Undefind',
                            'activity': None,
                            'connected': None,
                            'last_message': None,
                        } for user_id in users
                    },
                    'created': dateMSC,
                    'invite_link': invite_link
                }
            }
            room.redis_cashed(data=data, ex=None)
            return data
    
    def random_waiting(self, users: dict[int, dict[str, int]], num_meet: int = 1):
            users_dict = users.get('users', {})
            size_users = len(users_dict)
            if size_users != 2:
                logger.error(f'[Ошибка] юзеров != 2 человека: {size_users}\n Словарь: {users}')
                return False

            data = {
                num_meet: {
                      'users': {
                            user_id: {
                                'ready': False,
                            } for user_id in users_dict
                        },
                    'created': dateMSC
                    }
                }
            redis_random_waiting.redis_cashed(data=data, ex=None)
            return data
        
    def random_data_user(self, users: list, value: dict | None = None, main_data: dict | None = None) -> dict:
        if not main_data:
            main_data: dict = random_users.redis_data()
        value = value if value is not None else {}
        
        for user_id in users:
            user_id_str = str(user_id)
            
            user_data = main_data.get(user_id_str, {})

            skip_users = value.get("skip_users", user_data.get("skip_users", []))
            tolk_users = value.get('tolk_users', user_data.get('tolk_users', []))
            message_id = value.get('message_id', user_data.get('message_id', None))
            added_time = value.get('added_time', user_data.get('added_time', time.time() if user_id_str not in main_data else user_data.get('added_time')))
            last_activity = value.get('last_activity', user_data.get('last_activity', dateMSC)) # Обновляем last_activity всегда при обработке
            continue_id = value.get('continue_id', user_data.get('continue_id', None))

            main_data[user_id_str] = {
                # exceptions
                "skip_users": skip_users,
                "tolk_users": tolk_users,
                # messages
                'message_id': message_id,
                'continue_id': continue_id,
                # time
                'added_time': added_time,
                'last_activity': last_activity
            }

        random_users.redis_cashed(main_data, ex=None) # Сохраняем измененные данные
        return main_data
        
