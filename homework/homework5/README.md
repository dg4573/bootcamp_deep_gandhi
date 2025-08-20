# Section 05: Data Storage 

### Folder Structure:
homework5/
├── data/
│ ├── raw/ 
│ └── processed/ 
└── notebooks/ 

### Formats
- **CSV**: human-readable, good for quick inspection and sharing.  
- **Parquet**: efficient, compressed, preserves dtypes, faster for large datasets.  

### `.env` file has:
DATA_RAW= path/to/data/raw
DATA_PROCESSED= path/to/data/processed