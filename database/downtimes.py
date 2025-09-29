"""
Downtimes database operations - WITH UPDATE METHOD ADDED
Matches your actual database structure
"""

from .connection import get_db
from datetime import datetime, timedelta

class DowntimesDB:
    """Downtime entries database operations"""
    
    def __init__(self):
        self.db = get_db()
    
    def get_by_id(self, downtime_id):
        """Get downtime entry by ID"""
        with self.db.get_connection() as conn:
            query = """
                SELECT d.*, 
                       pl.line_name,
                       f.facility_name,
                       dc.category_name,
                       s.shift_name
                FROM Downtimes d
                INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                INNER JOIN Facilities f ON pl.facility_id = f.facility_id
                INNER JOIN DowntimeCategories dc ON d.category_id = dc.category_id
                LEFT JOIN Shifts s ON d.shift_id = s.shift_id
                WHERE d.downtime_id = ? AND d.is_deleted = 0
            """
            results = conn.execute_query(query, (downtime_id,))
            return results[0] if results else None
    
    def create(self, data):
        """
        Add a new downtime record
        
        Args:
            data: dict with keys:
                - line_id (required)
                - category_id (required)
                - shift_id (optional)
                - start_time (required)
                - end_time (required)
                - reason_notes (optional)
                - entered_by (required)
        
        Returns:
            tuple: (success, message, downtime_id)
        """
        with self.db.get_connection() as conn:
            # Validate required fields
            required = ['line_id', 'category_id', 'start_time', 'end_time', 'entered_by']
            for field in required:
                if field not in data or not data[field]:
                    return False, f"Missing required field: {field}", None
            
            # Calculate duration
            try:
                if isinstance(data['start_time'], str):
                    start = datetime.fromisoformat(data['start_time'])
                else:
                    start = data['start_time']
                
                if isinstance(data['end_time'], str):
                    end = datetime.fromisoformat(data['end_time'])
                else:
                    end = data['end_time']
                
                duration_minutes = int((end - start).total_seconds() / 60)
                
                if duration_minutes <= 0:
                    return False, "End time must be after start time", None
                
                if duration_minutes > 1440:  # 24 hours
                    return False, "Downtime duration cannot exceed 24 hours", None
                    
            except (ValueError, TypeError) as e:
                return False, f"Invalid datetime format: {str(e)}", None
            
            # Insert into database
            insert_query = """
                INSERT INTO Downtimes (
                    line_id, category_id, shift_id,
                    start_time, end_time, duration_minutes,
                    reason_notes, entered_by, entered_date,
                    created_by, created_date, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, GETDATE(), 0)
            """
            
            params = (
                data['line_id'],
                data['category_id'],
                data.get('shift_id'),
                start,
                end,
                duration_minutes,
                data.get('reason_notes', ''),
                data['entered_by'],
                data['entered_by']  # Also set created_by
            )
            
            success = conn.execute_query(insert_query, params)
            
            if success:
                # Get the new downtime ID
                new_downtime = conn.execute_query("""
                    SELECT TOP 1 downtime_id 
                    FROM Downtimes 
                    WHERE entered_by = ? 
                    ORDER BY downtime_id DESC
                """, (data['entered_by'],))
                
                downtime_id = new_downtime[0]['downtime_id'] if new_downtime else None
                return True, f"Downtime entry created ({duration_minutes} minutes)", downtime_id
            
            return False, "Failed to create downtime entry", None
    
    def update(self, downtime_id, data, username):
        """
        Update an existing downtime record
        
        Args:
            downtime_id: ID of the downtime entry to update
            data: dict with keys to update:
                - line_id (optional)
                - category_id (optional)
                - shift_id (optional)
                - start_time (optional)
                - end_time (optional)
                - reason_notes (optional)
            username: User making the update
        
        Returns:
            tuple: (success, message, changes)
        """
        with self.db.get_connection() as conn:
            # Get current record for comparison
            current = self.get_by_id(downtime_id)
            if not current:
                return False, "Downtime entry not found", None
            
            # Track changes for audit
            changes = {}
            
            # Build UPDATE query dynamically based on what's being updated
            update_fields = []
            params = []
            
            # Check each field for changes
            if 'line_id' in data and data['line_id'] != current['line_id']:
                update_fields.append('line_id = ?')
                params.append(data['line_id'])
                changes['line_id'] = {'old': current['line_id'], 'new': data['line_id']}
            
            if 'category_id' in data and data['category_id'] != current['category_id']:
                update_fields.append('category_id = ?')
                params.append(data['category_id'])
                changes['category_id'] = {'old': current['category_id'], 'new': data['category_id']}
            
            if 'shift_id' in data and data['shift_id'] != current.get('shift_id'):
                update_fields.append('shift_id = ?')
                params.append(data['shift_id'])
                changes['shift_id'] = {'old': current.get('shift_id'), 'new': data['shift_id']}
            
            # Handle datetime updates with recalculation of duration
            start_changed = False
            end_changed = False
            new_start = current['start_time']
            new_end = current['end_time']
            
            if 'start_time' in data:
                if isinstance(data['start_time'], str):
                    new_start = datetime.fromisoformat(data['start_time'])
                else:
                    new_start = data['start_time']
                
                if new_start != current['start_time']:
                    start_changed = True
                    update_fields.append('start_time = ?')
                    params.append(new_start)
                    changes['start_time'] = {
                        'old': current['start_time'].isoformat() if current['start_time'] else None,
                        'new': new_start.isoformat() if new_start else None
                    }
            
            if 'end_time' in data:
                if isinstance(data['end_time'], str):
                    new_end = datetime.fromisoformat(data['end_time'])
                else:
                    new_end = data['end_time']
                
                if new_end != current['end_time']:
                    end_changed = True
                    update_fields.append('end_time = ?')
                    params.append(new_end)
                    changes['end_time'] = {
                        'old': current['end_time'].isoformat() if current['end_time'] else None,
                        'new': new_end.isoformat() if new_end else None
                    }
            
            # Recalculate duration if times changed
            if start_changed or end_changed:
                duration_minutes = int((new_end - new_start).total_seconds() / 60)
                
                if duration_minutes <= 0:
                    return False, "End time must be after start time", None
                
                if duration_minutes > 1440:  # 24 hours
                    return False, "Downtime duration cannot exceed 24 hours", None
                
                update_fields.append('duration_minutes = ?')
                params.append(duration_minutes)
                changes['duration_minutes'] = {
                    'old': current['duration_minutes'],
                    'new': duration_minutes
                }
            
            if 'reason_notes' in data:
                old_notes = current.get('reason_notes', '')
                new_notes = data.get('reason_notes', '')
                if old_notes != new_notes:
                    update_fields.append('reason_notes = ?')
                    params.append(new_notes)
                    changes['reason_notes'] = {'old': old_notes, 'new': new_notes}
            
            # Only update if there are changes
            if not changes:
                return True, "No changes detected", None
            
            # Add modified_by and modified_date
            update_fields.extend(['modified_by = ?', 'modified_date = GETDATE()'])
            params.append(username)
            
            # Add the ID parameter at the end
            params.append(downtime_id)
            
            # Execute update
            update_query = f"""
                UPDATE Downtimes 
                SET {', '.join(update_fields)}
                WHERE downtime_id = ? AND is_deleted = 0
            """
            
            success = conn.execute_query(update_query, params)
            
            if success:
                return True, "Downtime entry updated successfully", changes
            
            return False, "Failed to update downtime entry", None
    
    def get_recent(self, days=7, line_id=None, limit=100):
        """Get recent downtime entries with facility information through line"""
        with self.db.get_connection() as conn:
            # Join with ProductionLines to get facility information
            base_query = f"""
                SELECT TOP {limit}
                    d.downtime_id,
                    d.line_id,
                    d.category_id,
                    d.start_time,
                    d.end_time,
                    d.duration_minutes,
                    d.reason_notes,
                    d.entered_by,
                    d.entered_date,
                    d.shift_id,
                    pl.facility_id,
                    pl.line_name,
                    f.facility_name,
                    dc.category_name,
                    dc.category_code,
                    s.shift_name
                FROM Downtimes d
                INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                INNER JOIN Facilities f ON pl.facility_id = f.facility_id
                INNER JOIN DowntimeCategories dc ON d.category_id = dc.category_id
                LEFT JOIN Shifts s ON d.shift_id = s.shift_id
                WHERE d.start_time >= DATEADD(day, ?, GETDATE())
                AND d.is_deleted = 0
            """
            
            params = [-days]
            
            if line_id:
                base_query += " AND d.line_id = ?"
                params.append(line_id)
            
            base_query += " ORDER BY d.start_time DESC"
            
            results = conn.execute_query(base_query, params)
            
            # Normalize the results to include facility_id
            normalized = []
            for row in results if results else []:
                row['notes'] = row.get('reason_notes', '')  # Map reason_notes to notes for compatibility
                normalized.append(row)
            
            return normalized
    
    def get_by_facility(self, facility_id, days=7, limit=100):
        """Get downtime entries for a specific facility"""
        with self.db.get_connection() as conn:
            query = f"""
                SELECT TOP {limit}
                    d.downtime_id,
                    d.line_id,
                    d.category_id,
                    d.start_time,
                    d.end_time,
                    d.duration_minutes,
                    d.reason_notes,
                    d.entered_by,
                    d.entered_date,
                    pl.facility_id,
                    pl.line_name,
                    f.facility_name,
                    dc.category_name
                FROM Downtimes d
                INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                INNER JOIN Facilities f ON pl.facility_id = f.facility_id
                INNER JOIN DowntimeCategories dc ON d.category_id = dc.category_id
                WHERE pl.facility_id = ?
                AND d.start_time >= DATEADD(day, ?, GETDATE())
                AND d.is_deleted = 0
                ORDER BY d.start_time DESC
            """
            
            results = conn.execute_query(query, (facility_id, -days))
            
            # Normalize
            normalized = []
            for row in results if results else []:
                row['notes'] = row.get('reason_notes', '')
                normalized.append(row)
            
            return normalized
    
    def get_by_date_range(self, start_date, end_date, facility_id=None, line_id=None):
        """Get downtime entries within a date range"""
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    d.*,
                    pl.facility_id,
                    pl.line_name,
                    f.facility_name,
                    dc.category_name
                FROM Downtimes d
                INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                INNER JOIN Facilities f ON pl.facility_id = f.facility_id
                INNER JOIN DowntimeCategories dc ON d.category_id = dc.category_id
                WHERE d.start_time >= ? 
                AND d.end_time <= ?
                AND d.is_deleted = 0
            """
            
            params = [start_date, end_date]
            
            if facility_id:
                query += " AND pl.facility_id = ?"
                params.append(facility_id)
            
            if line_id:
                query += " AND d.line_id = ?"
                params.append(line_id)
            
            query += " ORDER BY d.start_time DESC"
            
            results = conn.execute_query(query, params)
            
            # Normalize
            normalized = []
            for row in results if results else []:
                row['notes'] = row.get('reason_notes', '')
                normalized.append(row)
            
            return normalized
    
    def get_summary(self, start_date, end_date, group_by='category'):
        """
        Get downtime summary statistics
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            group_by: 'category', 'facility', 'line', or 'shift'
        
        Returns:
            list: Summary statistics grouped by specified field
        """
        with self.db.get_connection() as conn:
            params = [start_date, end_date]
            
            if group_by == 'category':
                query = """
                    SELECT 
                        dc.category_name as grouping,
                        COUNT(*) as event_count,
                        SUM(d.duration_minutes) as total_minutes,
                        AVG(d.duration_minutes) as avg_minutes,
                        MIN(d.duration_minutes) as min_minutes,
                        MAX(d.duration_minutes) as max_minutes
                    FROM Downtimes d
                    INNER JOIN DowntimeCategories dc ON d.category_id = dc.category_id
                    WHERE d.start_time >= ? AND d.end_time <= ?
                    AND d.is_deleted = 0
                    GROUP BY dc.category_name
                    ORDER BY total_minutes DESC
                """
            elif group_by == 'facility':
                query = """
                    SELECT 
                        f.facility_name as grouping,
                        COUNT(*) as event_count,
                        SUM(d.duration_minutes) as total_minutes,
                        AVG(d.duration_minutes) as avg_minutes,
                        MIN(d.duration_minutes) as min_minutes,
                        MAX(d.duration_minutes) as max_minutes
                    FROM Downtimes d
                    INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                    INNER JOIN Facilities f ON pl.facility_id = f.facility_id
                    WHERE d.start_time >= ? AND d.end_time <= ?
                    AND d.is_deleted = 0
                    GROUP BY f.facility_name
                    ORDER BY total_minutes DESC
                """
            elif group_by == 'line':
                query = """
                    SELECT 
                        pl.line_name as grouping,
                        f.facility_name,
                        COUNT(*) as event_count,
                        SUM(d.duration_minutes) as total_minutes,
                        AVG(d.duration_minutes) as avg_minutes,
                        MIN(d.duration_minutes) as min_minutes,
                        MAX(d.duration_minutes) as max_minutes
                    FROM Downtimes d
                    INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                    INNER JOIN Facilities f ON pl.facility_id = f.facility_id
                    WHERE d.start_time >= ? AND d.end_time <= ?
                    AND d.is_deleted = 0
                    GROUP BY pl.line_name, f.facility_name
                    ORDER BY total_minutes DESC
                """
            else:
                # Default to category
                return self.get_summary(start_date, end_date, 'category')
            
            return conn.execute_query(query, params)
    
    def get_top_issues(self, days=30, limit=10):
        """Get top downtime issues by frequency and duration"""
        with self.db.get_connection() as conn:
            # Top by frequency
            frequency_query = f"""
                SELECT TOP {limit}
                    dc.category_name,
                    COUNT(*) as occurrence_count,
                    SUM(d.duration_minutes) as total_minutes
                FROM Downtimes d
                INNER JOIN DowntimeCategories dc ON d.category_id = dc.category_id
                WHERE d.start_time >= DATEADD(day, ?, GETDATE())
                AND d.is_deleted = 0
                GROUP BY dc.category_name
                ORDER BY occurrence_count DESC
            """
            
            # Top by duration
            duration_query = f"""
                SELECT TOP {limit}
                    dc.category_name,
                    COUNT(*) as occurrence_count,
                    SUM(d.duration_minutes) as total_minutes
                FROM Downtimes d
                INNER JOIN DowntimeCategories dc ON d.category_id = dc.category_id
                WHERE d.start_time >= DATEADD(day, ?, GETDATE())
                AND d.is_deleted = 0
                GROUP BY dc.category_name
                ORDER BY total_minutes DESC
            """
            
            return {
                'by_frequency': conn.execute_query(frequency_query, (-days,)),
                'by_duration': conn.execute_query(duration_query, (-days,))
            }
    
    def delete(self, downtime_id, username):
        """Soft delete a downtime entry"""
        with self.db.get_connection() as conn:
            # Soft delete
            query = """
                UPDATE Downtimes 
                SET is_deleted = 1, modified_by = ?, modified_date = GETDATE()
                WHERE downtime_id = ?
            """
            
            success = conn.execute_query(query, (username, downtime_id))
            return success, "Downtime entry deleted" if success else "Failed to delete entry"
    
    def restore(self, downtime_id, username):
        """Restore a deleted downtime entry"""
        with self.db.get_connection() as conn:
            # Restore deleted entry
            query = """
                UPDATE Downtimes 
                SET is_deleted = 0, modified_by = ?, modified_date = GETDATE()
                WHERE downtime_id = ?
            """
            
            success = conn.execute_query(query, (username, downtime_id))
            return success, "Downtime entry restored" if success else "Failed to restore entry"
    
    def get_statistics(self, facility_id=None, days=30):
        """Get downtime statistics for dashboard"""
        with self.db.get_connection() as conn:
            params = [-days]
            
            # Build WHERE clause
            where_clause = """
                WHERE d.start_time >= DATEADD(day, ?, GETDATE())
                AND d.is_deleted = 0
            """
            
            if facility_id:
                where_clause += " AND pl.facility_id = ?"
                params.append(facility_id)
            
            # Total downtime
            total_query = f"""
                SELECT 
                    COUNT(*) as total_events,
                    ISNULL(SUM(d.duration_minutes), 0) as total_minutes,
                    ISNULL(AVG(d.duration_minutes), 0) as avg_minutes
                FROM Downtimes d
                INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                {where_clause}
            """
            
            totals = conn.execute_query(total_query, params)
            
            # Daily average
            daily_query = f"""
                SELECT 
                    CAST(d.start_time as DATE) as downtime_date,
                    COUNT(*) as events,
                    SUM(d.duration_minutes) as minutes
                FROM Downtimes d
                INNER JOIN ProductionLines pl ON d.line_id = pl.line_id
                {where_clause}
                GROUP BY CAST(d.start_time as DATE)
            """
            
            daily_data = conn.execute_query(daily_query, params)
            
            return {
                'total_events': totals[0]['total_events'] if totals else 0,
                'total_minutes': totals[0]['total_minutes'] if totals else 0,
                'avg_minutes': totals[0]['avg_minutes'] if totals else 0,
                'daily_data': daily_data
            }