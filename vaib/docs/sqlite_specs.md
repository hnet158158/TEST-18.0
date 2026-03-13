# SQLite Documentation

## Overview

SQLite is an open-source, zero-configuration, self-contained, stand-alone, transaction relational database engine designed to be embedded into an application.

SQLite is an in-process library that implements a self-contained, serverless, zero-configuration, transactional SQL database engine. The code for SQLite is in the public domain and is thus free for use for any purpose, commercial or private.

SQLite is the most extensively deployed SQL database engine in the world, the most used database in mobile applications, and an integral component in countless other applications.

## Key Features

* Self-contained: No need for a separate server process or operating system.
* Zero-configuration: No setup or administration needed.
* Stand-alone: No external dependencies.
* Cross-platform: Available on all major operating systems.
* Small footprint: Compact library size.
* Fast: Highly optimized for performance.
* Reliable: ACID-compliant with transaction support.
* Flexible: Dynamic typing system.

## Basic SQL Statements

### Simple Query
* SELECT – query data from a single table using SELECT statement.

### Sorting Rows
* ORDER BY – sort the result set in ascending or descending order.

### Filtering Data
* DISTINCT – query unique rows from a table using the DISTINCT clause.
* WHERE – filter rows of a result set using various conditions.
* AND – filter rows by combining multiple conditions.
* OR – combine multiple conditions and filter rows based on at least a specified condition being true.
* LIMIT – constrain the number of rows a query returns.
* BETWEEN – test whether a value is in a range of values.
* IN – check if a value matches any value in a list of values or subquery.
* LIKE – query data based on pattern matching using wildcard characters: percent sign (%) and underscore (_).
* GLOB – determine whether a string matches a specific UNIX pattern.
* IS NULL – check if a value is null or not.

### Joining Tables
* INNER JOIN – query data from multiple tables using the inner join clause.
* LEFT JOIN – combine data from multiple tables using the left join clause.
* RIGHT JOIN – combine rows from two tables based on a related column.
* CROSS JOIN – use the cross join clause to produce a cartesian product of result sets of the tables involved in the join.
* SELF JOIN – join a table with itself to create a result set that joins rows with other rows within the same table.
* FULL OUTER JOIN – use the full outer join in SQLite.

### Grouping Data
* GROUP BY – combine a set of rows into groups based on specified criteria. The GROUP BY clause helps you summarize data for reporting purposes.
* HAVING – specify the conditions to filter the groups summarized by the GROUP BY clause.

### Set Operators
* UNION – combine result sets of multiple queries into a single result set. Differences between UNION and UNION ALL clauses.
* EXCEPT – compare the result sets of two queries and return distinct rows from the left query that are not output by the right query.
* INTERSECT – compare the result sets of two queries and returns distinct rows that are output by both queries.

### Subquery & CTE
* Subquery – introduction to SQLite subquery and correlated subquery.
* EXISTS operator – test for the existence of rows returned by a subquery.
* Common Table Expressions (CTE) – use CTEs to simplify your queries and make them more readable.

### Changing Data
* INSERT – insert rows into a table.
* UPDATE – update existing rows in a table.
* DELETE – delete rows from a table.
* REPLACE – insert a new row or replace the existing row in a table.
* UPSERT – perform an insert if the row does not exist or update otherwise.
* RETURNING clause – return the inserted, updated, and deleted rows.

### Transactions
* TRANSACTION – handle transactions in SQLite.

## Data Definition

### Data Types
SQLite supports a dynamic type system with storage classes and type affinities:
* NULL - The value is a NULL value.
* INTEGER - The value is a signed integer.
* REAL - The value is a floating-point number.
* TEXT - The value is a text string.
* BLOB - The value is a blob of data.

### Table Operations
* CREATE TABLE – create a new table in the database.
* ALTER TABLE – modify the structure of an existing table.
* RENAME COLUMN – rename a column of a table.
* DROP TABLE – remove a table from the database.
* VACUUM – optimize database files.

### Constraints
* PRIMARY KEY – define the primary key for a table.
* NOT NULL constraint – enforce values of columns that are not NULL.
* UNIQUE constraint – ensure values in a column or a group of columns are unique.
* CHECK constraint – ensure the values in a column meet a specified condition defined by an expression.
* AUTOINCREMENT – explains how the AUTOINCREMENT column attribute works.

### Views
* CREATE VIEW – create a new view in the database.
* DROP VIEW – drop a view from its database schema.

### Indexes
* INDEX – utilize indexes to speed up your queries.
* EXPRESSION INDEX – use expression-based index.

### Triggers
* TRIGGER – manage triggers in the SQLite database.
* INSTEAD OF triggers – create INSTEAD OF triggers to update data via a view.

## Full-Text Search
* FTS (Full-Text Search) – get started with the full-text search in SQLite.

## SQLite Tools

### Command Line Interface
* SQLite Commands – commonly used commands in the sqlite3 program.
* SHOW TABLES – list all tables in a database.
* DESCRIBE TABLE – show the structure of a table.
* DUMP – use the .dump command to back up and restore a database.
* IMPORT CSV – import CSV files into a table.
* EXPORT CSV – export an SQLite database to CSV files.

## Programming Interface

SQLite provides a C/C++ API for embedding the database engine in applications. The API includes functions for:
* Opening and closing database connections
* Preparing and executing SQL statements
* Binding parameters to SQL statements
* Retrieving results from queries
* Managing transactions
* Handling errors

## Concurrency and Locking

SQLite uses file-based locking mechanisms to handle concurrent access:
* Multiple readers can access the database simultaneously
* Only one writer can access the database at a time
* Supports WAL (Write-Ahead Logging) mode for improved concurrency
* Shared cache mode allows multiple connections in the same process to share data

## Performance Features

* Memory-mapped I/O for faster access
* Query optimizer with cost-based analysis
* Various pragma settings for performance tuning
* Indexes for accelerating queries
* Efficient B-tree storage engine