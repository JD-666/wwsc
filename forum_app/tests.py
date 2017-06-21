from django.test import TestCase
from django.core.urlresolvers import reverse

from forum_app.models import Category, Thread, Post, Profile

from datetime import datetime


class CategoryMethodtests(TestCase):
    def test_ensure_num_childs_are_positive(self):
        """
        results True for categories where num_threads and num_posts are zero
        or positive. 
        """
        cat = Category(name='test', num_threads=-1, num_posts=-1)
        cat.save()
        self.assertEqual((cat.num_threads >= 0),True)
        self.assertEqual((cat.num_posts >= 0),True)

    def test_slug_creation(self):
        """
        Checks to make sure that when a category is created, an appropriate
        slug line is also created. i.e.
        'Rangom Cat Slug' --> 'random-cat-slug'
        """
        cat = Category(name='Random Category String 9000')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string-9000')

    def test_ensure_most_recent_post_not_initialized(self):
    
        """
        Checks to ensure that when a category is created, if a most_recent_post
        field is supplied with a dattime object that it gets appropriately
        ignore. This is because only Post submissions should update this field.
        """
        cat = Category(name='test', most_recent_post=datetime.now())
        cat.save()
        self.assertEqual((cat.most_recent_post == None), True)

class HomeViewTests(TestCase):
    def test_category_list_view_with_no_categoryies(self):
        """
        If no Categories exist, an appropriate message should be displayed. 
        Djando tests.py initializes it's own new DB called 'default'. This
        means that when tests.py runs, there is a new DB with no content and
        no Categories to start.
        """
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['categories'], [])
        self.assertContains(response, "There are no categories to display.")

    def test_category_list_view_with_existing_categories(self):
        """
        Checks to see that if a category exists, then category_list View
        appropriately generates a template with that view in it. 
        """
        cat = Category(name='test cat')
        cat.save()
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 1)
        self.assertContains(response, "test cat")
        