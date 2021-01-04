# aseemsDB

A database that uses Recoll to index PDFs, using FastAPI. If you want to run this locally you have two options:

1) Use the docker deploy script available at https://github.com/aseem-keyal/aseemsDB-deploy to run aseemsDB inside a container (recommended)
2) If you're on linux, you can install the dependencies listed in the Dockerfile, configure recoll (this only takes a minute), and use `uvicorn main:app --reload` to run the app locally

For deploying to production (with a bunch of cool features like metrics and graphs, automated backups, nginx static file serving, clusters), follow the directions at https://github.com/aseem-keyal/aseemsDB-deploy.

Feel free to email me @ aseem.keyal@gmail.com if you need help with anything.
