from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from quiz.models import Category, Question, Choice
from leaderboard.models import UserScore


class Command(BaseCommand):
    help = "Baza uchun Django bo'yicha to'liq test ma'lumotlarini yuklash"

    def handle(self, *args, **options):
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@quiz.uz", "is_staff": True, "is_superuser": True}
        )
        admin_user.set_password("admin123")
        admin_user.save()

        demo_users_data = [
            ("aziza_django", "aziza@quiz.uz", "Aziza Rahimova"),
            ("jasur_coder", "jasur@quiz.uz", "Jasur Temirov"),
            ("bekzod_python", "bekzod@quiz.uz", "Bekzod Aliyev"),
            ("nodira_dev", "nodira@quiz.uz", "Nodira Karimova"),
            ("sanjar_backend", "sanjar@quiz.uz", "Sanjar Yusupov"),
            ("umid_tech", "umid@quiz.uz", "Umid Soliyev"),
        ]

        created_users = []
        for uname, uemail, _ in demo_users_data:
            user, _ = User.objects.get_or_create(
                username=uname,
                defaults={"email": uemail}
            )
            user.set_password("pass123")
            user.save()
            created_users.append(user)

        data = [
            {
                "name": "Django Modellari va Migratsiyalar",
                "slug": "django-models-migrations",
                "icon": "layers",
                "description": "Modellar tuzilishi, maydonlar turlari (CharField, ForeignKey, ManyToManyField), Meta klassi va makemigrations/migrate buyruqlari bo'yicha savollar.",
                "questions": [
                    {
                        "text": "Django modelida matn maydonining maksimal uzunligini belgilash uchun qaysi parametr majburiy hisoblanadi?",
                        "difficulty": "easy",
                        "choices": [
                            ("max_length", True),
                            ("length", False),
                            ("size", False),
                            ("limit", False),
                        ]
                    },
                    {
                        "text": "Yangi model yoki o'zgarishlar uchun migratsiya faylini yaratuvchi boshqaruv buyrug'i qaysi?",
                        "difficulty": "easy",
                        "choices": [
                            ("python manage.py makemigrations", True),
                            ("python manage.py migrate", False),
                            ("python manage.py createmigrations", False),
                            ("python manage.py initmigrations", False),
                        ]
                    },
                    {
                        "text": "Bir modeldan boshqa modelga biriktirilgan ob'ekt o'chirilganda, bog'langan yozuvlar ham o'chib ketishi uchun on_delete ga nima beriladi?",
                        "difficulty": "easy",
                        "choices": [
                            ("models.CASCADE", True),
                            ("models.PROTECT", False),
                            ("models.SET_NULL", False),
                            ("models.DO_NOTHING", False),
                        ]
                    },
                    {
                        "text": "Django modelining ob'ektlari string ko'rinishida qanday ifodalanishini aniqlovchi maxsus Python metodi qaysi?",
                        "difficulty": "easy",
                        "choices": [
                            ("__str__(self)", True),
                            ("__repr__(self)", False),
                            ("__unicode__(self)", False),
                            ("to_string(self)", False),
                        ]
                    },
                    {
                        "text": "Bir modelda bir nechta maydonlar kombinatsiyasining takrorlanmasligini ta'minlash uchun Meta klassida qaysi parametr ishlatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("unique_together yoki UniqueConstraint", True),
                            ("index_together", False),
                            ("unique_fields", False),
                            ("combined_unique", False),
                        ]
                    },
                    {
                        "text": "Ko'pdan-ko'pga (Many-to-Many) munosabatda qo'shimcha maydonlar (masalan, sana, rol) saqlash uchun qaysi parametr orqali o'rta model (intermediate table) ko'rsatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("through", True),
                            ("intermediate", False),
                            ("bridge", False),
                            ("via", False),
                        ]
                    },
                    {
                        "text": "Django modelida avtomatik ravishda yozuv yaratilgan vaqtni faqat bir marta belgilash uchun DateTimeField da nima ishlatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("auto_now_add=True", True),
                            ("auto_now=True", False),
                            ("default_time=True", False),
                            ("created_now=True", False),
                        ]
                    },
                    {
                        "text": "Baza jadvallarini yaratmasdan, faqat boshqa modellar uchun umumiy maydonlar shablonini beruvchi model qanday e'lon qilinadi?",
                        "difficulty": "medium",
                        "choices": [
                            ("Meta klassida abstract = True orqali", True),
                            ("Meta klassida base = True orqali", False),
                            ("Meta klassida template = True orqali", False),
                            ("Model klassidan emas, AbstractModel dan voris olish orqali", False),
                        ]
                    },
                    {
                        "text": "Muayyan ilova migratsiyasini boshlang'ich (bo'sh) holatga qaytarish uchun qaysi buyruq qo'llaniladi?",
                        "difficulty": "hard",
                        "choices": [
                            ("python manage.py migrate <app_name> zero", True),
                            ("python manage.py migrate <app_name> rollback", False),
                            ("python manage.py --undo", False),
                            ("python manage.py reset <app_name>", False),
                        ]
                    },
                    {
                        "text": "Katta jadvallarda tez-tez qidiriladigan maydonlar uchun indeks yaratishning eng zamonaviy va tavsiya etilgan usuli qaysi?",
                        "difficulty": "hard",
                        "choices": [
                            ("Meta klassida indexes = [models.Index(fields=[...])] orqali", True),
                            ("db_index=False qo'yish orqali", False),
                            ("Meta klassida unique_together ishlatish orqali", False),
                            ("views.py da IndexQuery ishlatish orqali", False),
                        ]
                    },
                    {
                        "text": "Modelning get_absolute_url() metodi odatda nima maqsadda yoziladi?",
                        "difficulty": "hard",
                        "choices": [
                            ("Ob'ektning to'liq havolasini reverse orqali qaytarish uchun", True),
                            ("Faqat tashqi API manzilini ko'rsatish uchun", False),
                            ("Modelning admin panelidagi URL manzilini o'chirish uchun", False),
                            ("Statik fayllar joylashuvini ko'rsatish uchun", False),
                        ]
                    },
                ]
            },
            {
                "name": "Django ORM va So'rovlar",
                "slug": "django-orm-queries",
                "icon": "database",
                "description": "Filter, exclude, annotate, aggregate, select_related, prefetch_related va murakkab Q/F ob'ektlari.",
                "questions": [
                    {
                        "text": "Baza jadvalidagi barcha yozuvlarni QuerySet ko'rinishida olish uchun qaysi usul chaqiriladi?",
                        "difficulty": "easy",
                        "choices": [
                            ("Model.objects.all()", True),
                            ("Model.objects.get()", False),
                            ("Model.objects.filter()", False),
                            ("Model.objects.fetch()", False),
                        ]
                    },
                    {
                        "text": "Bitta aniq yozuvni topish uchun ishlatiladigan va topilmasa DoesNotExist xatoligini beruvchi metod qaysi?",
                        "difficulty": "easy",
                        "choices": [
                            ("Model.objects.get()", True),
                            ("Model.objects.find()", False),
                            ("Model.objects.first()", False),
                            ("Model.objects.single()", False),
                        ]
                    },
                    {
                        "text": "Maydon qiymati berilgan satr bilan boshlanishini filtr qilish uchun qaysi lookup ishlatiladi?",
                        "difficulty": "easy",
                        "choices": [
                            ("field__startswith", True),
                            ("field__has", False),
                            ("field__contains_start", False),
                            ("field__starts", False),
                        ]
                    },
                    {
                        "text": "Shartga mos kelmaydigan yozuvlarni olib tashlab saralash uchun qaysi metod qo'llaniladi?",
                        "difficulty": "easy",
                        "choices": [
                            ("Model.objects.exclude()", True),
                            ("Model.objects.remove()", False),
                            ("Model.objects.delete()", False),
                            ("Model.objects.without()", False),
                        ]
                    },
                    {
                        "text": "ForeignKey munosabatida N+1 muammosini oldini olish uchun (SQL JOIN orqali) qaysi metod ishlatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("select_related()", True),
                            ("prefetch_related()", False),
                            ("join_related()", False),
                            ("optimize_related()", False),
                        ]
                    },
                    {
                        "text": "Ko'pdan-ko'pga (ManyToManyField) yoki teskari ForeignKey bog'lanishida N+1 muammosini hal qilish uchun qaysi metod ishlatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("prefetch_related()", True),
                            ("select_related()", False),
                            ("join_tables()", False),
                            ("fetch_m2m()", False),
                        ]
                    },
                    {
                        "text": "Baza darajasida barcha yozuvlar bo'yicha umumiy o'rtacha yoki yig'indini (masalan, Avg, Sum) hisoblash uchun nima ishlatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("aggregate()", True),
                            ("annotate()", False),
                            ("accumulate()", False),
                            ("calculate()", False),
                        ]
                    },
                    {
                        "text": "Har bir yozuvga yangi hisoblangan maydon (masalan, unga tegishli izohlar soni) qo'shib olish uchun qaysi metod qo'llaniladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("annotate()", True),
                            ("aggregate()", False),
                            ("append_fields()", False),
                            ("calculate_row()", False),
                        ]
                    },
                    {
                        "text": "ORM so'rovlarida murakkab mantiqiy OR (|) va NOT (~) shartlarini qo'llash uchun qaysi ob'ekt kerak?",
                        "difficulty": "hard",
                        "choices": [
                            ("django.db.models.Q ob'ekti", True),
                            ("django.db.models.F ob'ekti", False),
                            ("django.db.models.Expression", False),
                            ("django.db.models.FilterLogic", False),
                        ]
                    },
                    {
                        "text": "Baza darajasidagi maydon qiymatini xotiraga yuklamasdan to'g'ridan-to'g'ri o'zgartirish (masalan: ko'rishlar sonini +1 ga oshirish) uchun qaysi ob'ekt qo'llaniladi?",
                        "difficulty": "hard",
                        "choices": [
                            ("F() ob'ekti (masalan, views=F('views') + 1)", True),
                            ("Q() ob'ekti", False),
                            ("Value() ob'ekti", False),
                            ("Func() ob'ekti", False),
                        ]
                    },
                    {
                        "text": "Katta hajmdagi yozuvlarni xotirani to'ldirmasdan qismlarga bo'lib ketma-ket qayta ishlash uchun qaysi QuerySet metodi ishlatiladi?",
                        "difficulty": "hard",
                        "choices": [
                            ("iterator()", True),
                            ("chunks()", False),
                            ("batch()", False),
                            ("stream()", False),
                        ]
                    },
                ]
            },
            {
                "name": "Django Ko'rinishlar va Autentifikatsiya",
                "slug": "django-views-auth",
                "icon": "shield",
                "description": "Funksiya va klassga asoslangan ko'rinishlar (CBV), Login, Logout, Decorator va Mixinlar.",
                "questions": [
                    {
                        "text": "Faqat tizimga kirgan foydalanuvchilar kira olishi uchun Funksiyaga asoslangan ko'rinishga (FBV) qaysi dekorator qo'yiladi?",
                        "difficulty": "easy",
                        "choices": [
                            ("@login_required", True),
                            ("@auth_required", False),
                            ("@is_authenticated", False),
                            ("@user_logged_in", False),
                        ]
                    },
                    {
                        "text": "Klassga asoslangan ko'rinishda (CBV) faqat tizimga kirgan foydalanuvchilarga ruxsat berish uchun qaysi mixin voris olinadi?",
                        "difficulty": "easy",
                        "choices": [
                            ("LoginRequiredMixin", True),
                            ("AuthRequiredMixin", False),
                            ("AuthenticatedOnlyMixin", False),
                            ("UserAccessMixin", False),
                        ]
                    },
                    {
                        "text": "Foydalanuvchini autentifikatsiya qilish uchun uning login va parolini tekshiruvchi funksiya qaysi?",
                        "difficulty": "easy",
                        "choices": [
                            ("authenticate(request, username=..., password=...)", True),
                            ("check_user(username, password)", False),
                            ("verify_credentials(username, password)", False),
                            ("validate_login(username, password)", False),
                        ]
                    },
                    {
                        "text": "Statik HTML sahifasini hech qanday ma'lumotlar bazasisiz ko'rsatish uchun qaysi standart CBV qulay?",
                        "difficulty": "easy",
                        "choices": [
                            ("TemplateView", True),
                            ("View", False),
                            ("RedirectView", False),
                            ("StaticView", False),
                        ]
                    },
                    {
                        "text": "Baza yozuvlari ro'yxatini chiqarish va sahifalash (pagination) uchun qaysi generik CBV ishlatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("ListView", True),
                            ("DetailView", False),
                            ("GridView", False),
                            ("TableQueryView", False),
                        ]
                    },
                    {
                        "text": "Yagona ob'ekt ma'lumotlarini (masalan, bitta maqola sahifasini) ko'rsatish uchun qaysi CBV ishlatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("DetailView", True),
                            ("SingleObjectView", False),
                            ("ItemView", False),
                            ("OneView", False),
                        ]
                    },
                    {
                        "text": "CreateView da forma muvaffaqiyatli saqlangandan so'ng yo'naltiriladigan URL qaysi xususiyat orqali beriladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("success_url", True),
                            ("redirect_url", False),
                            ("target_url", False),
                            ("next_url", False),
                        ]
                    },
                    {
                        "text": "Foydalanuvchi huquqlarini (Permission) tekshirish uchun CBV da qaysi mixin qo'llaniladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("PermissionRequiredMixin", True),
                            ("RightsCheckMixin", False),
                            ("HasPermissionMixin", False),
                            ("RoleRequiredMixin", False),
                        ]
                    },
                    {
                        "text": "CBV da shablonga (template) qo'shimcha o'zgaruvchilar uzatish uchun qaysi metod qayta yoziladi (override qilinadi)?",
                        "difficulty": "hard",
                        "choices": [
                            ("get_context_data(self, **kwargs)", True),
                            ("get_template_vars(self)", False),
                            ("render_context(self)", False),
                            ("add_context(self, context)", False),
                        ]
                    },
                    {
                        "text": "CSRF himoyasidan mustasno qilish uchun qaysi dekorator ishlatiladi (ehtiyotkorlik bilan qo'llanishi shart)?",
                        "difficulty": "hard",
                        "choices": [
                            ("@csrf_exempt", True),
                            ("@no_csrf", False),
                            ("@csrf_disable", False),
                            ("@skip_csrf", False),
                        ]
                    },
                    {
                        "text": "Foydalanuvchi o'ziga tegishli bo'lmagan ob'ektni tahrirlashini cheklash uchun qaysi metodda tekshiruv o'rnatiladi?",
                        "difficulty": "hard",
                        "choices": [
                            ("get_object() yoki dispatch() metodida", True),
                            ("get_queryset_only() metodida", False),
                            ("validate_user_role() metodida", False),
                            ("form_invalid() metodida", False),
                        ]
                    },
                ]
            },
            {
                "name": "Django Formalari va Validatsiya",
                "slug": "django-forms-validation",
                "icon": "file-text",
                "description": "ModelForm, Form, maydon validatsiyasi, clean() metodlari va xatoliklarni chiqarish.",
                "questions": [
                    {
                        "text": "Mavjud Django modeliga asoslangan forma yaratish uchun qaysi klassdan voris olinadi?",
                        "difficulty": "easy",
                        "choices": [
                            ("forms.ModelForm", True),
                            ("forms.Form", False),
                            ("forms.BaseModelForm", False),
                            ("forms.AutoForm", False),
                        ]
                    },
                    {
                        "text": "HTML shablonida POST formasi yaratilganda xavfsizlik uchun qaysi teg kiritilishi shart?",
                        "difficulty": "easy",
                        "choices": [
                            ("{% csrf_token %}", True),
                            ("{% token_security %}", False),
                            ("{% secret_key %}", False),
                            ("{% form_protect %}", False),
                        ]
                    },
                    {
                        "text": "Forma yuborilgan barcha ma'lumotlar to'g'riligini tekshirish uchun ko'rinishda qaysi metod chaqiriladi?",
                        "difficulty": "easy",
                        "choices": [
                            ("form.is_valid()", True),
                            ("form.validate()", False),
                            ("form.check()", False),
                            ("form.is_clean()", False),
                        ]
                    },
                    {
                        "text": "Tekshiruvdan muvaffaqiyatli o'tgan tozalangan ma'lumotlar forma ob'ektining qaysi lug'atida saqlanadi?",
                        "difficulty": "easy",
                        "choices": [
                            ("form.cleaned_data", True),
                            ("form.valid_data", False),
                            ("form.clean_values", False),
                            ("form.data_safe", False),
                        ]
                    },
                    {
                        "text": "Muayyan bitta maydonni (masalan, 'email') maxsus qoida bo'yicha tekshirish uchun formaga qaysi metod yoziladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("clean_email(self)", True),
                            ("validate_email(self)", False),
                            ("check_email(self)", False),
                            ("verify_email(self)", False),
                        ]
                    },
                    {
                        "text": "Bir nechta maydonlarni bir-biriga bog'liq holda tekshirish uchun (masalan, ikkita parolni taqqoslash) qaysi metod override qilinadi?",
                        "difficulty": "medium",
                        "choices": [
                            ("clean(self)", True),
                            ("validate_all(self)", False),
                            ("cross_validate(self)", False),
                            ("check_all_fields(self)", False),
                        ]
                    },
                    {
                        "text": "ModelForm da modelning qaysi maydonlari formaga kiritilishini qayerda ko'rsatiladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("Meta klassining fields parametrida", True),
                            ("Form klassining visible_fields ro'yxatida", False),
                            ("forms.ModelForm ning args qismida", False),
                            ("views.py ning form_class parametrida", False),
                        ]
                    },
                    {
                        "text": "Forma validatsiyasida xatolik haqida xabar berish uchun qaysi istisno (exception) chaqiriladi?",
                        "difficulty": "medium",
                        "choices": [
                            ("forms.ValidationError", True),
                            ("forms.FormError", False),
                            ("ValueError", False),
                            ("forms.InvalidFieldError", False),
                        ]
                    },
                    {
                        "text": "ModelForm da bazaga darhol saqlamasdan ob'ekt nusxasini olish uchun nima qilinadi?",
                        "difficulty": "hard",
                        "choices": [
                            ("form.save(commit=False)", True),
                            ("form.save(delay=True)", False),
                            ("form.instance_only()", False),
                            ("form.build_object()", False),
                        ]
                    },
                    {
                        "text": "Forma maydonining HTML da ko'rinishini (input type, css klass, placeholder) o'zgartirish uchun nima ishlatiladi?",
                        "difficulty": "hard",
                        "choices": [
                            ("widget parametri (masalan, forms.TextInput(attrs={...}))", True),
                            ("renderer parametri", False),
                            ("html_attributes parametri", False),
                            ("view_style parametri", False),
                        ]
                    },
                    {
                        "text": "Fayl yoki rasm yuklaydigan formani qabul qilishda HTML form tagiga qaysi atribut qo'yilishi shart?",
                        "difficulty": "hard",
                        "choices": [
                            ('enctype="multipart/form-data"', True),
                            ('enctype="application/octet-stream"', False),
                            ('upload="file"', False),
                            ('method="file"', False),
                        ]
                    },
                ]
            }
        ]

        categories_dict = {}
        for cat_info in data:
            cat, _ = Category.objects.get_or_create(
                slug=cat_info["slug"],
                defaults={
                    "name": cat_info["name"],
                    "icon": cat_info["icon"],
                    "description": cat_info["description"],
                }
            )
            cat.icon = cat_info["icon"]
            cat.save()
            categories_dict[cat.slug] = cat

            for q_data in cat_info["questions"]:
                question, _ = Question.objects.get_or_create(
                    category=cat,
                    text=q_data["text"],
                    defaults={
                        "difficulty": q_data["difficulty"],
                    }
                )
                question.choices.all().delete()
                import random
                shuffled_choices = list(q_data["choices"])
                random.shuffle(shuffled_choices)
                for ch_text, is_corr in shuffled_choices:
                    Choice.objects.create(
                        question=question,
                        text=ch_text,
                        is_correct=is_corr
                    )

        sample_scores = [
            (created_users[0], "django-models-migrations", 23, 11, 10),
            (created_users[1], "django-orm-queries", 21, 11, 9),
            (created_users[2], "django-views-auth", 20, 11, 9),
            (created_users[3], "django-forms-validation", 19, 11, 8),
            (created_users[4], "django-models-migrations", 17, 11, 8),
            (created_users[5], "django-orm-queries", 16, 11, 7),
            (created_users[0], "django-views-auth", 18, 11, 8),
            (created_users[1], "django-forms-validation", 22, 11, 10),
            (admin_user, "django-models-migrations", 25, 11, 11),
        ]

        for u, c_slug, score, total_q, corr_a in sample_scores:
            cat = categories_dict.get(c_slug)
            if not UserScore.objects.filter(user=u, category=cat).exists():
                UserScore.objects.create(
                    user=u,
                    category=cat,
                    score=score,
                    total_questions=total_q,
                    correct_answers=corr_a,
                    details=[
                        {
                            "question_text": f"Namuna savol #{i+1}",
                            "difficulty": "medium",
                            "difficulty_display": "O'rta",
                            "points": 2,
                            "points_earned": 2 if i < corr_a else 0,
                            "selected_choice_text": "Tanlangan javob",
                            "correct_choice_text": "To'g'ri javob",
                            "is_correct": i < corr_a
                        } for i in range(total_q)
                    ]
                )

        self.stdout.write(self.style.SUCCESS("Muvaffaqiyatli yakunlandi!"))
