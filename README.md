# GHData

This project aims to provide an interface to data related to GitHub repositories. This project requires the GHTorrent database. [Backups of this database are avaliable](http://ghtorrent.org/downloads.html) and [it can be synchronized with current data](https://github.com/OSSHealth/ghtorrent-sync). Support for all event types reported by the [GitHub Events API](https://developer.github.com/v3/activity/events/) are planned for the version 1.0.0 milestone.

To install development version: `pip install --upgrade git+git://github.com/OSSHealth/ghdata.git`

A MySQL installation is required. The GHTorrent database requires a large amount of disk space.