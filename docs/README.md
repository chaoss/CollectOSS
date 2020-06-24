# Getting Started with Docs

1. Directory for source files: `augur/docs/source`
2. Each branch has itself published on readthedocs.io
	- Master: https://oss-augur.readthedocs.io/en/master/ 
	- Dev: https://oss-augur.readthedocs.io/en/dev/
3. Syntax reference for restructred text, which is what readthedocs.io uses: https://docutils.sourceforge.io/docs/user/rst/quickref.html 
4. Best way to figure out how things are structure is to look in the source folder under docs
	- Each directory has a `toc.rst` file that is a table of contents
	- There are configuration steps on each branch so the docs are built there if that's what you are working on.
	- There is also a way to build locally, but Sean doesn't know what it is. 