from beanie.odm.operators.update.general import Set

from app.database import User


class UserRepository:

    @staticmethod
    async def update_password(user_id, new_password):
        await User.find_one(
            User.id == user_id
        ).update(
            Set(
                {
                    User.password: new_password
                }
            )
        )
