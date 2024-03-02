from django.test import TestCase
from .models import Product, Lesson, Group
from django.contrib.auth.models import User
from datetime import datetime
import pytz
from .utils import GroupDistributionUtil


class BuyProductTestCase(TestCase):
    def setUp(self):
        users_count = 100
        self.users = []
        for i in range(users_count):
            user = User.objects.create(username=f"user{i}", password="12345")
            self.users.append(user)

    def test_group_distribution_util(self):
        num_products = 20
        for j in range(1, num_products):
            product = Product.objects.create(
                title="Mytitle",
                cost=1000.0,
                start_datetime=datetime(2024, 10, 10, 10, 10, tzinfo=pytz.UTC),
                min_group_students=j,
                max_group_students=j + 5,
                author=self.users[0],
            )
            for i in range(len(self.users)):
                user = self.users[i]
                name = f"user{i}"
                self.assertTrue(user.username == name)
                group_distr = GroupDistributionUtil(product)
                group = group_distr.manage(user)
                all_groups = Group.objects.filter(product=product)
                groups_len = {
                    group.name: len(group.users.all()) for group in all_groups
                }
                max_value = max(groups_len.values())
                min_value = min(groups_len.values())
                self.assertTrue(
                    max_value - min_value <= 1
                    or product.min_group_students > (max_value + min_value) // 2
                )
