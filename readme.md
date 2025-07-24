# Django Image Sharing API

Tiny Django + DRF backend (SQLite) for a simple image‑sharing app with captions, follows, likes, and personalized feeds.

---

## Quick Setup

1. **Clone the repo & activate a virtual env**

   ```bash
   git clone <repo-url>
   cd django-image-sharing-api
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies & run migrations**

   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   ```

3. **Seed demo data (optional)**

   ```bash
   python manage.py setup_demo_data   # creates demo users, posts, follows, likes fileciteturn18file19
   ```

4. **Start the dev server**

   ```bash
   python manage.py runserver  # http://127.0.0.1:8000/
   ```

---

## Management Commands

List and inspect all custom management commands:

```bash
# List all command scripts
find . -path "*/management/commands/*.py" ! -name "__init__.py" \
  -exec basename {} .py \;

# Show help/usage for each
python manage.py help <command_name>
```

### Run individually

```bash
python manage.py create_test_users      # create 5 test users (testuser1..testuser5)
python manage.py create_test_posts      # generate 10 dummy posts by those users
python manage.py create_test_follows    # establish 9 follow relationships among test users
python manage.py create_test_likes      # add 17 like relationships to posts
python manage.py setup_demo_data        # seed full demo dataset (users, posts, follows, likes)
```

Available commands:

- `create_test_users` — Generate a set of 5 test users for integration testing.
- `create_test_posts` — Create 10 dummy posts linked to test users.
- `create_test_follows` — Populate 9 follow relationships among test users.
- `create_test_likes` — Add 17 likes to existing posts by test users.
- `setup_demo_data` — Seed a complete demo dataset (users, posts, follows, likes).

---

## Tests

Run automated tests to verify functionality:

```bash
# Run all tests (14 total)
python manage.py test -v2        # 14 passing tests

# Run individual test modules
python manage.py test users/test_views.py
python manage.py test posts/test_views.py
python manage.py test social/test_views.py

# Run a single test class
python manage.py test posts.test_views.PopularPostsTests -v2
```

**Test coverage:**

- **users/test_views.py** — registration, login/logout, profile, user listing (5 tests) fileciteturn18file18
- **posts/test_views.py** — post CRUD, my‑posts, popular ordering (6 tests) fileciteturn18file18
- **social/test_views.py** — follow/unfollow, like/unlike, feed retrieval (3 tests) fileciteturn18file18

---

## API Endpoints

All routes are prefixed with `/api/v1` and use Token authentication:

| Functionality     | Method & Path                        | Description                                              |
| ----------------- | ------------------------------------ | -------------------------------------------------------- |
| **Register**      | `POST /users/register/`              | Create a new user                                        |
| **Login**         | `POST /users/login/`                 | Obtain auth token                                        |
| **List Users**    | `GET /users/`                        | All users (requires auth)                                |
| **Current User**  | `GET /users/me/`                     | Profile of authenticated user                            |
| **Create Post**   | `POST /posts/`                       | New image post                                           |
| **List Posts**    | `GET /posts/`                        | All posts (paginated)                                    |
| **My Posts**      | `GET /posts/my-posts/`               | Posts of authenticated user                              |
| **Popular Posts** | `GET /posts/popular/`                | Posts ordered by like count desc fileciteturn18file11 |
| **Follow User**   | `POST /social/follow/{user_id}/`     | Follow another user                                      |
| **Unfollow User** | `DELETE /social/unfollow/{user_id}/` | Remove follow                                            |
| **Like Post**     | `POST /social/like/{post_id}/`       | Like a post                                              |
| **Unlike Post**   | `DELETE /social/unlike/{post_id}/`   | Remove like                                              |
| **Personal Feed** | `GET /posts/`                        | Newest posts from followed users                         |

---

## Postman & cURL Usage

### Postman

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd django-image-sharing-api
   ```

2. **Import** the collection file into Postman:

   - In Postman, click **Import → File**
   - Select `postman_collections/image_sharing_api_v3.postman_collection.json`

3. **Select** the environment with:

   ```text
   base_url = http://127.0.0.1:8000/api/v1
   ```

4. **Run** **Login** to set your `{{token}}`
5. **Execute** any endpoint; all headers are pre‑configured

### cURL Examples

```bash
# Login → save token
BASE=http://127.0.0.1:8000/api/v1
TOKEN=$(curl -s -X POST $BASE/users/login/ -H "Content-Type: application/json" \
  -d '{"username":"alice_photos","password":"demopass123"}' | jq -r .token)

# Create a post
curl -X POST $BASE/posts/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"caption":"Sunset","image_url":"https://picsum.photos/400/400"}'

# Follow user 2
curl -X POST $BASE/social/follow/2/ -H "Authorization: Token $TOKEN"

# Like post 1
curl -X POST $BASE/social/like/1/ -H "Authorization: Token $TOKEN"

# View popular posts
curl -H "Authorization: Token $TOKEN" $BASE/posts/popular/
```

---

## Full Test & Demo Flow

1. **Migrate & seed** (optional)

   ```bash
   python manage.py migrate
   python manage.py setup_demo_data
   ```

2. **Run server** `python manage.py runserver`
3. **Login** via Postman or cURL → get token
4. **Test endpoints** (create posts, follow, like, feed) in Postman or via cURL
5. **Run automated tests** `python manage.py test -v2`

That’s it—your API is fully tested, documented, and ready to go!
