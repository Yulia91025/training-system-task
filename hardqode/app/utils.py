from .models import Product, Lesson, Group
from django.contrib.auth.models import User
from django.utils import timezone


class GroupDistributionUtil:

    def __init__(self, product: Product) -> None:
        self.product = product

    def manage(self, user: User) -> Group:
        users = self.all_product_users()
        if user in users:
            return None
        groups = self.get_groups()
        self.groups_count = len(groups.all())
        if not groups:
            new_group = self.create_new_group()
            new_group.users.add(user)
            return new_group

        self.min_len = self.product.min_group_students
        self.max_len = self.product.max_group_students
        self.total_len = len(users)
        avg_len = self.total_len / self.groups_count

        if avg_len > self.min_len:
            if avg_len == self.max_len:
                new_group = self.create_new_group()
            start_datetime = self.product.start_datetime
            now = timezone.now()
            if now < start_datetime:
                self.groups = self.get_groups()
                groups_curr_lens = {
                    group: len(group.users.all()) for group in self.groups
                }
                groups_lens = self.get_groups_counts()
                groups_diff_lens = {
                    self.groups[i]: (groups_lens[i] - groups_curr_lens[self.groups[i]])
                    for i in range(len(self.groups))
                }
                groups_overfield = {}
                groups_underfield = {}
                for group in self.groups:
                    diff = groups_diff_lens[group]
                    if diff > 0:
                        groups_underfield[group] = diff
                    elif diff < 0:
                        groups_overfield[group] = -diff

                move_paths = []
                under_groups = list(groups_underfield.keys())
                i = 0
                for over_group in groups_overfield.keys():
                    over_count = groups_overfield[over_group]
                    while over_count:
                        under_group = under_groups[i]
                        under_count = groups_underfield[under_group]
                        if under_count <= over_count:
                            move_count = under_count
                            groups_underfield.pop(under_group)
                            i += 1
                        else:
                            move_count = over_count
                        over_count -= move_count
                        groups_overfield[over_group] = over_count
                        under_count -= move_count
                        groups_underfield[under_group] = under_count
                        move_paths.append([over_group, under_group, move_count])

                for move_path in move_paths:
                    self.move_users(move_path[0], move_path[1], move_path[2])

        group = self.add_student(user)
        return group

    def get_groups_counts(self) -> list[int]:
        groups = self.get_groups()
        groups_lens = [0 for _ in range(len(groups))]
        i = 0
        j = 0
        while i <= self.total_len:
            if groups_lens[j] < self.min_len:
                groups_lens[j] += 1
                i += 1
                if groups_lens[j] == self.min_len:
                    j = (j + 1) % len(groups)
            else:
                groups_lens[j] += 1
                i += 1
                j = (j + 1) % len(groups)
        return groups_lens

    def get_groups(self) -> list[Group]:
        return Group.objects.filter(product=self.product)

    def all_product_users(self) -> list[User]:
        users = []
        groups = self.get_groups()
        for group in groups:
            for user in group.users.all():
                users.append(user)
        return users

    def create_new_group(self) -> Group:
        name = self.product.title + str(self.groups_count)
        new_group = Group.objects.create(product=self.product, name=name)
        return new_group

    def min_group_length_now(self, start_indx: int = 0) -> int:
        groups = self.get_groups()
        self.groups_lengths = {
            group: len(group.users.all()) for group in groups[start_indx:]
        }
        return min(self.groups_lengths.values())

    def move_users(self, group: Group, new_group: Group, num_to_move: int) -> None:
        users = group.users.all()
        users_to_move = users[:num_to_move]
        for user in users_to_move:
            new_group.users.add(user)
            group.users.remove(user)

    def add_student(self, user: User) -> Group:
        groups = self.get_groups()
        min_length_now = self.min_group_length_now()
        groups_first_min = None
        i = 0
        while not groups_first_min:
            group = groups[i]
            if self.groups_lengths[group] == min_length_now:
                groups_first_min = group
            i += 1
        groups_first_min.users.add(user)
        return groups_first_min
