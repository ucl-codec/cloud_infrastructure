# Data sync

Each local node has an S3 data import bucket where data providers can upload data. This is
automatically synced to the EFS file store used by the node for training.

In addition to adding and modifying data, the sync will also delete data that has been removed 
from the S3 bucket.

The sync is initiated once per hour. The system administrator can also manually trigger a sync
provided one is not already in progress.

---
## Monitor status of a data sync

- Log into the AWS Console
- Navigate to DataSync
- Click on the task for the appropriate local node
- Examine the task status in the Overview, and the `History` tab to view previous events 

---

## Manually trigger a data sync

- Log into the AWS Console
- Navigate to DataSync
- Click on the task for the appropriate local node
- Click `Start` and `Start with defaults`

