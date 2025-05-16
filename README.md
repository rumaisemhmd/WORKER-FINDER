Worker Finder

Worker Finder is a Django-based web application that connects users with verified and unverified daily wage workers. It allows users to search for local workers, book them for services, and handle task completion securely using OTP and a wallet-based payment system.


---

Features

For Users

Sign up and log in to the platform.

Search and filter workers by type and location.

View worker profiles (verified/unverified).

Book a worker and schedule a service.

Receive an OTP upon booking to confirm job completion.

See job history and transactions.

In-app wallet system for smoother payments.


For Workers

Sign up and submit interview requests (if unverified).

Verified workers can manage their service availability.

Accept or reject bookings.

Enter OTP to mark a job as completed.

Track earnings in their wallet.


For Admin

Manage user and worker accounts.

Approve or reject worker interview requests.

View all transactions and job status.

Dashboard to monitor activity across the platform.



---

Key Modules

Authentication – User/Worker registration & login.

Booking System – User books and schedules a worker.

OTP Verification – Job marked completed only after OTP validation.

Wallet System – Payments are added to worker wallets post-completion.

Admin Panel – Full control over users, workers, and jobs.



---

OTP Verification (Post-Booking Completion)

OTP is generated when a user books a worker.

OTP is visible in the user dashboard.

User must share OTP with the worker after the task is done.

Worker enters the OTP to mark job as completed.

This prevents misuse and ensures work confirmation.



---

Wallet System

Each worker has an associated wallet.

On successful OTP verification, payment is transferred to the worker’s wallet.

Wallet balance is updated accordingly.

Workers can request withdrawal.



---

Payment Integration

Instead of using Razorpay or online gateways, this project uses manual QR code payments.

Users are required to scan a QR and pay for booking confirmation and submit upi id.

Admin verifies the payment manually and then confirms the job.

For now no online payment gateway is integrated, keeping it simple and local-transaction friendly.



---

Technologies Used

Backend: Django, Python

Frontend: HTML, CSS, Bootstrap, Javascript

Database: PostgreSQL 

Others: Django Admin, Virtual Environment, GitHub for version control
