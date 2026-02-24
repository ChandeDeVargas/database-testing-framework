# Database Testing Framework

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-60+-informational?style=for-the-badge)

> Professional database testing framework - Data integrity, quality, and performance

---

## 🎯 Project Overview

Comprehensive database testing suite demonstrating advanced SQL skills, data quality assurance, and performance optimization. This project showcases expertise in database testing - a rare and highly valuable QA skill.

**Database Support:** SQLite, PostgreSQL, MySQL  
**Tests:** 60+ automated database tests  
**Coverage:** Integrity, Quality, Performance, Schema

---

## 📊 Quick Results

| Category          | Tests  | Status   | Key Metrics          |
| ----------------- | ------ | -------- | -------------------- |
| Basic Operations  | 8      | ✅       | CRUD validated       |
| Data Integrity    | 13     | ✅       | 0 orphaned records   |
| Data Quality      | 16     | ✅       | RFC email validation |
| Query Performance | 12     | ✅       | <10ms queries        |
| Schema Validation | 8      | ✅       | Structure verified   |
| Test Factories    | 7      | ✅       | Data generation      |
| **TOTAL**         | **64** | **100%** | **Production-ready** |

---

## 🗂️ Project Structure

```
database-testing-framework/
├── tests/
│   ├── test_basic_operations.py       # CRUD operations
│   ├── integration/
│   │   └── test_data_integrity.py     # Foreign keys, constraints
│   ├── data_quality/
│   │   ├── test_email_validation.py   # Email quality checks
│   │   ├── test_duplicates.py         # Duplicate detection
│   │   └── test_value_ranges.py       # Range validation
│   ├── performance/
│   │   └── test_query_speed.py        # Performance & optimization
│   ├── test_schema_validation.py      # Schema structure
│   └── test_factories.py              # Factory testing
├── config/
│   ├── database.py                    # Multi-DB support
│   └── models.py                      # ORM models
├── fixtures/
│   └── factories.py                   # Test data factories
├── db/                                # SQLite database files
├── reports/                           # Test reports
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/ChandeDeVargas/database-testing-framework.git
cd database-testing-framework

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running Tests

### Run All Tests

```bash
pytest tests/ -v -s
```

### Run by Category

```bash
# Basic operations
pytest tests/test_basic_operations.py -v -s

# Data integrity
pytest tests/integration/ -v -s

# Data quality
pytest tests/data_quality/ -v -s

# Performance
pytest tests/performance/ -v -s

# Schema validation
pytest tests/test_schema_validation.py -v -s
```

---

## 📊 Test Coverage

### 1. Basic Operations (8 tests)

- Database connectivity
- CRUD operations (Create, Read, Update, Delete)
- Query filtering
- Record counting

### 2. Data Integrity (13 tests)

**Referential Integrity:**

- Orphaned records detection
- Foreign key constraint enforcement
- Cascade delete behavior

**Constraint Validation:**

- UNIQUE constraints (email, SKU)
- NOT NULL constraints
- Foreign key violations

**Data Consistency:**

- Order totals match item sums
- Stock levels validation
- Price validation

**Result:** 0 orphaned records, all constraints enforced

---

### 3. Data Quality (16 tests)

**Email Validation:**

- @ symbol presence
- Domain structure validation
- RFC 5322 compliance
- Suspicious pattern detection
- Case consistency

**Duplicate Detection:**

- Duplicate emails (case-insensitive)
- Duplicate SKUs
- Duplicate orders detection

**Value Range Validation:**

- Age ranges (0-120 years)
- Price ranges ($0.01-$1M)
- Stock quantities (0-100k)
- Future timestamp detection
- Order status enum validation

**Result:** 100% RFC-compliant emails, 0 duplicates

---

### 4. Query Performance (12 tests)

**Performance Metrics:**

- Simple SELECT: 6.67ms (SLA: 100ms) ✅
- JOIN queries: 7.03ms (SLA: 500ms) ✅
- Aggregations: 10.31ms (SLA: 1000ms) ✅
- Bulk insert (100 records): 46.41ms ✅

**Optimizations Measured:**

- SELECT specific columns: 58.2% faster than SELECT \*
- EXISTS: 76.8% faster than COUNT(\*)
- Batch updates: 72.0% faster than individual

**N+1 Query Detection:**

- Lazy loading: 10 queries
- Eager loading: 1 query
- Issue successfully detected ✅

**Connection Management:**

- No connection leaks
- 10 concurrent connections: 36.88ms

---

### 5. Schema Validation (8 tests)

- Table existence validation
- Column type validation
- Foreign key documentation
- Unique constraint verification
- Primary key validation
- Column count stability
- Unexpected table detection

---

### 6. Test Data Factories (7 tests)

**Professional test data generation:**

- UserFactory (with variants: minor, senior, inactive)
- ProductFactory (out-of-stock, expensive, cheap)
- OrderFactory (pending, completed, with items)
- ScenarioFactory (complete customer scenarios)

**Benefits:**

- Consistent test data
- Realistic relationships
- Easy customization
- Better than Faker alone

---

## 🛠️ What This Project Demonstrates

### Database Testing Skills

- ✅ **SQL Expertise** - Complex queries, JOINs, aggregations
- ✅ **Data Integrity** - Foreign keys, constraints, referential integrity
- ✅ **Data Quality** - Email validation, duplicate detection, range checking
- ✅ **Performance Testing** - Query optimization, N+1 detection
- ✅ **Schema Validation** - Structure verification, migration testing
- ✅ **Test Data Management** - Professional factory pattern

### Technical Skills

- ✅ **Python** - Advanced OOP, fixtures, context managers
- ✅ **SQLAlchemy** - ORM, raw SQL, multi-database support
- ✅ **Pytest** - Fixtures, markers, parameterization
- ✅ **Database Design** - Normalization, relationships, constraints
- ✅ **Performance Analysis** - Query timing, optimization strategies

### Professional Practices

- ✅ **Test Automation** - 64 automated tests
- ✅ **Code Organization** - Modular, maintainable structure
- ✅ **Documentation** - Comprehensive comments and docstrings
- ✅ **Version Control** - Git workflow with meaningful commits
- ✅ **Multi-Database Support** - SQLite, PostgreSQL, MySQL

---

## 📈 Performance Benchmarks

```
Query Type              Time      SLA       Status
─────────────────────────────────────────────────
Simple SELECT          6.67ms    100ms     ✅ 93% under
JOIN                   7.03ms    500ms     ✅ 98% under
Aggregation           10.31ms   1000ms     ✅ 99% under
Bulk Insert (100)     46.41ms      -       ✅ Efficient
Pagination            <10ms        -       ✅ Stable

