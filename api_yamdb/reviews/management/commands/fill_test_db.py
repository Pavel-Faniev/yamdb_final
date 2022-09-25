import csv
from sys import stdout

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ...models import Category, Comment, Genre, Review, Title

User = get_user_model()


class Command(BaseCommand):
    """
    Класс позволяет автоматически заполнить данные
    в базе на основе таблиц.
    """
    help = 'import data'

    def _load_table_data(self, file_name, model_name):
        """Функция создает записи в таблице"""

        # данный словарь нужен, чтобы функция поменяла, для каких
        # полей надо брать экземпляр класса
        mapping_field_model = {
            'category': Category,
            'author': User,
            'genre_id': Genre,
        }

        # открываем файл
        with open(file_name, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for idx, table_line in enumerate(reader):
                table_line_dict = {}
                if idx == 0:
                    # считаем, что в первой строке всегда хранятся заголовки
                    headers = table_line
                    continue
                for idx2, table_line_item in enumerate(table_line):
                    # по очереди читаем строки, делаем из них словарь
                    if headers[idx2] in mapping_field_model.keys():
                        # если поле-foreign key, то создаем экземпляр объекта
                        model_instance = mapping_field_model[
                            headers[idx2]
                        ].objects.get(pk=table_line_item)
                        table_line_dict[headers[idx2]] = model_instance
                    else:
                        table_line_dict[headers[idx2]] = table_line_item

                if table_line_dict:
                    # выводим в консоль, чтобы было видно, что грузим
                    stdout.write(str(table_line_dict))
                    stdout.write('||')
                    obj, created = model_name.objects.update_or_create(
                        **table_line_dict
                    )

    def handle(self, *args, **options):
        # основной метод команды, из которого вызываем служебную функцию
        static_folder = settings.STATICFILES_DIRS[0]
        file_path_model_mapping = {
            'data\\category.csv': Category,
            'data\\genre.csv': Genre,
            'data\\users.csv': User,
            'data\\titles.csv': Title,
            'data\\review.csv': Review,
            'data\\comments.csv': Comment,
        }

        for file_name, model_name in file_path_model_mapping.items():
            file_full_path = f'{static_folder}{file_name}'
            Command._load_table_data(file_full_path, model_name)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated from {file_name}')
            )
