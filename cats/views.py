from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import ScopedRateThrottle


from .models import Achievement, Cat, User
from .pagination import CatsPagination, CustomPagination
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .throttling import WorkingHoursRateThrottle


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Анонимным GET-запросом можно получить информацию о котиках.
    # Все остальное закрыто.
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # Кастомный класс permisions:
    permission_classes = (OwnerOrReadOnly,)
    # Подключили класс AnonRateThrottle
    # throttle_classes = (AnonRateThrottle,)
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    throttle_scope = 'low_request'
    # Игнорируем pagination указанную в settings.
    # pagination_class = None  # или ставим PageNumberPagination
    # pagination_class = LimitOffsetPagination
    # Или кастомный пагинатор
    pagination_class = CatsPagination

    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    # Добавим в кортеж ещё один бэкенд
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    # Временно отключим пагинацию на уровне вьюсета,
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    # http://127.0.0.1:8000/cats/?color=Black
    filterset_fields = ('color', 'birth_year')
    search_fields = ('name',)
    # Поиск можно проводить и по содержимому полей связанных моделей.
    # Доступные для поиска поля связанной модели указываются через нотацию
    # с двойным подчёркиванием: ForeignKey текущей модели__имя поля
    # в связанной модели.
    # http://127.0.0.1:8000/cats/?search=Бар
    # search_fields = ('achievements__name', 'owner__username')
    # Сортировка выдачи: бэкенд OrderingFilter /cats/?ordering=name
    ordering_fields = ('name', 'birth_year')
    # Сортировка по умолчанию.
    ordering = ('birth_year',)

    def get_permissions(self):

        '''Теперь при GET-запросе информации о конкретном котике доступ
        будет определяться пермишеном ReadOnly: запросы будут разрешены всем.
        При остальных запросах доступ будет определять
        пермишен OwnerOrReadOnly.'''

        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов.
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
