# factaday - one new fact a day
A Simple Python and FastAPI webapp using generative AI to generate one new fact every day from a variety of topics.

## Setup & Installation

### 1) Clone the repo

```bash
git clone https://github.com/JeppesS1423/factaday.git
cd factaday
```

### 2) Get an Anthropic API key
If you do not already have one ready, navigate to https://platform.claude.com/settings/keys and create a new key.

### 3) Create `.env`
Copy the example or create your own:

```.env
ANTHROPIC_API_KEY=your-api-key-here
DATABASE_PATH=./data
```

This directory will be mounted by Docker for persistence.

## Starting the App

### Using Docker Compose

```bash
docker-compose up --build
```

The app will be available at:

```
http://localhost:8000
```

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

Created by Jesper H @ JeppesS1423
