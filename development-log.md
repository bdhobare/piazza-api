# Development Log
## Nov 17
- Initial project boostrap.
- Layout determined
- Initial README entries
- Initial requirements,gitignore & dockerignore files
- Sources: Wek 5&6 Course material

## Nov 19
- In additiont to access_token, successful login should also return refresh_token and expires_at
- Database should be read from the volume rather than known file path
- Hash password before storing it
- Foreign keys in mathing posts/comments/reactions to users
- Topics will be prepopulated in the database because they are fixed
- created_at: Unix timestamp, so that the caller can display it in the local timestamp, compared to sending it in server's timestamp
- post status stored as an int to save space, then int enum used to decode it to string for clients
- No reactions on comments themselves
- Stripped down details of a user to be appended in Posts and Comments responses: UserSimple
- Seeding the default topics during application startup if they don't already exist in the DB, Can we feed this through the config file?  raise the same exception to terminate startup if issues seeding
- One-to-Many (e.g., User → Posts) foreign key
- we store topics as actual values to reduce query times by avoiding joining
-  increase or decrease this like and dislike counts in a transction but store value in posts table to reduce joins
- likes & dislikes tables: Ensure a combination of author_id x post_id is unique by marking the two fields as primary keys

## Nov 21
- Remove topic strings from posts table: we can retrieve the strings when fetching data. This allow us to normalize the data better and avoid wrong id-name matching of topics.
- Send topics as a list of strings, validation happens on server before inserting into post->topics table.
- Topic and status can be passed as optionals query params: /posts?topic=Tech&status=1
- TODO: Add returning of comments with posts

##  Nov 23/24
- Implemented the put reaction endpoint.
- When putting a reactinon, also update the status of the post if it has expired, making next checks faster.
- We store reaction value as  "like"/"dislike".
- We add a constraint to prevent invalid values from being inserted into the database
- Add updated_at to the reaction table to track when the reaction was made/updated

## Nov 25
- Unify all timestamps in UTC
- Fix missing filtering logic on status in GET /posts endpoint
- Change the post status to string to make comparison and API uniform
- Fix missing check to block authors reacting to their posts
- Change timestamps from Unix to AwareDateTime to store all timestamps in UTC

## Nov 25
- Add most-liked endpoint
- Remove the UserSimple class and use UserResponse directly. This is to reduce the data manipulation needed after query responses.
- 
