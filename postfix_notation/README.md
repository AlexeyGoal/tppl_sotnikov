# Стековая машина

Программа для вычисления выражений в обратной польской нотации (постфиксной нотации).

## Запуск

```bash
python main.py "2 3 +"
```


### Пример

```bash
python main.py "3 0 4 ~ 2 ~"
```
Вывод:
```text 
step 1: [3.0]
step 2: [3.0, 0.0]
step 3: [3.0, 0.0, 4.0]
step 4: [49.0]
step 5: [49.0, 2.0]
step 6: [47.0]
3 0 4 ~ 2 ~ = 47.0
```


## Тестирование

```bash
pytest test_postfix.py
```

### Запуск с проверкой покрытия
```bash
pytest --cov=main test_postfix.py 
```

## Требования

- Python 3.6+
- pytest (для запуска тестов)
- pytest-cov (для проверки покрытия)

## Установка зависимостей

```bash
pip install pytest pytest-cov
```
