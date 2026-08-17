# Decisions

## Model Design Decisions

### Receipt Identity
- Used `receipt_ref` as the unique business identifier.
- Enforced a uniqueness constraint on `receipt_ref`.

### Client UUID
- Stored `client_uuid` but did not use it for uniqueness.

### Conflict Resolution
- Used `recorded_at` for last-write-wins behavior.
- Newer records update existing records; older or equal records are ignored.

### Device IDs
- Stored both batch-level and receipt-level `device_id`.
- Sample data contains both and they do not always match.

### Outlet Handling
- Stored `outlet_code` directly on the collection record.
- Did not validate against the Outlet table.

### Audit History
- Kept current receipt state in `Collection`.
- Stored processing history in audit tables.

### Batch Tracking
- Added `CollectionBatch` and `BatchAudit` models.
- Allows tracking what happened to each batch.

### Duplicate Batch Detection
- Generated a SHA-256 hash from the batch payload.
- Used the hash to identify duplicate batch retries.

### Database Indexes
- Added indexes on fields used for filtering and lookups.

---

## Validation Decisions

### Batch Size
- Maximum of 200 receipts per batch.
- Larger batches are rejected.

### Empty Batches
- Empty batches are rejected.

### Duplicate Receipt References
- Duplicate `receipt_ref` values within the same batch are rejected.

### Payment Methods
- Accepted:
  - CASH
  - MPESA
  - CHEQUE

### Amount Validation
- Amount must be greater than zero.

### Receipt Device ID
- Treated as optional because it appears in the sample but not in the original contract.

---

## API Decisions

### Duplicate Batch Handling
- Duplicate batches return HTTP 200.
- Duplicate retries are treated as successful idempotent operations.

### Receipt-Level Feedback
- Response includes the outcome for each receipt.
- Allows clients to see whether a receipt was created, updated, or ignored.

### Collection Listing
- Supports filtering by:
  - outlet_code
  - date_from
  - date_to
- Results are paginated.

### Transaction Management
- Batch processing runs inside a database transaction.
- Failures roll back the entire batch.

---

## Where the contract was unclear or wrong

### Device IDs
The contract shows a batch-level `device_id`, but the sample payload also contains receipt-level device IDs that do not always match.

I stored both values.

### Receipt Identity
The contract does not specify what uniquely identifies a receipt.

I chose `receipt_ref` because it best addresses the duplicate-banking problem.

### Duplicate Batch Detection
The contract says batches may be retried but does not specify how to detect duplicates.

I implemented duplicate detection using a deterministic SHA-256 hash of the batch payload.

---

## What I did with the awkward records in sample_batch.json

I found receipts where the receipt-level `device_id` differed from the batch-level `device_id`.

Instead of discarding either value, I stored both and treated the receipt-level value as receipt-specific information.

---

## Failure behaviour

- Invalid requests return HTTP 400.
- No partial writes occur because processing is transactional.
- Clients can correct data and safely retry.
- Duplicate batches return HTTP 200 and are not reprocessed.

---

## What I did not build, and why

- Authentication and authorization.
- Admin/reporting interfaces.
- Background job processing.

I focused on the collection intake requirements within the assessment time limit.

---

## Where this would fall over first at ten times the volume

The first bottleneck would be synchronous receipt processing within a single request.

At higher volumes I would consider:
- Bulk database operations.
- Background processing.
- Additional indexing and query optimization.
