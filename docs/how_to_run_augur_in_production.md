# How to Run Augur in Production

## Resetting Logs with AUGUR_RESET_LOGS

Augur does provides an environment variable to control whether logs are reset on server startup. This gives system administrators more control over log management.

`AUGUR_RESET_LOGS` : This controls the automatic reset of logs when Augur starts.

- Default Behavior:  
  If the variable is not set, it defaults to True, meaning Augur will reset logs on startup to avoid infinite log growth.

- Custom Behavior:  
  If set to False (or any common variation), Augur will not reset logs. In this case, the sysadmin is responsible for managing log growth.  

- Usage Example:
  ```bash
  export AUGUR_RESET_LOGS=False
  ```