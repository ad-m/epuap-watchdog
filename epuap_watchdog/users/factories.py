import factory
from django.conf import settings


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user%d' % n)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', 'pass')

    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ('username',)
