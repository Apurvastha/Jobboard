# get smarthr token
http POST http://127.0.0.1:8000/api/v1/accounts/token/ `
  username=smarthr password=testpass123

# try to edit mercari's job (id=1) with smarthr's token
http PATCH http://127.0.0.1:8000/api/v1/jobs/1/ `
  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwOTQwOTMzLCJpYXQiOjE3ODA5MzczMzMsImp0aSI6ImJmZTJhMTVjM2M1MDRhMmJhM2QzZGZiMTcyZjY5YjMxIiwidXNlcl9pZCI6IjMiLCJ1c2VybmFtZSI6InNtYXJ0aHIiLCJlbWFpbCI6ImhpcmVAc21hcnRoci5jb20iLCJyb2xlIjoiY29tcGFueSJ9.xxArv8bET5h07qMYO7sJC6x4mEiH9Srn5wCptYppY8g" `
  title="Hacked Title"
# expect: 403 — You can only modify your own resources.

{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwOTQwOTMzLCJpYXQiOjE3ODA5MzczMzMsImp0aSI6ImJmZTJhMTVjM2M1MDRhMmJhM2QzZGZiMTcyZjY5YjMxIiwidXNlcl9pZCI6IjMiLCJ1c2VybmFtZSI6InNtYXJ0aHIiLCJlbWFpbCI6ImhpcmVAc21hcnRoci5jb20iLCJyb2xlIjoiY29tcGFueSJ9.xxArv8bET5h07qMYO7sJC6x4mEiH9Srn5wCptYppY8g",
    "email": "hire@smarthr.com",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MTU0MjEzMywiaWF0IjoxNzgwOTM3MzMzLCJqdGkiOiI1Yzc2MzM5ZTY4NTI0MmZlYjYzZjdjZjNkZGI1YmQyNSIsInVzZXJfaWQiOiIzIiwidXNlcm5hbWUiOiJzbWFydGhyIiwiZW1haWwiOiJoaXJlQHNtYXJ0aHIuY29tIiwicm9sZSI6ImNvbXBhbnkifQ.yRC55yFFJgT1QKytj1jabOfjSYfAYLj4P_pZwz3nwSo",
    "role": "company",
    "user_id": 3,
    "username": "smarthr"
}

http PATCH http://127.0.0.1:8000/api/v1/jobs/203/ `
  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwOTQwOTMzLCJpYXQiOjE3ODA5MzczMzMsImp0aSI6ImJmZTJhMTVjM2M1MDRhMmJhM2QzZGZiMTcyZjY5YjMxIiwidXNlcl9pZCI6IjMiLCJ1c2VybmFtZSI6InNtYXJ0aHIiLCJlbWFpbCI6ImhpcmVAc21hcnRoci5jb20iLCJyb2xlIjoiY29tcGFueSJ9.xxArv8bET5h07qMYO7sJC6x4mEiH9Srn5wCptYppY8g" `
  title="Updated Senior Python Engineer Tokyo"
# expect: 200 OK with updated job