# Smart City Issue Reporting System

A multi-database prototype platform that allows citizens to report 
urban issues such as waste, lighting, and traffic. The system 
integrates four NoSQL database types to handle different data needs.

## Features
- Citizen registration and issue reporting
- Issue status tracking and updates
- Urban network relationships between citizens, departments and locations
- Analytics on most reported issues, busiest areas and response times
- Caching layer for active sessions and frequently accessed data

## Tech Stack
- **MongoDB** — citizen profiles and service requests
- **Redis** — caching layer for sessions and active data
- **Neo4j** — relationships between citizens, services and locations
- **InfluxDB** — time-series analytics and response time tracking
- **Streamlit** — web interface and dashboard
- **Docker** — containerized deployment
