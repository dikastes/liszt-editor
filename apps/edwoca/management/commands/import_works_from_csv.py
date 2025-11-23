from ...models.expression import IndexNumber, Expression, ExpressionTitle
from ...models.work import Work, WorkTitle
from django.core.management.base import BaseCommand, CommandError
from dmad_on_django.models import Status, Language, Person, Corporation, Place, Period
from pylobid.pylobid import GNDNotFoundError, GNDIdError
from csv import DictReader

class Command(BaseCommand):
    help = "Sepcify a file to import works from."

    def add_arguments(self, parser):
        parser.add_argument(
                'file_name',
                nargs=1,
                type=str,
                help='Path to a file containing CSV encoded manifestation data.'
            )

    def handle(self, *args, **options):
        with open(options['file_name'][0]) as file:
            reader = list(DictReader(file))
            total = len(reader)
            for i, row in enumerate(reader):
                index_number = row['Raabe']
                if index_number:
                    print(f'{str(i+1)} von {total}')
                    print(f'Raabe {row["Raabe"]}')

                    if index_number != '-':
                        existing_index_number = IndexNumber.objects.filter(number = index_number).first()
                        if existing_index_number:
                            work = existing_index_number.expression.work
                            work_title = work.titles.filter(status = Status.TEMPORARY).first()
                            work_title.title += ' | ' + row['Werktitel (MGG)']
                            work_title.save()
                        else:
                            work = Work.objects.create()
                            WorkTitle.objects.create(
                                    title = row['Werktitel (MGG)'],
                                    work = work,
                                    status = Status.TEMPORARY
                                )

                        expression = Expression.objects.create(work = work)
                        IndexNumber.objects.create(
                                index = IndexNumber.Indexes.RAABE,
                                number = index_number,
                                expression = expression
                            )
                        if row['Searle'] != '-':
                            IndexNumber.objects.create(
                                    index = IndexNumber.Indexes.SEARLE,
                                    number = row['Searle'],
                                    expression = expression
                                )
                        if row['Eckhardt-Müller'] != '-':
                            IndexNumber.objects.create(
                                    index = IndexNumber.Indexes.MULLER,
                                    number = row['Eckhardt-Müller'],
                                    expression = expression
                                )
                        ExpressionTitle.objects.create(
                                title = row['Werktitel (MGG)'],
                                expression = expression,
                                status = Status.TEMPORARY
                            )
                    else:
                        work = Work.objects.create()
                        WorkTitle.objects.create(
                                title = row['Werktitel (MGG)'],
                                work = work,
                                status = Status.TEMPORARY
                            )

                        expression = Expression.objects.create(work = work)
                        if row['Searle'] != '-':
                            IndexNumber.objects.create(
                                    index = IndexNumber.Indexes.SEARLE,
                                    number = row['Searle'],
                                    expression = expression
                                )
                        if row['Eckhardt-Müller'] != '-':
                            IndexNumber.objects.create(
                                    index = IndexNumber.Indexes.MULLER,
                                    number = row['Eckhardt-Müller'],
                                    expression = expression
                                )
                        ExpressionTitle.objects.create(
                                title = row['Werktitel (MGG)'],
                                expression = expression,
                                status = Status.TEMPORARY
                            )
