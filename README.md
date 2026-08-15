# Backend assessment - offline collection intake

**Time box: three hours.** Stop at three hours. What you have at three hours is
what we look at.

## The situation

Kirinyaga Distributors runs six vans out of a depot in Nakuru. Reps take cash
and M-Pesa at the customer's door and record each receipt on an Android
handset. Coverage on the routes is bad. The handset writes to local storage
first and pushes to us later - sometimes minutes later, sometimes the next
morning when the rep gets back to the depot and onto wifi.

Last week the depot manager found the same receipt banked twice in our
reporting. That is where you come in.

Your job is the server side of that push: **the endpoint that accepts a batch
of collections a handset recorded while it was offline.**

## The contract, as it was handed to you

This is verbatim from the ticket. It is what a real ticket looks like.

```
POST /api/v1/collections/batch/

  {
    "device_id": "AND-KDG907X",
    "receipts": [
      {
        "client_uuid": "9f1c0000-0000-4000-8000-000000000000",
        "outlet_code": "OUT-1003",
        "invoice_no": "INV-480123",
        "method": "CASH",
        "amount_kes": 14820.00,
        "receipt_ref": "RC482910337",
        "recorded_at": "2026-07-14T11:42:08+03:00"
      }
    ]
  }

  A batch is up to 200 receipts.
  The handset retries the whole batch if it does not get a response, so
  the same batch may arrive more than once.
  Where two records collide, last write wins by recorded_at.

GET /api/v1/collections/?outlet_code=&date_from=&date_to=

  Lists what the server holds. Paginated.
```

We also need to be able to see what happened to a batch after the fact.

## What to deliver

1. Both endpoints, working, against Postgres.
2. Tests. `make test` must pass. The three acceptance tests in
   `tests/test_acceptance.py` are the floor, not the ceiling - we expect tests
   you wrote yourself as well.
3. `make test` and `make test-pg` both passing.
4. `DECISIONS.md`, filled in. See below.
5. `AI-LOG.md`, filled in.

## Read the contract before you build to it

The ticket above was written by a person in a hurry. Parts of it are clear.
Parts of it are not, and at least one part of it will cause a defect in
production if you implement it exactly as written.

We are not going to tell you which parts. Finding that out is the job.

Where the contract is silent or wrong, **make a call, implement your call, and
write down why in `DECISIONS.md`.** A defensible decision that contradicts the
ticket scores higher than faithful implementation of a bad instruction. Coming
back and saying "the ticket says X but X is unsafe because Y, so I did Z" is
exactly the behaviour we are hiring for.

`fixtures/sample_batch.json` is a real capture from a handset. It is worth
reading closely before you write any code.

## Getting started

Unzip this folder and make it a git repository before you start work. We read
the commit history.

```bash
git init && git add -A && git commit -m "Starting point as supplied"
```

Then:

```bash
docker compose up -d db      # Postgres on 5432
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make migrate
make seed                    # loads the outlet list
make test
make run                     # http://127.0.0.1:8000
```

Tests default to SQLite so they run without Docker. `make test-pg` runs the
same suite against Postgres. Both must pass before you submit.

A GitHub Actions workflow is included in `.github/workflows/`. You do not have
to use it - if you push this to your own GitHub it runs for free, and if you
do not, `make test` and `make test-pg` passing locally is what matters.

## Sending it back

Create a repository on your own GitHub or GitLab account, make it **public**,
push, and send us the link.

```bash
git remote add origin <your repo url>
git push -u origin main
```

That is the whole submission. Nothing to email, no access to grant.

## How we read it

- Does it work, and can we tell that it works without running it?
- Small, readable commits. We read the history. One giant commit reads as a
  paste and we will probe it hard in the live session.
- Tests that assert behaviour, not implementation.
- `DECISIONS.md` is weighted as heavily as the code.

## Using AI

Use whatever helps. You own everything you submit. In the live session you
will extend this service in front of us, so do not submit code you cannot
explain line by line.
