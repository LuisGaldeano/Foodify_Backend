import factory.alchemy
from factory import post_generation
from factory.fuzzy import FuzzyText

from application.models import Users
from tests.test_sql_app import get_test_db_session


class UsersFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Users
        sqlalchemy_session = get_test_db_session()  # Set to None by default
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    first_name = FuzzyText(length=12)
    second_name = FuzzyText(length=12)
    username = FuzzyText(length=12)
    email = factory.LazyAttribute(
        lambda a: f"{a.first_name}.{a.second_name}@example.com".lower()
    )
    disabled = False

    @post_generation
    def password(self: Users, create, extracted, **kwargs):
        self.update_password(new_password=extracted)
        session = get_test_db_session()
        session.add(self)
        session.commit()
        session.refresh(self)