Optimizations:
SELECT specific        58.2% faster than SELECT *
EXISTS                 76.8% faster than COUNT(*)
Batch updates          72.0% faster than individual
```

---

## 🎯 Real-World Applications

### Banking/Fintech

- Transaction integrity validation
- Account balance consistency checks
- Audit trail completeness
- Regulatory compliance testing

### E-commerce

- Inventory accuracy
- Order total validation
- Product duplicate detection
- Customer data quality

### Healthcare

- Patient record integrity
- Duplicate patient detection
- Data privacy compliance
- Referential integrity (appointments, prescriptions)

---

## 🔧 Configuration

### Multi-Database Support

```python
# SQLite (default - local file)
db = DatabaseConfig('sqlite')

# PostgreSQL (production)
db = DatabaseConfig('postgresql')

# MySQL (production)
db = DatabaseConfig('mysql')
```

### Custom Configuration

Edit `config/database.py` to customize connection strings, pool sizes, and other database settings.

---

## 📚 Documentation

Each test file contains:

- Detailed docstrings explaining purpose
- Business impact analysis
- Real-world scenarios
- Expected vs actual behavior
- Fix recommendations

Example:

```python
def test_order_total_matches_items_sum(self):
    """
    Test: Order total equals sum of (quantity * price)

    Business Rule: Financial accuracy
    Risk: Revenue leakage if totals are wrong

    This test prevents:
    - Undercharging customers (revenue loss)
    - Overcharging customers (refunds, disputes)
    - Accounting discrepancies
    """
```

---

## 💡 Usage Examples

### Using Factories

```python
from fixtures.factories import UserFactory, OrderFactory

# Create single user
user = UserFactory.create(age=25)

# Create batch
users = UserFactory.create_batch(10)

# Create complete scenario
scenario = ScenarioFactory.create_customer_with_orders(db_session)
```

### Running Performance Tests

```python
# Measure query performance
pytest tests/performance/ -v -s

# Check for N+1 queries
pytest tests/performance/ -k "n_plus_one" -v -s
```

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

---

## 📄 License

MIT License - Free to use as reference or template

---

## 👤 Author

**Chande De Vargas**

- GitHub: [@ChandeDeVargas](https://github.com/ChandeDeVargas)
- LinkedIn: [Chande De Vargas](https://www.linkedin.com/in/chande-de-vargas-b8a51838a/)
- Role: QA Automation Engineer | Database Testing Specialist

---

## 🙏 Acknowledgments

- **SQLAlchemy Team** - Excellent ORM framework
- **Pytest Team** - Best testing framework
- **Faker** - Realistic test data generation

---

## 📚 Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Database Testing Best Practices](https://www.guru99.com/data-testing.html)

---

**⭐ If this project helped you learn database testing, please star it!**

**🗄️ Database testing is a rare and valuable skill - master it!**
