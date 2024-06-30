# Web Scraping and Analysis Service

This project implements a distributed web scraping and analysis service using RabbitMQ, TypeScript (for the producer), and Python (for the consumer). It captures screenshots of websites, analyzes them using OpenAI's GPT-4 Vision model, and stores the results in a PostgreSQL database.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Components](#components)
3. [Prerequisites](#prerequisites)
4. [Setup](#setup)
5. [Usage](#usage)
6. [Architecture](#architecture)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [License](#license)

## Project Overview

This service automates the process of capturing website screenshots, extracting information from these images using AI, and storing the analysis results. It's designed to be scalable and can handle a large number of URLs efficiently.

## Components

- **Producer (TypeScript)**: Captures screenshots of websites and sends them to a RabbitMQ queue.
- **Consumer (Python)**: Processes screenshots from the queue, analyzes them using OpenAI's GPT-4 Vision API, and stores results in a PostgreSQL database.
- **RabbitMQ**: Message broker for coordinating work between the producer and consumer.
- **PostgreSQL**: Database for storing analysis results.

## Prerequisites

- Node.js and npm
- Python 3.7+
- RabbitMQ
- PostgreSQL
- OpenAI API key

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/web-scraping-analysis-service.git
   cd web-scraping-analysis-service
   ```

2. **Set up the producer:**
   ```bash
   cd producer
   npm install
   ```

3. **Set up the consumer:**
   ```bash
   cd ../consumer
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Create a PostgreSQL database
   - Run the SQL script to create the necessary table:
     ```sql
     CREATE TABLE website_analyses (
         id SERIAL PRIMARY KEY,
         url TEXT NOT NULL,
         analysis JSONB NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );
     ```

5. **Configure environment variables:**
   Create a `.env` file in both the producer and consumer directories with the following contents:
   ```
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=localhost
   DB_PORT=5432
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. **Start RabbitMQ:**
   Ensure RabbitMQ is running on your system.

2. **Run the producer:**
   ```bash
   cd producer
   npm start
   ```

3. **Run the consumer:**
   ```bash
   cd consumer
   python consumer.py
   ```

4. **Add URLs to process:**
   Use the provided script to add URLs to the queue:
   ```bash
   python add_urls.py
   ```

## Architecture

```
[Producer (TS)] --> [RabbitMQ] --> [Consumer (Python)] --> [PostgreSQL]
     |                                       |
     v                                       v
[Website Screenshots]                 [OpenAI GPT-4 Vision API]
```

## Troubleshooting

- Ensure all environment variables are correctly set.
- Check RabbitMQ and PostgreSQL logs for any connection issues.
- Verify that the OpenAI API key is valid and has sufficient credits.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Getting Started

For first-time users, follow these steps to get the project up and running:

1. **Install Dependencies:**
   - Ensure you have Node.js, Python, RabbitMQ, and PostgreSQL installed on your system.
   - Install the required Node.js packages:
     ```bash
     cd producer
     npm install
     ```
   - Install the required Python packages:
     ```bash
     cd consumer
     pip install -r requirements.txt
     ```

2. **Set Up the Database:**
   - Create a new PostgreSQL database for the project.
   - Use the provided SQL script to create the necessary table.

3. **Configure Environment:**
   - Create `.env` files in both the producer and consumer directories.
   - Add all required environment variables as listed in the Setup section.

4. **Start the Services:**
   - Start RabbitMQ (the method depends on your installation).
   - Run the producer: `npm start` in the producer directory.
   - Run the consumer: `python consumer.py` in the consumer directory.

5. **Add URLs:**
   - Use the `add_urls.py` script to add some test URLs to the queue.

6. **Monitor the Process:**
   - Watch the console output of both the producer and consumer.
   - Check the PostgreSQL database for incoming results.

## Example Output

Here's an example of what the analysis output might look like:

```json
{
  "url": "https://example.com",
  "analysis": {
    "main_content": "Welcome to Example.com",
    "key_features": ["Simple design", "Clear navigation", "Informative content"],
    "improvement_suggestions": [
      "Add a call-to-action button",
      "Implement a responsive design",
      "Include more visual elements"
    ]
  }
}
```

## Scaling for Production

To scale this system for production use:

1. **Containerization:** Use Docker to containerize each component.
2. **Load Balancing:** Implement a load balancer for multiple producer and consumer instances.
3. **Database Optimization:** Consider database sharding or read replicas for high traffic.
4. **Monitoring:** Implement comprehensive monitoring and alerting systems.
5. **Error Handling:** Enhance error handling and implement a dead-letter queue for failed jobs.

## Limitations and Future Improvements

- Currently limited by OpenAI API rate limits and costs.
- Could implement caching to avoid re-analyzing recently processed URLs.
- Potential for adding more diverse analysis models or services.

## How to Contribute

1. Fork the repository.
2. Create a new branch for your feature: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

Please adhere to the project's coding standards and include tests for new features.