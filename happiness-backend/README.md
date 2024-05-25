# Happiness App Backend

The Happiness App backend is built using Python, Flask, and SQLAlchemy.

## API Modules

Below is a high level overview of the Happiness App API. For more information, access the interactive API playground [here](https://happiness-app-backend.herokuapp.com/docs).

### User

Provides user related functionality, such as:

- Registering new users
- Fetching user profiles
- Deleting users
- Adding and deleting user settings (profile picture, email, username, reminder emails, etc)
- Resetting user passwords

### Groups

Provides functionality for happiness groups, such as:

- Creating/deleting groups
- Sending and managing group invites
- Fetching group information
- Fetching all the happiness entries in a group
- Fetching all the unread happiness entries in a group

### Happiness

Provides functionality for keeping track of happiness, such as:

- Creating new happiness entries
- Editing/deleting happiness entries
- Fetching user happiness entries based on a date range or pagination
- Adding user comments to happiness entries
- Searching happiness entries with filters
- Exporting happiness entries to a CSV file

### Reads

Provides functionality for the reads system, such as:

- Marking happiness entries as read or unread
- Get all the unread happiness entries for a user 

### Journal

Provides functionality for private happiness entries, such as:

- Requesting a user's decryption key
- Creating and editing journal entries
- Fetching journal entries based on a date range or pagination

### Token

Provides functionality for user authentication, such as:

- Creating and revoking API access tokens

## Authentication

Besides the token creation endpoint, which requires basic authentication, all other endpoints
require access token based authentication.

A token can be acquired by sending a `POST` request to the `/api/tokens` endpoint,
passing the username and password of according to Basic Authentication scheme.
The access token is included in the response body.

To access API endpoints, the access token should be passed in using the Bearer Authentication
scheme.

If API endpoints are accessed with an expired or missing access token, a `401` status code will be
sent.