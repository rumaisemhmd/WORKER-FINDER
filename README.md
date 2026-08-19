# Worker Finder

A Django-based web application connecting users with verified and unverified daily-wage workers. Users can search for local workers, book them for services, and confirm task completion securely through OTP verification and an in-app wallet payment system.

---

## Problem

Daily-wage service marketplaces have a trust gap: customers have no reliable way to confirm a job was actually completed, and workers have no clean way to prove it. There's also usually no simple way to hold and release payment tied to that confirmation without a full payment-gateway integration.

## Solution

Worker Finder ties job completion to OTP confirmation from both sides, and settles payment through an in-app wallet only after that confirmation — the trust mechanism is built into the workflow itself, not bolted on.

---

## Features

**For Users**
- Sign up and log in
- Search and filter workers by type and location
- View worker profiles (verified / unverified)
- Book a worker and schedule a service
- Receive an OTP on booking to confirm job completion
- View job history and transaction records
- In-app wallet for smoother payments

**For Workers**
- Sign up and submit interview requests (unverified workers)
- Verified workers manage their own service availability
- Accept or reject bookings
- Enter OTP to mark a job complete
- Track earnings through an in-app wallet

**For Admin**
- Manage user and worker accounts
- Approve or reject worker interview requests
- View all transactions and job statuses
- Dashboard to monitor platform activity

---

## Architecture / Workflow

```
User books worker → OTP generated → job performed →
user shares OTP → worker enters OTP → OTP validated →
booking marked complete → payment credited to worker wallet
```

**Key modules:**

| Module | Purpose |
|---|---|
| Authentication | User/worker registration and login |
| Booking System | Users book and schedule a worker |
| OTP Verification | Job marked complete only after OTP validation |
| Wallet System | Payments credited to worker wallets post-completion |
| Admin Panel | Full control over users, workers, and jobs |

## OTP Verification Flow

1. OTP is generated automatically on booking.
2. The OTP is visible on the user's dashboard.
3. Once the job is physically completed, the user shares the OTP with the worker.
4. The worker enters the OTP in the app to mark the job complete.
5. Only a matching, valid OTP transitions the booking to "completed" — this prevents a worker from claiming a job is done without the user's confirmation.

## Wallet System

- Every worker has an associated in-app wallet.
- On successful OTP verification, the booking payment is credited to the worker's wallet — this is the *only* code path that credits a wallet, by design, so there's a single source of truth for balance changes.
- Wallet balance updates automatically after each completed job.
- Workers can request a withdrawal from their balance.

## Payment Flow

This project intentionally uses a **manual QR-code payment flow** instead of integrating a gateway like Razorpay, to keep the system self-contained for a portfolio project:

1. The user scans a QR code and submits their UPI ID to confirm booking payment.
2. The admin manually verifies the payment.
3. Once verified, the admin confirms the booking.

No live payment gateway is integrated — a deliberate scope decision (see Future Improvements), not a missing feature.

## Technical Decisions

- **Role-based access control** enforced at the view level (customer / worker / admin), rather than relying on a single `is_staff` flag, since the app has three genuinely distinct permission sets.
- **PostgreSQL over MySQL** for stronger handling of the app's relational data — users, bookings, wallet transactions, and OTP records are all related, not flat.
- **Manual payment verification instead of a gateway integration**, to keep the project fully self-contained without external payment infrastructure dependencies.

---

## Tech Stack

- **Backend:** Django, Python
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Database:** PostgreSQL
- **Other:** Django Admin, Virtual Environment, Git/GitHub

## Installation

```bash
git clone https://github.com/rumaisemhmd/WORKER-FINDER.git
cd WORKER-FINDER
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file (or configure `settings.py` directly) with your PostgreSQL credentials and Django secret key before running migrations. *(Update this section with your project's actual required environment variables.)*

## How to Run

```bash
python manage.py migrate
python manage.py runserver
```

---

## Future Improvements

- Integrate a real payment gateway (Razorpay/Stripe) to replace the manual QR + admin-verification flow
- Automate payment verification instead of relying on manual admin confirmation
- Add automated tests around the OTP and wallet logic
- Move to Django REST Framework for a proper API layer, enabling a future mobile client to reuse the same backend

---

## Author

**Mohammed Rumaise A**
[GitHub](https://github.com/rumaisemhmd) · [LinkedIn](https://linkedin.com/in/mohammed-rumaise-a-dev)
