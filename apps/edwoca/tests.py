from django.test import TestCase
from dmad_on_django.models import Status, Language, Person, Place
from .models import Title, Contributor, Work
from xml.etree import ElementTree as ET

# Create your tests here.

class TitleModelTests(TestCase):
    title = 'example title'
    language = Language['DE']
    status = Status.PRIMARY
    expected = '<title lang="de">%s</title>' % title

    def test_title_yields_correct_mei(self):
        future_title = Title(
            title=self.title,
            language=self.language,
            status=self.status
        )

        self.assertEquals(
            ET.tostring(future_title.to_mei()),
            self.expected.encode(encoding='utf-8')
        )

    def test_alternative_title_is_rendered_correctly_in_mei(self):
        status = Status.ALTERNATIVE
        future_title = Title(
            title=self.title,
            language=self.language,
            status=status
        )
        expected = '<title type="alternative" lang="de">%s</title>' % self.title

        self.assertEquals(
            ET.tostring(future_title.to_mei()),
            expected.encode(encoding='utf-8')
        )

class ContributorModelTests(TestCase):
    name = 'example name'
    gnd_id = '125Y'
    work_catalog_number = 'A3'
    role = Contributor.Role.COMPOSER
    expected = '<persName role="%s" auth="GND" auth.uri="d-nb.info/gnd" codedval="%s">%s</persName>' % \
        (role, gnd_id, name)

    def test_contributor_yields_correct_mei(self):
        future_person = Person(name=self.name, gnd_id=self.gnd_id)
        future_work = Work(id=1, gnd_id=self.gnd_id, work_catalog_number=self.work_catalog_number)
        future_work.save()
        future_work.titles.create(
            title=TitleModelTests.title,
            language=TitleModelTests.language,
            status=TitleModelTests.status
                )
        future_contributor = Contributor(person=future_person, work=future_work, role=self.role)

        self.assertEquals(
            ET.tostring(future_contributor.to_mei()),
            self.expected.encode(encoding='utf-8')
        )

class WorkModelTests(TestCase):
    gnd_id = '123X'
    work_catalog_number = 'A3'
    history = 'example history'

    def test_work_yields_correct_mei(self):
        future_work = Work(
            id = 1,
            gnd_id = self.gnd_id,
            work_catalog_number = self.work_catalog_number,
            history = self.history
        )
        future_work.save()

        future_work.titles.create(
            title=TitleModelTests.title,
            language=TitleModelTests.language,
            status=TitleModelTests.status
        )

        expected = '<work>%s<identifier label="GND">%s</identifier><identifier label="LQWV">%s</identifier><history>%s</history></work>' % \
            (
                TitleModelTests.expected,
                self.gnd_id,
                self.work_catalog_number,
                self.history
            )

        self.assertEquals(
            ET.tostring(future_work.to_mei()),
            expected.encode(encoding='utf-8')
        )

