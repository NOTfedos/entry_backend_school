# Вступительное задание в осеннюю школу бекенд-разработки Яндека

## Установка docker:


## Сборка
```
docker-compose build
```

## Запуск
```
docker-compose up -d
```

## Инициализация/сброс БД
Зайдите в bash контейнера приложения
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

Также доступен сервис pgAdmin на порте 5050.
