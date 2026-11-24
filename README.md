
# StockFlow - Inventory Management System

StockFlow is a desktop inventory management application built
with Python, Tkinter, and SQLite. It allows users to manage
products, monitor stock levels, and track inventory value
through a graphical user interface.

## Features

- Add, view, edit, and delete products
- Real-time inventory dashboard
- Live product search
- Category-based filtering
- Automatic low-stock alerts
- Color-coded inventory table
- Total inventory value calculation
- Persistent SQLite database storage
- Input validation and error handling
- Deletion confirmation
- Command-line interface

## Technologies Used

- Python
- SQLite
- SQL
- Tkinter
- Git and GitHub

## Installation

1. Clone or download this repository.
2. Ensure Python 3 is installed.
3. Open the project folder in your terminal.
4. Run the application:

```bash
python gui.py
```

The SQLite database will be created automatically.

No additional third-party Python packages are required.

## Command-Line Version

To run the terminal-based application:

```bash
python main.py
```

## Project Structure

| File | Description |
|------|-------------|
| database.py | Database initialization |
| inventory.py | Inventory management functions |
| main.py | Command-line application |
| gui.py | Graphical user interface |
| inventory.db | Automatically generated SQLite database |

## Database Design

The products table stores:

- Product ID
- Product name
- Category
- Quantity
- Unit price
- Supplier

## Skills Demonstrated

- Python programming
- SQL database management
- CRUD operations
- Graphical user interface development
- Event-driven programming
- Exception handling
- Input validation
- Data persistence
- Modular programming

## Future Improvements

- CSV and Excel export
- Inventory analytics and visualization
- Stock transaction history
- Supplier management
- User authentication
- Barcode integration
- Automated testing

## Author

Developed by a Computer Science and Engineering student
at The Ohio State University.