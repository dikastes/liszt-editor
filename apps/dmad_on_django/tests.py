from django.test import TestCase
from django.urls import reverse
from .models import Person

# Create your tests here.

# synchronization starts 3 trialon GNDAPIError

# person sync creates valid primary name

# deleting a person deletes all names


class LinkGNDTest(TestCase):

    def test_gnd_link_workflow(self):
        p = Person.objects.create()

        url = reverse('dmad_on_django:person_link', kwargs={'pk': p.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
