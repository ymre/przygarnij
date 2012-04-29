#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wymiana.models import *

from milkman.dairy import milkman

import os

TESTS_DIR = os.path.dirname(__file__)


class ViewTest(TestCase):
    fixtures = ['testing.json']

    def check_login_required(self, url):
        resp = self.client.get(url)
        self.assertRedirects(
                resp,
                reverse('login') + '?next={0}'.format(url),
                status_code=302,
                target_status_code=200
            )
        self.login()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def login(self, user='franek', password='asdasd'):
        self.client.login(username=user, password=password)

    def test_index(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([adv.pk for adv in resp.context['lista']], [3, 2, 1])

    def test_adv(self):
        adv = Advert.objects.get(pk=3)
        resp = self.client.get(reverse('adv', args=[3]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['adv'], adv)
        self.assertEqual(adv.count + 1, Advert.objects.get(pk=3).count)

        resp = self.client.get(reverse('adv', args=[0]))
        self.assertEqual(resp.status_code, 404)

    def test_adv_add_basic(self):
        self.check_login_required(reverse('adv_add'))

    def test_adv_add_empty_form(self):
        self.login()
        data = {
            'form-TOTAL_FORMS': '5',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '5'
        }
        resp = self.client.post(reverse('adv_add'), data)
        self.assertEqual(resp.context['form'].errors['title'],
                ['This field is required.'])
        self.assertEqual(resp.context['form'].errors['what'],
                ['This field is required.'])

    def test_adv_add_good_without_photo(self):
        self.login()
        data = {
            'form-TOTAL_FORMS': '5',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '5',
            'title': 'kaktus',
            'what': 'wielki kaktus'
        }
        adv_count = Advert.objects.all().count()
        resp = self.client.post(reverse('adv_add'), data)
        adv = Advert.objects.all().latest('pk')
        self.assertRedirects(resp, reverse('adv', args=[adv.pk]),
                status_code=302, target_status_code=200)
        self.assertEqual(Advert.objects.all().count(), adv_count + 1)

        self.assertEqual(adv.user, User.objects.get(username='franek'))
        self.assertEqual(adv.enable, True)

    def test_add_photo(self):
        self.login()

        img = open(os.path.join(TESTS_DIR, 'test_files/very_small.jpg'), 'rb')

        data = {
            'form-TOTAL_FORMS': '5',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '5',
            'title': 'kaktus',
            'what': 'wielki kaktus',
            'form-1-image': img,
        }

        photo_count = Photo.objects.all().count()
        adv_count = Advert.objects.all().count()

        resp = self.client.post(reverse('adv_add'), data)
        adv = Advert.objects.all().latest('pk')
        self.assertRedirects(resp, reverse('adv', args=[adv.pk]),
                status_code=302, target_status_code=200)

        self.assertEqual(Advert.objects.all().count(), adv_count + 1)
        self.assertEqual(photo_count + 1, Photo.objects.all().count())

        photo = Photo.objects.all().latest('pk')
        self.assertEqual(photo.image.name, '%s.jpg' % photo.pk)
        self.assertEqual(photo.adv, adv)

        img.close()

    def test_adv_edit_basic(self):
        self.check_login_required(reverse('adv_edit', args=[1]))

        resp = self.client.get(reverse('adv_edit', args=[0]))
        self.assertEqual(resp.status_code, 404)

    def test_adv_edit_empty(self):
        self.login()

        data = {
            'form-TOTAL_FORMS': '5',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '5',
            'title': 'zmiana',
            'what': '',
        }

        resp = self.client.post(reverse('adv_edit', args=[1]), data)
        self.assertEqual(resp.context['form']['what'].errors,
                ['This field is required.'])

    def test_adv_edit(self):
        self.login()

        data = {
            'form-TOTAL_FORMS': '5',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '5',
            'title': 'zmiana',
            'what': 'kaktus',
            'form-0-id': 1,
        }

        adv = Advert.objects.all().count()
        photo = Photo.objects.all().count()

        resp = self.client.post(reverse('adv_edit', args=[1]), data)
        self.assertRedirects(resp, reverse('adv', args=[1]), status_code=302,
                target_status_code=200)
        self.assertEqual(Advert.objects.get(pk=1).title, 'zmiana')

        self.assertEqual(adv, Advert.objects.all().count())
        self.assertEqual(photo, Photo.objects.all().count())

    def test_adv_delete_photo(self):
        self.login()

        data = {
            'form-TOTAL_FORMS': '5',
            'form-INITIAL_FORMS': '2',
            'form-MAX_NUM_FORMS': '5',
            'title': 'zmiana',
            'what': 'kaktus',
            'form-0-id': 2,
            'form-0-DELETE': 'on',
            'form-1-id': 3,
        }
        photo = Photo.objects.all().count()

        resp = self.client.post(reverse('adv_edit', args=[2]), data)
        self.assertRedirects(resp, reverse('adv', args=[2]), status_code=302,
                target_status_code=200)

        self.assertEqual(photo - 1, Photo.objects.all().count())

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

    def test_adv_ans_basic(self):
        resp = self.client.get(reverse('adv_ans', args=[1]))
        self.assertContains(resp, 'Captcha')

        resp = self.client.get(reverse('adv_ans', args=[0]))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(reverse('adv_ans', args=[1]), {})
        fields = ['message', 'email', 'captcha']
        for f in fields:
            self.assertEqual(resp.context['form'][f].errors,
                    ['This field is required.'])

        self.login()

        resp = self.client.get(reverse('adv_ans', args=[1]))
        self.assertNotContains(resp, 'Captcha')

        resp = self.client.post(reverse('adv_ans', args=[1]), {})
        self.assertEqual(resp.context['form']['message'].errors,
                ['This field is required.'])

    def answer_mail(self, ans, outbox, mes):
        self.assertEqual(len(outbox), 1)
        self.assertTrue(mes in outbox[0].body)
        self.assertEqual([ans.adv.user.email], outbox[0].to)
        self.assertEqual(u'Odpowiedź na ogłoszenie: {0}'.format(ans.adv.title),
                outbox[0].subject)
        self.assertEqual('przygarnijkwiatka@gmail.com', outbox[0].from_email)
        self.assertEqual(ans.email, outbox[0].extra_headers['Reply-To'])

    def test_adv_ans(self):
        self.login(user='zosia', password='asdasd')
        mes = 'bla bla bla'

        mail.outbox = []
        resp = self.client.post(reverse('adv_ans', args=[1]),
                {'message': mes})
        self.assertRedirects(resp, reverse('index'), status_code=302,
                target_status_code=200)
        ans = Answer.objects.all().latest('pk')

        self.answer_mail(ans=ans, outbox=mail.outbox, mes=mes)

    def test_adv_ans_anon(self):
        from captcha.models import CaptchaStore

        captcha_count = CaptchaStore.objects.count()
        self.failUnlessEqual(captcha_count, 0)

        resp = self.client.get(reverse('adv_ans', args=[1]))

        captcha_count = CaptchaStore.objects.count()
        self.failUnlessEqual(captcha_count, 1)

        captcha = CaptchaStore.objects.all()[0]

        mes = 'bla bla bla'
        resp = self.client.post(reverse('adv_ans', args=[1]),
                {
                    'message': mes,
                    'email': 'test@test.pl',
                    'captcha_0': captcha.hashkey,
                    'captcha_1': captcha.response
                })
        self.assertRedirects(resp, reverse('index'), status_code=302,
                target_status_code=200)

        ans = Answer.objects.all().latest('pk')
        self.answer_mail(ans=ans, outbox=mail.outbox, mes=mes)

    def test_adv_delete_basic(self):
        self.check_login_required(reverse('adv_del', args=[1]))

        self.login(user='zosia', password='asdasd')

        resp = self.client.get(reverse('adv_del', args=[0]))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(reverse('adv_del', args=[1]))
        self.assertEqual(resp.status_code, 404)

    def test_adv_delete(self):
        self.login()

        resp = self.client.get(reverse('adv_del', args=[1]))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse('adv_del', args=[1]))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(reverse('adv_del', args=[1]), {'pk': 1})
        self.assertRedirects(resp, reverse('profile'), status_code=302,
                target_status_code=200)
        self.assertFalse(Advert.objects.get(pk=1).enable)

    def test_panel(self):
        self.check_login_required(reverse('profile'))

        self.login()
        resp = self.client.get(reverse('profile'))
        self.assertEqual([a.pk for a in resp.context['lista']], [2, 1])

    def test_userinfo(self):
        self.check_login_required(reverse('info'))

        self.login()

        info_num = UserInfo.objects.all().count()
        for info in ['bla bla bla', 'inne blablanie']:
            resp = self.client.post(reverse('info'), {'info': info})
            self.assertRedirects(resp, reverse('profile'), status_code=302,
                    target_status_code=200)

            resp = self.client.get(reverse('info'))
            self.assertContains(resp, info)
        self.assertEqual(info_num + 1, UserInfo.objects.all().count())

    def test_userpage(self):
        info = UserInfo.objects.create(
                user=User.objects.get(username='franek'),
                info='bla bla bla'
            )
        info.save()

        resp = self.client.get(reverse('user', args=['nie_ma_mnie']))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(reverse('user', args=['franek']))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([a.pk for a in resp.context['lista']], [2, 1])
        self.assertEqual(resp.context['info'][0], info)

    def test_about(self):
        resp = self.client.get(reverse('about'))
        self.assertEqual(resp.status_code, 200)


class PhotoTest(TestCase):
    def setUp(self):
        self.adv = milkman.deliver(Advert)
        self.adv.save()

    def tearDown(self):
        self.adv.delete()

    def test_save(self):
        images = [
            ('very_small', [160, 200]),
            ('big', [600, 800]),
            ('too_big', [600, 428]),
            ('too_big_too', [266, 800]),
        ]
        for i in images:
            img = open(os.path.join(TESTS_DIR, 'test_files/%s.jpg' % i[0]), 'rb')

            photo = Photo.objects.create(adv=self.adv,
                    image=SimpleUploadedFile(img.name, img.read(), 'image/jpg'))
            photo.save()

            photo = Photo.objects.all().latest('pk')
            self.assertEqual(photo.image.name, '%s.jpg' % photo.pk)
            self.assertEqual([photo.image.height, photo.image.width], i[1])
            img.close()
