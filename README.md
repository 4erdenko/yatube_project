# Yatube: A Social Network for Bloggers

Yatube is a Django-based social network for bloggers, where users can create personal diaries, follow other authors, and comment on their posts. The project is designed with simplicity and usability in mind, allowing users to easily navigate and interact with the platform.

## Features

- User registration and profile creation
- Personalized author pages displaying all posts
- Following other authors and viewing their content
- Commenting on posts
- Unique username and address selection during registration
- Basic text formatting for a clean and simple post appearance
- Community groups for browsing various authors' content
- Admin interface for moderating posts and blocking users

## Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/yatube.git
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Configure your database settings in `yatube/settings.py`.

4. Run migrations:

```
python manage.py migrate
```

5. Start the development server:

```
python manage.py runserver
```

Now you can access the Yatube web application at `http://127.0.0.1:8000/`.

## Models

Yatube consists of four main models: `Group`, `Post`, `Comment`, and `Follow`.

### Group

The `Group` model represents a community where users can share their posts. Each group has a unique slug and a description.

### Post

The `Post` model represents a user's diary entry. Posts contain text, a publication date, an author, an optional group, and an optional image. Posts are ordered by publication date in descending order.

### Comment

The `Comment` model allows users to leave comments on posts. Each comment is linked to a post and an author, and has a publication date.

### Follow

The `Follow` model represents the relationship between users and the authors they follow. A unique constraint ensures that each user can follow an author only once.

## Future improvements

- Encourage and reward top authors
- Improve spam and bot prevention
- Implement a more customizable design
- Add additional social features, such as likes and shares

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
