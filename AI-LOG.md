# AI Log

## What I used it for

I used ChatGPT to:

- Discuss model design and data structures.
- Review duplicate receipt and batch handling approaches.
- Explore validation rules and edge cases.
- Suggest additional test cases.
- Review documentation structure.

All final implementation decisions and code changes were made and reviewed by me.

## Something it got wrong

An early suggestion was to validate outlet codes against the Outlet table.

After reviewing the requirements, I decided not to enforce outlet validation because the contract does not require it and it could prevent valid offline collections from syncing.

## What I verified myself

I personally verified:

- The sample payload and device ID inconsistencies.
- The use of `receipt_ref` for collision detection.
- Last-write-wins behavior using `recorded_at`.
- Duplicate batch handling.
- Validation rules.
- The POST and GET endpoint behavior.
- That all provided and custom tests passed successfully.