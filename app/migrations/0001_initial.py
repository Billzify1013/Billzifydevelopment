# Generated by Django 4.1.3 on 2024-06-17 09:02

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField()),
                ('date_of_joining', models.DateField()),
                ('employee_contact', models.BigIntegerField(validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('position', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('salarybyday', models.IntegerField(default=0)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Gueststay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guestname', models.CharField(default=None, max_length=150)),
                ('guestphome', models.BigIntegerField(validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('guestemail', models.EmailField(default=None, max_length=254)),
                ('guestcity', models.CharField(default=None, max_length=50)),
                ('guestcountry', models.CharField(default=None, max_length=50)),
                ('guestidimg', models.ImageField(blank=True, null=True, upload_to='Guestid')),
                ('checkindate', models.DateField()),
                ('checkoutdate', models.DateField()),
                ('noofguest', models.BigIntegerField(default=0)),
                ('adults', models.BigIntegerField(default=0)),
                ('children', models.BigIntegerField(default=0)),
                ('purposeofvisit', models.CharField(default=None, max_length=150)),
                ('roomno', models.IntegerField(default=0)),
                ('subtotal', models.BigIntegerField(default=0)),
                ('discount', models.BigIntegerField(default=0)),
                ('total', models.BigIntegerField(default=0)),
                ('tax', models.CharField(max_length=10)),
                ('checkoutstatus', models.BooleanField(default=False)),
                ('checkoutdone', models.BooleanField(default=False)),
                ('noofrooms', models.IntegerField(default=1)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_gst_number', models.CharField(blank=True, max_length=15)),
                ('invoice_number', models.CharField(blank=True, max_length=20)),
                ('invoice_date', models.DateField(blank=True)),
                ('total_item_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('subtotal_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('gst_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('sgst_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('grand_total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('modeofpayment', models.CharField(blank=True, max_length=20)),
                ('room_no', models.CharField(blank=True, max_length=40)),
                ('foliostatus', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.gueststay')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='onlinechannls',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channalname', models.CharField(max_length=100)),
                ('channal_img', models.ImageField(default=None, upload_to='channal images')),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='websitelinks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logoname', models.CharField(max_length=40)),
                ('googlelink', models.URLField(null=True)),
                ('websitelink', models.URLField(null=True)),
                ('laundryurl', models.URLField(null=True)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='webreview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('years', models.CharField(max_length=10)),
                ('clientscount', models.CharField(max_length=20)),
                ('reviewscount', models.CharField(max_length=20)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='webgallary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gallary_img', models.ImageField(blank=True, null=True, upload_to='gallaryimg')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Taxes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taxname', models.CharField(max_length=100)),
                ('taxcode', models.IntegerField(default=0)),
                ('taxrate', models.IntegerField(default=0)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.subscriptionplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SaveAdvanceBookGuestData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookingdate', models.DateField()),
                ('noofrooms', models.IntegerField(default=0)),
                ('bookingguest', models.CharField(max_length=100)),
                ('bookingguestphone', models.BigIntegerField(validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('advance_amount', models.BigIntegerField(default=0)),
                ('reamaining_amount', models.BigIntegerField(default=0)),
                ('total_amount', models.BigIntegerField(default=0)),
                ('discount', models.BigIntegerField(default=0)),
                ('checkoutdate', models.DateField()),
                ('staydays', models.IntegerField(default=0)),
                ('checkinstatus', models.BooleanField(default=False)),
                ('channal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.onlinechannls')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SalaryManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary_date', models.DateField()),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('salary_days', models.DecimalField(decimal_places=2, max_digits=10)),
                ('basic_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bonus', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('deductions', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.employee')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoomsCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=150)),
                ('Hsn_sac', models.IntegerField(default=0)),
                ('roomimg', models.ImageField(blank=True, null=True, upload_to='roomimg')),
                ('catprice', models.IntegerField(default=1)),
                ('category_tax', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.taxes')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rooms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.IntegerField(default=0)),
                ('checkin', models.IntegerField(default=0)),
                ('price', models.IntegerField(default=1)),
                ('tax_amount', models.BigIntegerField(default=0)),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.roomscategory')),
                ('tax', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.taxes')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoomCleaning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_date', models.DateField(null=True)),
                ('status', models.BooleanField(default=False)),
                ('rooms', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.rooms')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoomBookAdvance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookingdate', models.DateField()),
                ('bookingguest', models.CharField(max_length=100)),
                ('bookingguestphone', models.BigIntegerField(validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('checkoutdate', models.DateField()),
                ('checkinstatus', models.BooleanField(default=False)),
                ('partly_checkin', models.BooleanField(default=False)),
                ('bookingstatus', models.BooleanField(default=False)),
                ('channal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.onlinechannls')),
                ('roomno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.rooms')),
                ('saveguestdata', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.saveadvancebookguestdata')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='offerwebsitevendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15)),
                ('amount', models.CharField(max_length=15)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.roomscategory')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MoreGuestData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('another_guest_name', models.CharField(default=None, max_length=100)),
                ('another_guest_phone', models.BigIntegerField(default=None, validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('another_guest_address', models.CharField(default=None, max_length=150)),
                ('mainguest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.gueststay')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Messgesinfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('defaultlimit', models.IntegerField(default=0)),
                ('changedlimit', models.IntegerField(default=0)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='loylty_Guests_Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.CharField(default=None, max_length=100)),
                ('guest_contact', models.BigIntegerField(validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('loylty_point', models.IntegerField(default=0)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='loylty_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loylty_rate_prsantage', models.BigIntegerField(default=0)),
                ('Is_active', models.BooleanField(default=False)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LaundryServices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('sercategory', models.CharField(choices=[('laundry', 'laundry'), ('drycleaning', 'drycleaning')], max_length=255)),
                ('gencategory', models.CharField(choices=[('mens', 'mens'), ('womens', 'womens')], max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
                ('hsncode', models.CharField(max_length=10, null=True)),
                ('price', models.IntegerField()),
                ('category_tax', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.taxes')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('hsncode', models.IntegerField(blank=True, default=0)),
                ('quantity_likedays', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cgst_rate', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)])),
                ('sgst_rate', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)])),
                ('paidstatus', models.BooleanField(default=False)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.invoice')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HotelProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(default=None, max_length=254)),
                ('contact', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('zipcode', models.CharField(max_length=8)),
                ('gstin', models.CharField(max_length=25)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profileimage')),
                ('counrty', models.CharField(max_length=35)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eventname', models.CharField(max_length=100)),
                ('eventprice', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('termscondition', models.TextField()),
                ('Hsn_sac', models.IntegerField(default=0)),
                ('eventax', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.taxes')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventBookGuest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customername', models.CharField(max_length=50)),
                ('guestemail', models.EmailField(default=None, max_length=254)),
                ('customer_contact', models.BigIntegerField(validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('customeraddress', models.CharField(max_length=150)),
                ('customergst', models.CharField(max_length=18)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('taxamount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('advanceamount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reamainingamount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('status', models.BooleanField(default=False)),
                ('invoice_date', models.DateField(null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.events')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DailyManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('check_in_time', models.TimeField(null=True)),
                ('check_out_time', models.TimeField(null=True)),
                ('halfday', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.employee')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=15)),
                ('groups', models.ManyToManyField(related_name='custom_users', to='auth.group')),
                ('user_permissions', models.ManyToManyField(related_name='custom_users', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='amainities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=60)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='reviewQr',
            fields=[
                ('room_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='app.rooms')),
                ('qrimage', models.ImageField(default=None, upload_to='Qr images')),
                ('foodurl', models.URLField(null=True)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
