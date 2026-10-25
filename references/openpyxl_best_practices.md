# openpyxl Best Practices for Template Population

This document outlines the rules and best practices for populating pre-designed `.xlsx` templates using `openpyxl` without corrupting existing formulas, layouts, or functionality.

---

## Core Principles

1. **Preserve Template Integrity**: Never modify the template structure, only populate data
2. **Maintain Formulas**: Ensure all existing formulas continue to work after data injection
3. **Respect Layout**: Don't change cell formatting, merged cells, or named ranges
4. **No VBA**: Never use or modify VBA macros
5. **No Inline Styling**: Don't override existing cell styles programmatically

---

## Template Preservation Rules

### 1. Sheet Management

**DO:**
- Read all sheets from the template
- Navigate to specific sheets by name
- Preserve sheet order
- Keep hidden sheets hidden

**DON'T:**
- Delete or rename sheets
- Create new sheets unless specified
- Unhide hidden sheets
- Change sheet tab colors

### 2. Named Ranges

**DO:**
- Use named ranges for data cell identification
- Preserve all existing named ranges
- Reference named ranges in your code
- Document named ranges in template metadata

**DON'T:**
- Delete or rename named ranges
- Create new named ranges unless necessary
- Modify named range references

### 3. Cell Protection

**DO:**
- Respect locked cells (don't modify them)
- Only write to unlocked data cells
- Preserve cell protection settings

**DON'T:**
- Write to locked cells
- Change protection settings
- Unprotect the workbook/sheet

### 4. Formulas

**DO:**
- Preserve all existing formulas
- Ensure data injection doesn't break formula references
- Test formulas after data population
- Use named ranges to make formulas robust

**DON'T:**
- Overwrite cells containing formulas
- Modify formula logic
- Delete formula dependencies

---

## Data Injection Patterns

### 1. Cell Naming Conventions

Use a consistent naming convention for data cells:

**Prefix Convention:**
- `DATA_` prefix for all data input cells
- `PARAM_` prefix for parameter cells
- `CALC_` prefix for calculated cells (if any)

**Examples:**
- `DATA_REPORT_DATE` - Report date
- `DATA_TOTAL_SALES` - Total sales value
- `DATA_REGION` - Region name
- `PARAM_START_DATE` - Start date parameter
- `DATA_TABLE_START_ROW` - First row of data table

### 2. Data Type Validation

**Before injection:**
```python
# Validate data types
if not isinstance(value, (int, float, str, datetime)):
    raise ValueError(f"Invalid type for {cell_name}: {type(value)}")

# Check for None/missing values
if value is None:
    value = ""  # or appropriate default
```

**Numeric data:**
- Ensure numeric cells receive int or float
- Handle decimal precision appropriately
- Check for overflow (Excel's limit is ~1.797E+308)

**Date data:**
- Convert datetime objects to Excel date format
- Use `openpyxl.utils.datetime` utilities
- Preserve time zone information if needed

**String data:**
- Handle None values as empty strings
- Truncate if exceeding cell limits (32,767 chars)
- Handle special characters appropriately

### 3. Batch Update Operations

**For large datasets, use batch operations:**

```python
# Inefficient - one cell at a time
for row, data in enumerate(dataset, start=2):
    sheet[f'A{row}'].value = data['name']
    sheet[f'B{row}'].value = data['value']

# Efficient - batch assignment
for row, data in enumerate(dataset, start=2):
    sheet.cell(row=row, column=1, value=data['name'])
    sheet.cell(row=row, column=2, value=data['value'])
```

**For very large datasets, consider write_only mode:**
```python
from openpyxl import Workbook
wb = Workbook(write_only=True)
ws = wb.create_sheet()
ws.append(['Column1', 'Column2'])
for data in large_dataset:
    ws.append([data['col1'], data['col2']])
wb.save('output.xlsx')
```

### 4. Preserve Cell Formatting

**DON'T override existing styles:**
```python
# BAD - overrides formatting
cell.font = Font(bold=True)
cell.fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

# GOOD - preserve existing formatting
cell.value = new_value  # Only change the value
```

**If you need to format, use named styles:**
```python
# Define styles in the template
# Apply by name instead of inline
if cell.style != 'DataStyle':
    cell.style = 'DataStyle'
```

---

## Error Handling

### 1. Validation Before Injection

```python
def validate_data(data: dict, schema: dict) -> bool:
    """Validate data against schema before injection."""
    for field, expected_type in schema.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], expected_type):
            raise TypeError(f"Invalid type for {field}: expected {expected_type}")
    return True
```

### 2. Graceful Handling of Missing Values

```python
# Use defaults for missing data
value = data.get('field_name', default_value)

# Log warnings for missing optional fields
if 'optional_field' not in data:
    logger.warning(f"Optional field 'optional_field' missing")
```

### 3. Rollback on Error

```python
def populate_template(template_path: str, output_path: str, data: dict):
    """Populate template with rollback on error."""
    # Load template
    wb = load_workbook(template_path)

    try:
        # Populate data
        inject_data(wb, data)

        # Save to output
        wb.save(output_path)
        return True

    except Exception as e:
        logger.error(f"Failed to populate template: {e}")
        # Don't save corrupted file
        return False

    finally:
        wb.close()
```

### 4. Detailed Logging

```python
import logging

logger = logging.getLogger(__name__)

def inject_data(sheet, data):
    for cell_name, value in data.items():
        try:
            cell = sheet[cell_name]
            cell.value = value
            logger.debug(f"Set {cell_name} = {value}")
        except Exception as e:
            logger.error(f"Failed to set {cell_name}: {e}")
            raise
```

---

## Performance Best Practices

### 1. Minimize Cell Access

```python
# BAD - accesses cells multiple times
for i in range(1000):
    value = sheet[f'A{i}'].value * 2
    sheet[f'A{i}'].value = value

# GOOD - batch operations
for row in sheet.iter_rows(min_row=1, max_row=1000):
    for cell in row:
        if cell.column == 1:
            cell.value = cell.value * 2
```

### 2. Use iter_rows/iter_cols

```python
# Efficient iteration
for row in sheet.iter_rows(min_row=2, values_only=True):
    process_row(row)
```

### 3. Disable Calculations (if applicable)

```python
# For large datasets, disable automatic recalculation
wb = load_workbook(template_path)
wb.calculation = 'manual'
# ... populate data ...
wb.calculation = 'automatic'
```

### 4. Close Workbooks Properly

```python
wb = load_workbook(template_path)
try:
    # ... work ...
    wb.save(output_path)
finally:
    wb.close()  # Always close
```

---

## Testing Guidelines

### 1. Test Formula Integrity

After data injection:
1. Load the output file
2. Check that all formulas still return expected values
3. Verify no formula references are broken
4. Test with edge case data (empty, max values, special characters)

### 2. Test Layout Preservation

1. Verify merged cells remain merged
2. Check that cell formatting is unchanged
3. Ensure named ranges still exist
4. Validate print areas and page setup

### 3. Test Data Types

1. Inject various data types (numbers, dates, strings, booleans)
2. Verify data is correctly interpreted in Excel
3. Check for type conversion issues
4. Test with None/missing values

### 4. Test Edge Cases

1. Empty datasets
2. Single row datasets
3. Maximum row count (1,048,576 rows)
4. Maximum column count (16,384 columns)
5. Very long strings
6. Special characters and unicode

---

## Common Pitfalls

### 1. Overwriting Formulas

**Problem:** Writing data to cells that contain formulas.

**Solution:** Use named ranges to identify data-only cells. Never write to cells starting with "=".

### 2. Breaking Cell References

**Problem:** Inserting/deleting rows/columns breaks formula references.

**Solution:** Never insert or delete rows/columns. Only modify cell values.

### 3. Corrupting Named Ranges

**Problem:** Renaming or deleting cells that are part of named ranges.

**Solution:** Preserve all named ranges. Only modify values within named ranges.

### 4. Memory Issues with Large Files

**Problem:** Loading large Excel files consumes excessive memory.

**Solution:** Use `read_only=True` for reading large files, `write_only=True` for writing.

### 5. Date/Time Format Issues

**Problem:** Dates are not displayed correctly after injection.

**Solution:** Use `openpyxl.utils.datetime` utilities and preserve cell number formats.

---

## Example Code Pattern

```python
from openpyxl import load_workbook
from openpyxl.utils.datetime import datetime_to_excel
import logging

logger = logging.getLogger(__name__)

def populate_report_template(template_path: str, output_path: str, data: dict):
    """
    Populate a report template with data.

    Args:
        template_path: Path to the template Excel file
        output_path: Path where the populated file will be saved
        data: Dictionary mapping cell names to values
    """
    logger.info(f"Loading template: {template_path}")
    wb = load_workbook(template_path)

    try:
        sheet = wb.active

        # Inject data using named ranges
        for cell_name, value in data.items():
            try:
                cell = sheet[cell_name]
                cell.value = value
                logger.debug(f"Set {cell_name} = {value}")
            except Exception as e:
                logger.error(f"Failed to set {cell_name}: {e}")
                raise

        # Save to output
        logger.info(f"Saving to: {output_path}")
        wb.save(output_path)
        logger.info("Template populated successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to populate template: {e}")
        return False

    finally:
        wb.close()
```

---

## Checklist

Before deploying template population code:

- [ ] All data injection uses named ranges or documented cell references
- [ ] No formulas are overwritten
- [ ] Cell formatting is preserved
- [ ] Named ranges are preserved
- [ ] Error handling is in place
- [ ] Logging is implemented
- [ ] Tests cover edge cases
- [ ] Performance is acceptable for expected data volumes
- [ ] No VBA macros are used or modified
- [ ] No inline styling overrides
- [ ] Workbook is properly closed after use
- [ ] Data types are validated before injection
- [ ] Rollback mechanism exists for errors
