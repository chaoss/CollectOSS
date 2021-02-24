# augurface

## Project setup
From the augur root directory, you need to configure a local server that points to the database you want to add repositories to, which will typically be remote. You then need to rebuild development: 

```
make rebuild-dev
```

You then need to edit the `frontend.config.json` so that it points this frontend to the server running on a remote machine where you want to add repositories. The changes are in the server block of the config file, and will include the hostname, and the port the Augur backend is running on.

From this directory, you need to:

```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
