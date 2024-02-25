# Use an official Node runtime as a base image
FROM node:14

WORKDIR /app

COPY /app .

# Install any needed packages specified in package.json
RUN npm install

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run app.js when the container launches
CMD ["npm", "start"]