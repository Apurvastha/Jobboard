# jobs/management/commands/seed_data.py
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, CompanyProfile, CandidateProfile
from jobs.models import JobListing, Category, Tag
from applications.models import Application
from blog.models import (
    Post, Comment,
    Category as BlogCategory,
    Tag as BlogTag
)


class Command(BaseCommand):
    help = 'Seed the database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Application.objects.all().delete()
            JobListing.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()
            CompanyProfile.objects.all().delete()
            CandidateProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            Post.objects.all().delete()
            Comment.objects.all().delete()
            BlogCategory.objects.all().delete()
            BlogTag.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

        # ── JOB CATEGORIES ─────────────────────────────────────
        self.stdout.write('Creating job categories...')
        backend = Category.objects.get_or_create(
            name='Backend', slug='backend'
        )[0]
        frontend = Category.objects.get_or_create(
            name='Frontend', slug='frontend'
        )[0]
        ai = Category.objects.get_or_create(
            name='AI/ML', slug='ai-ml'
        )[0]
        devops = Category.objects.get_or_create(
            name='DevOps', slug='devops'
        )[0]

        # ── JOB TAGS ───────────────────────────────────────────
        self.stdout.write('Creating tags...')
        python_tag   = Tag.objects.get_or_create(name='Python')[0]
        django_tag   = Tag.objects.get_or_create(name='Django')[0]
        fastapi_tag  = Tag.objects.get_or_create(name='FastAPI')[0]
        react_tag    = Tag.objects.get_or_create(name='React')[0]
        ml_tag       = Tag.objects.get_or_create(name='Machine Learning')[0]
        docker_tag   = Tag.objects.get_or_create(name='Docker')[0]
        k8s_tag      = Tag.objects.get_or_create(name='Kubernetes')[0]
        redis_tag    = Tag.objects.get_or_create(name='Redis')[0]

        # ── COMPANY USERS ──────────────────────────────────────
        self.stdout.write('Creating company users...')
        user_mercari = User.objects.get_or_create(
            username='mercari',
            defaults={
                'email': 'hire@mercari.com',
                'role': User.Role.COMPANY,
            }
        )[0]
        user_mercari.set_password('testpass123')
        user_mercari.save()

        user_smarthr = User.objects.get_or_create(
            username='smarthr',
            defaults={
                'email': 'hire@smarthr.com',
                'role': User.Role.COMPANY,
            }
        )[0]
        user_smarthr.set_password('testpass123')
        user_smarthr.save()

        user_cyber = User.objects.get_or_create(
            username='cyberagent',
            defaults={
                'email': 'hire@cyberagent.com',
                'role': User.Role.COMPANY,
            }
        )[0]
        user_cyber.set_password('testpass123')
        user_cyber.save()

        user_ubie = User.objects.get_or_create(
            username='ubie',
            defaults={
                'email': 'hire@ubie.life',
                'role': User.Role.COMPANY,
            }
        )[0]
        user_ubie.set_password('testpass123')
        user_ubie.save()

        # ── COMPANY PROFILES ───────────────────────────────────
        self.stdout.write('Creating company profiles...')
        mercari = CompanyProfile.objects.get_or_create(
            user=user_mercari,
            defaults={
                'name': 'Mercari',
                'website': 'https://mercari.com',
                'description': 'Japan leading marketplace app.',
                'country': 'Japan',
                'founded_year': 2013,
            }
        )[0]

        smarthr = CompanyProfile.objects.get_or_create(
            user=user_smarthr,
            defaults={
                'name': 'SmartHR',
                'website': 'https://smarthr.jp',
                'description': 'Cloud HR software for Japanese companies.',
                'country': 'Japan',
                'founded_year': 2013,
            }
        )[0]

        cyberagent = CompanyProfile.objects.get_or_create(
            user=user_cyber,
            defaults={
                'name': 'CyberAgent',
                'website': 'https://cyberagent.co.jp',
                'description': 'Internet services and AI research.',
                'country': 'Japan',
                'founded_year': 1998,
            }
        )[0]

        ubie = CompanyProfile.objects.get_or_create(
            user=user_ubie,
            defaults={
                'name': 'Ubie',
                'website': 'https://ubie.life',
                'description': 'AI-powered medical technology startup.',
                'country': 'Japan',
                'founded_year': 2017,
            }
        )[0]

        # ── CANDIDATE USERS ────────────────────────────────────
        self.stdout.write('Creating candidate users...')
        candidates = []
        candidate_data = [
            ('alice', 'alice@test.com'),
            ('bob', 'bob@test.com'),
            ('carol', 'carol@test.com'),
            ('dave', 'dave@test.com'),
            ('eve', 'eve@test.com'),
        ]
        for username, email in candidate_data:
            user = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': User.Role.CANDIDATE,
                }
            )[0]
            user.set_password('testpass123')
            user.save()
            CandidateProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f'Backend engineer looking for opportunities in Japan.',
                    'years_of_experience': random.randint(1, 5),
                    'skills': 'Python, Django, FastAPI, PostgreSQL, Redis',
                }
            )
            candidates.append(user)

        # ── FEATURED JOB LISTINGS ──────────────────────────────
        self.stdout.write('Creating featured job listings...')
        job1 = JobListing.objects.get_or_create(
            title='Senior Backend Engineer',
            company=mercari,
            defaults={
                'description': (
                    'Build scalable microservices for Japan largest marketplace. '
                    'You will work on high-traffic systems handling millions of '
                    'transactions daily. Strong Python and Go experience required.'
                ),
                'category': backend,
                'job_type': 'full_time',
                'experience_level': 'senior',
                'location': 'Tokyo',
                'is_remote': False,
                'salary_min': 8000000,
                'salary_max': 12000000,
                'is_active': True,
            }
        )[0]
        job1.tags.set([python_tag, django_tag, redis_tag, docker_tag])

        job2 = JobListing.objects.get_or_create(
            title='Python Django Developer',
            company=smarthr,
            defaults={
                'description': (
                    'Build internal tools and REST APIs with Django and DRF. '
                    'You will own features end to end from database design to '
                    'deployment. Remote friendly position.'
                ),
                'category': backend,
                'job_type': 'full_time',
                'experience_level': 'mid',
                'location': 'Tokyo',
                'is_remote': True,
                'salary_min': 6000000,
                'salary_max': 9000000,
                'is_active': True,
            }
        )[0]
        job2.tags.set([python_tag, django_tag, docker_tag])

        job3 = JobListing.objects.get_or_create(
            title='AI Backend Engineer',
            company=cyberagent,
            defaults={
                'description': (
                    'Build LLM pipelines and RAG systems with FastAPI. '
                    'You will work directly with the AI lab team on production '
                    'AI features used by millions of users.'
                ),
                'category': ai,
                'job_type': 'full_time',
                'experience_level': 'mid',
                'location': 'Osaka',
                'is_remote': True,
                'salary_min': 7000000,
                'salary_max': 10000000,
                'is_active': True,
            }
        )[0]
        job3.tags.set([python_tag, fastapi_tag, ml_tag, docker_tag])

        job4 = JobListing.objects.get_or_create(
            title='ML Engineer — Healthcare AI',
            company=ubie,
            defaults={
                'description': (
                    'Apply machine learning to healthcare data to improve '
                    'patient outcomes. Work on NLP models for medical records '
                    'and symptom analysis.'
                ),
                'category': ai,
                'job_type': 'full_time',
                'experience_level': 'senior',
                'location': 'Tokyo',
                'is_remote': True,
                'salary_min': 9000000,
                'salary_max': 14000000,
                'is_active': True,
            }
        )[0]
        job4.tags.set([python_tag, ml_tag, docker_tag, k8s_tag])

        job5 = JobListing.objects.get_or_create(
            title='Junior Python Developer',
            company=smarthr,
            defaults={
                'description': (
                    'Entry level Python position. You will work alongside '
                    'senior engineers building internal tooling and APIs.'
                ),
                'category': backend,
                'job_type': 'contract',
                'experience_level': 'junior',
                'location': 'Tokyo',
                'is_remote': False,
                'salary_min': 4000000,
                'salary_max': 5500000,
                'is_active': True,
            }
        )[0]
        job5.tags.set([python_tag, django_tag])

        # ── BULK JOB LISTINGS ──────────────────────────────────
        self.stdout.write('Creating 200 bulk job listings...')
        companies = [mercari, smarthr, cyberagent, ubie]
        categories = [backend, frontend, ai, devops]
        all_tags = [
            python_tag, django_tag, fastapi_tag,
            react_tag, ml_tag, docker_tag, k8s_tag, redis_tag
        ]
        locations = ['Tokyo', 'Osaka', 'Kyoto', 'Fukuoka', 'Nagoya']
        job_types = ['full_time', 'part_time', 'contract', 'internship']
        levels = ['junior', 'mid', 'senior']

        bulk_jobs = []
        for i in range(200):
            bulk_jobs.append(JobListing(
                title=f'Engineer Position {i}',
                description=f'Job description for position {i}. '
                            f'Looking for talented engineers to join our team.',
                company=random.choice(companies),
                category=random.choice(categories),
                job_type=random.choice(job_types),
                experience_level=random.choice(levels),
                location=random.choice(locations),
                is_remote=random.choice([True, False]),
                salary_min=random.randint(3000000, 8000000),
                salary_max=random.randint(8000000, 15000000),
                is_active=random.choice([True, True, True, False]),
            ))

        created_bulk = JobListing.objects.bulk_create(
            bulk_jobs,
            ignore_conflicts=True
        )

        # add random tags to bulk jobs
        for job in JobListing.objects.filter(
            title__startswith='Engineer Position'
        ):
            random_tags = random.sample(all_tags, k=random.randint(1, 3))
            job.tags.set(random_tags)

        # ── APPLICATIONS ───────────────────────────────────────
        self.stdout.write('Creating applications...')
        featured_jobs = [job1, job2, job3, job4, job5]
        statuses = ['pending', 'reviewing', 'rejected', 'accepted']

        for candidate in candidates:
            # each candidate applies to 2-3 jobs
            jobs_to_apply = random.sample(featured_jobs, k=random.randint(2, 3))
            for job in jobs_to_apply:
                Application.objects.get_or_create(
                    candidate=candidate,
                    job=job,
                    defaults={
                        'status': random.choice(statuses),
                        'cover_letter': (
                            f'I am very interested in the {job.title} position '
                            f'at {job.company.name}. I have strong Python skills '
                            f'and experience with Django and FastAPI.'
                        ),
                    }
                )

        # ── BLOG DATA ──────────────────────────────────────────
        self.stdout.write('Creating blog data...')
        blog_tech = BlogCategory.objects.get_or_create(
            name='Technology', slug='technology'
        )[0]
        blog_career = BlogCategory.objects.get_or_create(
            name='Career', slug='career'
        )[0]
        blog_python = BlogCategory.objects.get_or_create(
            name='Python', slug='python'
        )[0]

        blog_django_tag  = BlogTag.objects.get_or_create(name='Django')[0]
        blog_fastapi_tag = BlogTag.objects.get_or_create(name='FastAPI')[0]
        blog_japan_tag   = BlogTag.objects.get_or_create(name='Japan')[0]
        blog_backend_tag = BlogTag.objects.get_or_create(name='Backend')[0]
        blog_ai_tag      = BlogTag.objects.get_or_create(name='AI')[0]

        author1 = candidates[0]
        author2 = candidates[1]

        post1 = Post.objects.get_or_create(
            slug='backend-job-japan',
            defaults={
                'title': 'Getting a Backend Job in Japan',
                'body': (
                    'Japan has a thriving tech scene with companies like '
                    'Mercari and SmartHR actively hiring international engineers. '
                    'English is increasingly accepted in technical roles.'
                ),
                'author': author1,
                'category': blog_career,
                'status': 'published',
                'views_count': 450,
            }
        )[0]
        post1.tags.set([blog_japan_tag, blog_backend_tag])

        post2 = Post.objects.get_or_create(
            slug='django-vs-fastapi-2026',
            defaults={
                'title': 'Django vs FastAPI in 2026',
                'body': (
                    'Both Django and FastAPI are excellent choices for '
                    'backend development. Django is batteries-included and '
                    'great for complex data models. FastAPI is async-first '
                    'and perfect for AI microservices.'
                ),
                'author': author1,
                'category': blog_python,
                'status': 'published',
                'views_count': 820,
            }
        )[0]
        post2.tags.set([blog_django_tag, blog_fastapi_tag, blog_backend_tag])

        post3 = Post.objects.get_or_create(
            slug='rag-systems-fastapi',
            defaults={
                'title': 'Building RAG Systems with FastAPI',
                'body': (
                    'RAG pipelines are the backbone of modern AI applications. '
                    'FastAPI streaming responses with SSE make it easy to stream '
                    'LLM output directly to clients in real time.'
                ),
                'author': author2,
                'category': blog_tech,
                'status': 'published',
                'views_count': 1200,
            }
        )[0]
        post3.tags.set([blog_fastapi_tag, blog_ai_tag, blog_backend_tag])

        # comments
        comment1 = Comment.objects.get_or_create(
            post=post1,
            author=candidates[1],
            body='Great article! Very helpful for my Japan job search.',
            defaults={'is_approved': True}
        )[0]

        comment2 = Comment.objects.get_or_create(
            post=post1,
            author=candidates[2],
            body='Do you need Japanese language skills?',
            defaults={'is_approved': True}
        )[0]

        Comment.objects.get_or_create(
            post=post1,
            author=author1,
            body='N3 helps but many companies hire engineers in English.',
            defaults={
                'parent': comment2,
                'is_approved': True,
            }
        )

        Comment.objects.get_or_create(
            post=post2,
            author=candidates[2],
            body='FastAPI is so much faster for pure API work.',
            defaults={'is_approved': True}
        )

        # ── SUMMARY ────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\n=== Seed complete ==='))
        self.stdout.write(f'  Users:        {User.objects.count()}')
        self.stdout.write(f'  Companies:    {CompanyProfile.objects.count()}')
        self.stdout.write(f'  Candidates:   {CandidateProfile.objects.count()}')
        self.stdout.write(f'  Job listings: {JobListing.objects.count()}')
        self.stdout.write(f'  Applications: {Application.objects.count()}')
        self.stdout.write(f'  Blog posts:   {Post.objects.count()}')
        self.stdout.write(f'  Comments:     {Comment.objects.count()}')
        self.stdout.write(self.style.SUCCESS('====================='))