# Вступительное задание в осеннюю школу бекенд-разработки Яндека


## Сборка
```
docker-compose build
```

## Запуск
```
docker-compose up -d
```

## Инициализация/сброс БД
При запущенном docker-compose зайдите в bash контейнера приложения
```
docker exec -it itemapp_container bash
```
Выполните команду
```
python3 init_database.py
```

## Тестирование
При запущенном docker-compose выполните:
```
cd ./src/tests
python unit_test.py
```

## Прочие сервисы
Само API транслируется на порт 80.

Документацию можно посмотреть по адресам:
- OpenAPI: `/docs`
- ReDoc: `/redoc`

Также доступен сервис pgAdmin на порте 5050.
