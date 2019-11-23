# Release Notes

## Next Dev to Master Push
1. Schema update script
2. Users may need to create a new virtualenv. Not sure why. I build master then switched to dev and it didn't work until I blew away my virtual environment and recreated it.
3. There are now 2 schema update scripts that I have added to the installer. We need to include a status check for the schema version. 
4. Need to make some notes about postgres configuration for performance on large sets of data
5. Frontend configuration block
```
    "Frontend": {
        "host": "0.0.0.0",
        "port": "5002"
    },
```

 
