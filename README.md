# Stanford Scheduler Backend

A Flask-based backend service for managing and generating academic schedules for Stanford programs. This service provides APIs for program management, profile management, and automated schedule generation based on course requirements and constraints.

## Features

- **Program Management**: Create and manage academic programs with required courses
- **Profile Management**: Handle student profiles and preferences
- **Schedule Generation**: Automatically generate optimal course schedules based on:
  - Course prerequisites
  - Quarter availability
  - Program requirements
  - Student preferences
- **MongoDB Integration**: Persistent storage for programs and profiles
- **CORS Enabled**: Ready for frontend integration

## Prerequisites

- Python 3.x
- MongoDB
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StanfordSchedulerBackend.git
cd StanfordSchedulerBackend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
   - Create an `appsettings.json` file in the root directory
   - Add your MongoDB connection string:
```json
{
    "DatabaseConnection": {
        "ConnectionString": "your_mongodb_connection_string"
    }
}
```

## API Endpoints

### Schedule Generation
- `POST /solve-user-schedule`
  - Generates a schedule based on program and profile IDs
  - Request body: `{"program": "program_id", "profile": "profile_id"}`

### Program Management
- `POST /post-program`
  - Creates a new program
- `POST /post-program-course`
  - Adds a course to an existing program
- `POST /post-prereq-course`
  - Adds prerequisites to a program course

### Profile Management
- `POST /post-profile`
  - Creates a new student profile

## Development

The backend is structured with the following main components:
- `src/controller.py`: Main Flask application and API endpoints
- `src/classes/`: Core business logic and data models
  - `constrain/`: Schedule generation logic
  - `components/`: Data models for courses and other entities

## Running the Application

1. Start the Flask server:
```bash
python src/controller.py
```

The server will start in debug mode on the default port (5000).

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Stanford University for academic program information
- Flask framework and its contributors
- MongoDB team for the database solution
