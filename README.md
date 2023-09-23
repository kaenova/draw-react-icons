# draw-react-icons

![System Flow](docs/flow.png)

# Objective

Create a react-icons alternative website to be able search an icon by drawing on the web

# TODO

- [x] Generate image from react icons to be processed as embedding  
~~[ ] Search lightweight model to be runned on Github Action and Vercel~~  
~~- [ ] Convert into tf.js to be deployed in Vercel~~  
- [x] Create schedule to update icon embedding
  - [x] Create Github Action with Cron that run a python program to update database
  - [x] Smart update (don't update available icon, only update icon that isn't in the database)
- [x] Create website to draw, and send it to Vercel for draw embedding and checked into database
- [ ] Change Database to self hosted using https://qdrant.tech/
