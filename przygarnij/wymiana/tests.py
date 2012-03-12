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

    def test_adv_edit(self):
        resp = self.client.get(reverse('adv_edit', args=[1]))
        self.assertEqual(resp.status_code, 302)

        self.login()
        resp = self.client.get(reverse('adv_edit', args=[1]))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('adv_edit', args=[100]))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(reverse('adv_edit', args=[1]),
                {'title': 'zmiana', 'what': ''})
        self.assertEqual(resp.context['form']['what'].errors,
                ['This field is required.'])

        adv = Advert.objects.all().count()
        resp = self.client.post(reverse('adv_edit', args=[1]),
                {'title': 'zmiana', 'what': 'kaktus'})
        self.assertRedirects(resp, reverse('adv', args=[1]), status_code=302,
                target_status_code=200)
        self.assertEqual(Advert.objects.get(pk=1).title, 'zmiana')
        self.assertEqual(adv, Advert.objects.all().count())

    def test_adv_list(self):
        resp = self.client.get(reverse('adv_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([adv.pk for adv in resp.context['adv_list']], [3, 2, 1])

        resp = self.client.get(reverse('adv_list'), {'what': 'a', 'where': 'all'})
        self.assertEqual(resp.context['form']['what'].errors,
                ['Ensure this value has at least 3 characters (it has 1).'])

        resp = self.client.get(reverse('adv_list'),
                {'what': 'aaaaa', 'where': 'all'})
        self.assertContains(resp, 'Brak ogłoszeń spełniających zadane kryteria.')

        resp = self.client.get(reverse('adv_list'), {'page': 'asd'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([adv.pk for adv in resp.context['adv_list']], [3, 2, 1])

    def test_about(self):
        resp = self.client.get(reverse('about'))
        self.assertEqual(resp.status_code, 200)

