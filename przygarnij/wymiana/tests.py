#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from wymiana.models import *


class ViewTest(TestCase):
    fixtures = ['testing.json']

    def login(self, user='franek', password='asdasd'):
        resp = self.client.post(reverse('login'),
                {'username': user, 'password': password}, follow=True)
        self.assertRedirects(resp, reverse('profile'), status_code=302,
                target_status_code=200)

    def test_index(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([adv.pk for adv in resp.context['lista']], [3, 2, 1])

    def test_adv(self):
        resp = self.client.get(reverse('adv', args=[3]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['adv'], Advert.objects.get(pk=3))

        resp = self.client.get(reverse('adv', args=[99]))
        self.assertEqual(resp.status_code, 404)

    def test_adv_add(self):
        resp = self.client.get(reverse('adv_add'))
        self.assertEqual(resp.status_code, 302)

        self.login()
        resp = self.client.get(reverse('adv_add'))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse('adv_add'), {})
        self.assertEqual(resp.context['form'].errors['title'],
                ['This field is required.'])
        self.assertEqual(resp.context['form'].errors['what'],
                ['This field is required.'])

        adv_count = Advert.objects.all().count()
        resp = self.client.post(reverse('adv_add'), {
                'title': 'kaktus', 'what': 'wielki kaktus'
            })
        self.assertRedirects(resp, reverse('index'), status_code=302,
                target_status_code=200)
        self.assertEqual(Advert.objects.all().count(), adv_count + 1)

        adv = Advert.objects.all().latest('pk')
        self.assertEqual(adv.user, User.objects.get(username='franek'))
        self.assertEqual(adv.enable, True)

    def test_about(self):
        resp = self.client.get(reverse('about'))
        self.assertEqual(resp.status_code, 200)

