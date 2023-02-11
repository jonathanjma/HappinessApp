# Happiness App Backend

The Happiness App backend is built using Python, Flask, and SQLAlchemy.

## API Modules

Below is a high level overview of the Happiness App API

### User

Provides user related functionality, such as:

- Registering new users
- Fetching user profiles
- Deleting users
- Adding and deleting user settings

### Groups

Provides functionality for happiness groups, such as:

- Creating/deleting groups
- Adding/removing users
- Fetching group information
- Fetching a group's paginated happiness statistics

### Happiness

Provides functionality for keeping track of happiness, such as:

- Uploading new happiness data
- Editing/deleting happiness data
- Fetching user happiness via date range and pagination

### Token

Provides functionality for user authentication, such as:

- Creating and revoking access tokens
- Email verification
- Password reset

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