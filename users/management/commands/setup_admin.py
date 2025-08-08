from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Setup admin user with password and role'

    def handle(self, *args, **options):
        try:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin123')
            admin_user.role = 'admin'
            admin_user.is_active = True
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Successfully updated admin user with password "admin123" and role "admin"')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Admin user does not exist')
            )