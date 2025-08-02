# Hospital Management System AI Agents

This document describes the four AI agents designed for the hospital management system and their interactions with the PostgreSQL database.

## Agent Overview

### 1. Bed Management Agent
**Purpose**: Manages hospital bed allocation, availability tracking, and patient assignments.

**Key Functions**:
- `checkAvailability()`: Check available beds by type, department, or floor
- `assignBed()`: Assign beds to patients with admission tracking
- `dischargeBed()`: Discharge patients and make beds available
- `getOccupancyStats()`: Generate occupancy reports and statistics
- `predictDemand()`: Predict future bed demand based on historical data

**Database Tables Used**:
- `beds` - Primary table for bed management
- `rooms` - Room information and capacity
- `patients` - Patient information for assignments
- `departments` - Department-specific bed management

**MCP Tools Available**:
- `create_bed()` - Create new bed records
- `list_beds()` - List beds with optional status filtering
- `assign_bed_to_patient()` - Assign beds to patients
- `discharge_bed()` - Discharge patients from beds

### 2. Equipment Tracker Agent
**Purpose**: Tracks medical equipment, schedules maintenance, and monitors equipment status.

**Key Functions**:
- `trackEquipment()`: Monitor equipment location and status
- `scheduleMaintenacne()`: Schedule and track maintenance activities
- `checkAvailability()`: Check equipment availability for procedures
- `generateReports()`: Generate equipment utilization reports
- `predictFailures()`: Predict equipment failures based on usage patterns

**Database Tables Used**:
- `equipment` - Equipment inventory and status
- `equipment_categories` - Equipment classification
- `departments` - Department-specific equipment tracking

**MCP Tools Available**:
- `create_equipment_category()` - Create equipment categories
- `create_equipment()` - Add new equipment to inventory
- `list_equipment()` - List equipment with filtering options
- `update_equipment_status()` - Update equipment status and notes

### 3. Staff Allocation Agent
**Purpose**: Optimizes staff scheduling and workload distribution across departments.

**Key Functions**:
- `optimizeScheduling()`: Create optimal staff schedules
- `checkAvailability()`: Check staff availability for shifts
- `assignShifts()`: Assign staff to specific shifts and departments
- `balanceWorkload()`: Balance workload across staff members
- `predictStaffing()`: Predict staffing needs based on patient load

**Database Tables Used**:
- `staff` - Staff information and assignments
- `users` - User credentials and contact information
- `departments` - Department staffing requirements

**MCP Tools Available**:
- `create_staff()` - Add new staff members
- `list_staff()` - List staff with department/status filtering
- `update_user()` - Update staff user information

### 4. Supply Inventory Agent
**Purpose**: Manages medical supplies, tracks inventory levels, and optimizes ordering.

**Key Functions**:
- `trackInventory()`: Monitor supply levels and usage patterns
- `predictReorder()`: Predict when supplies need reordering
- `manageStock()`: Handle stock adjustments and transfers
- `generateAlerts()`: Alert when supplies are low or expired
- `optimizeOrdering()`: Optimize ordering quantities and timing

**Database Tables Used**:
- `supplies` - Supply inventory and stock levels
- `supply_categories` - Supply classification
- `inventory_transactions` - Track all inventory movements

**MCP Tools Available**:
- `create_supply_category()` - Create supply categories
- `create_supply()` - Add new supplies to inventory
- `list_supplies()` - List supplies with low stock filtering
- `update_supply_stock()` - Update stock levels with transaction logging

## Agent Interaction Logging

All agent interactions are logged in the `agent_interactions` table with the following information:
- Agent type (bed_management, equipment_tracker, staff_allocation, supply_inventory)
- User who made the query
- Query text and response
- Action taken by the agent
- Confidence score of the response
- Execution time in milliseconds

**MCP Tool**:
- `log_agent_interaction()` - Log agent interactions for analysis

## Database Schema for AI Agents

### Core Agent Tables

```sql
-- Agent interaction logging
CREATE TABLE agent_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('bed_management', 'equipment_tracker', 'staff_allocation', 'supply_inventory')),
    user_id UUID,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    action_taken VARCHAR(100),
    confidence_score DECIMAL(3, 2),
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Bed management specific indexes
CREATE INDEX idx_beds_status ON beds(status);
CREATE INDEX idx_beds_room ON beds(room_id);

-- Equipment tracking specific indexes
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_equipment_department ON equipment(department_id);
CREATE INDEX idx_equipment_maintenance ON equipment(next_maintenance);

-- Supply inventory specific indexes
CREATE INDEX idx_supplies_stock_level ON supplies(current_stock, minimum_stock_level);
CREATE INDEX idx_supplies_expiry ON supplies(expiry_date);
CREATE INDEX idx_inventory_transactions_supply ON inventory_transactions(supply_id);

-- Staff allocation specific indexes
CREATE INDEX idx_staff_department ON staff(department_id);
CREATE INDEX idx_staff_status ON staff(status);
CREATE INDEX idx_staff_shift ON staff(shift_pattern);

-- Agent interaction indexes
CREATE INDEX idx_agent_interactions_type ON agent_interactions(agent_type);
CREATE INDEX idx_agent_interactions_date ON agent_interactions(created_at);
```

## Agent Integration Points

### 1. Real-time Notifications
Agents can trigger notifications when:
- Bed occupancy reaches critical levels
- Equipment requires maintenance
- Staff scheduling conflicts arise
- Supply levels fall below minimum thresholds

### 2. Cross-Agent Communication
Agents can communicate with each other for:
- **Bed + Staff**: Ensure adequate staffing for bed assignments
- **Equipment + Supply**: Track supplies used with equipment
- **Staff + Supply**: Staff access to required supplies

### 3. Predictive Analytics
Agents use historical data for:
- Predicting peak bed demand periods
- Forecasting equipment maintenance needs
- Optimizing staff schedules based on patient flow
- Preventing supply stockouts

### 4. Performance Metrics
Key metrics tracked by each agent:
- **Bed Management**: Occupancy rates, average length of stay, turnover time
- **Equipment Tracker**: Utilization rates, maintenance compliance, downtime
- **Staff Allocation**: Staff-to-patient ratios, overtime hours, shift coverage
- **Supply Inventory**: Stock turnover, waste reduction, cost optimization

## Implementation Notes

1. **Error Handling**: All agent tools include comprehensive error handling and return structured responses
2. **Data Validation**: Input validation ensures data integrity across all operations
3. **Audit Trail**: All operations are logged with timestamps and user attribution
4. **Scalability**: Database design supports horizontal scaling for large hospital systems
5. **Security**: UUID-based primary keys and proper foreign key constraints ensure data security

## Usage Examples

### Bed Management Agent
```python
# Check available beds
beds = list_beds(status="available")

# Assign bed to patient
result = assign_bed_to_patient(
    bed_id="bed_uuid_here",
    patient_id="patient_uuid_here",
    admission_date="2024-08-15T10:30:00"
)
```

### Supply Inventory Agent
```python
# Check low stock items
low_stock = list_supplies(low_stock_only=True)

# Update stock with transaction
result = update_supply_stock(
    supply_id="supply_uuid_here",
    quantity_change=50,
    transaction_type="in",
    performed_by="user_uuid_here",
    unit_cost=1.25
)
```

This comprehensive system provides full CRUD operations for all hospital management entities while supporting advanced AI agent functionalities.
